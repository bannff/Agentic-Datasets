from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Callable, cast
import logging

import yaml
from pydantic import BaseModel, Field, field_validator

from .pipeline import ingest, normalize, export  # type: ignore[import-untyped]
from .registry import registry
from .schemas.messages import ConversationRecord

# Type aliases for clarity
IngestFunc = Callable[[Path], Iterator[Dict[str, Any]]]
NormalizeFunc = Callable[[Any], Iterator[ConversationRecord]]  # Accepts Iterable[dict]

logger = logging.getLogger(__name__)


class LLMProviderConfig(BaseModel):
    """Unified LLM provider configuration.
    
    Model format follows LiteLLM convention: "provider/model_name"
    Examples:
        - "ollama/qwen3:8b" (local Ollama - default)
        - "openai/gpt-4o" (OpenAI)
        - "anthropic/claude-4-sonnet-20250514" (Anthropic)
        - "bedrock/anthropic.claude-v2" (AWS Bedrock)
    
    Set via:
        - YAML config: llm.model, llm.temperature, etc.
        - Environment: AGENTIC_LLM_MODEL, AGENTIC_LLM_TEMPERATURE
    """
    model: str = Field(
        default_factory=lambda: os.getenv("AGENTIC_LLM_MODEL", "ollama/qwen3:8b")
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("AGENTIC_LLM_TEMPERATURE", "0.7"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("AGENTIC_LLM_MAX_TOKENS", "4096"))
    )
    api_base: Optional[str] = Field(
        default_factory=lambda: os.getenv("OLLAMA_HOST")
    )


class StageConfig(BaseModel):
    name: str = Field(..., description="Transform name from registry")
    params: Dict[str, Any] = Field(default_factory=dict)


class PipelineSpec(BaseModel):
    input: Path
    output: Path
    max_records: Optional[int] = None
    orchestrator: Optional[str] = Field(
        default=None, description="Optional orchestrator backend: 'strands' or None for local"
    )
    llm: Optional[LLMProviderConfig] = Field(
        default=None, description="Unified LLM provider configuration for all stages"
    )
    stages: List[StageConfig] = Field(default_factory=list)  # type: ignore[assignment]

    @field_validator("stages", mode="before")
    @classmethod
    def _coerce_stages(cls, v: Any) -> list[StageConfig]:  # type: ignore[name-defined]
        # Allow list of dicts in YAML to become List[StageConfig]
        if isinstance(v, list) and v and isinstance(v[0], dict):
            return [StageConfig.model_validate(stage_dict) for stage_dict in (v or [])]  # type: ignore
        return cast(list[StageConfig], v if isinstance(v, list) else [])  # type: ignore


def load_spec(path: Path) -> PipelineSpec:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return PipelineSpec.model_validate(data)


def run_spec(spec: PipelineSpec) -> Path:
    """Run pipeline stages, saving intermediate outputs to audit trail.
    
    Args:
        spec: PipelineSpec with input, output, and stages
        
    Returns:
        Path to final output file
    """
    # Configure global LLM provider if specified
    if spec.llm:
        from .llm import LLMConfig, set_default_config
        llm_config = LLMConfig(
            model=spec.llm.model,
            temperature=spec.llm.temperature,
            max_tokens=spec.llm.max_tokens,
            api_base=spec.llm.api_base,
        )
        set_default_config(llm_config)
        logger.info(f"LLM provider configured: {spec.llm.model}")
    
    # Create stage outputs directory
    output_dir = Path(spec.output).parent
    stages_audit_dir = output_dir / ".pipeline_stages"
    stages_audit_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Pipeline audit trail: {stages_audit_dir}")
    
    # Load and normalize input
    records: Iterator[Dict[str, Any]] = ingest(spec.input)  # type: ignore[assignment]
    stream: Iterator[ConversationRecord] = normalize(records)  # type: ignore[arg-type]
    
    # Ensure stages are properly typed
    stages: List[StageConfig] = spec.stages  # type: ignore
    
    # Process through stages with intermediate checkpoints
    if spec.orchestrator == "strands":
        from .orchestrators.strands import run_strands_pipeline

        stream = run_strands_pipeline([s.model_dump() for s in stages], stream)
    else:
        # Local in-process registry with intermediate outputs
        for stage_idx, st in enumerate(stages, 1):
            transform = registry.get(st.name)
            stream = transform(stream, **st.params)
            
            # Save intermediate output (create new list from stream to avoid consuming iterator)
            stage_output_path = stages_audit_dir / f"{stage_idx:02d}_{st.name}.jsonl"
            items: List[ConversationRecord] = []
            for rec in stream:  # type: ignore
                items.append(rec)
                
            # Export intermediate checkpoint
            export(items, stage_output_path)
            logger.info(f"Stage {stage_idx} ({st.name}): {len(items)} records → {stage_output_path}")
            
            # Convert back to iterator for next stage (or final output)
            stream = iter(items)
    
    # Truncate if needed and save final output
    if spec.max_records is not None:
        items_final: List[ConversationRecord] = []
        for i, rec in enumerate(stream):
            if i >= spec.max_records:
                break
            items_final.append(rec)
        export(items_final, spec.output)
        logger.info(f"Final output (truncated to {spec.max_records}): {spec.output}")
    else:
        # Stream has been fully consumed in stages above, items holds final data
        if not isinstance(stream, list):
            items_final = list(stream)
        else:
            items_final = stream  # type: ignore
        export(items_final, spec.output)
        logger.info(f"Final output: {len(items_final)} records → {spec.output}")
    
    return spec.output
