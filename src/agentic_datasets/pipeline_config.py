from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

import yaml
from pydantic import BaseModel, Field, field_validator

from .pipeline import ingest, normalize, export
from .registry import registry
from .schemas.messages import ConversationRecord


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
    stages: List[Union[StageConfig, Dict[str, Any]]] = Field(default_factory=list)

    @field_validator("stages", mode="before")
    @classmethod
    def _coerce_stages(cls, v: Any) -> Any:
        # Allow list of dicts in YAML to become List[StageConfig]
        if isinstance(v, list) and v and isinstance(v[0], dict):
            return [StageConfig.model_validate(i) for i in v]
        return v


def load_spec(path: Path) -> PipelineSpec:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return PipelineSpec.model_validate(data)


def run_spec(spec: PipelineSpec) -> Path:
    records: Iterator[Dict[str, Any]] = ingest(spec.input)
    stream: Iterator[ConversationRecord] = normalize(records)
    # Normalize stages to StageConfig for static typing downstream
    stages: List[StageConfig] = [s if isinstance(s, StageConfig) else StageConfig.model_validate(s) for s in spec.stages]
    # Orchestrate stages
    if spec.orchestrator == "strands":
        from .orchestrators.strands import run_strands_pipeline

        stream = run_strands_pipeline([s.model_dump() for s in stages], stream)
    else:
        # Local in-process registry
        for st in stages:
            transform = registry.get(st.name)
            stream = transform(stream, **st.params)
    # Truncate if needed
    if spec.max_records is not None:
        items: List[ConversationRecord] = []
        for i, rec in enumerate(stream):
            if i >= spec.max_records:
                break
            items.append(rec)
        export(items, spec.output)
    else:
        export(stream, spec.output)
    return spec.output
