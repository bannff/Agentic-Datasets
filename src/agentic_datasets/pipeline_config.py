from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

import yaml
from pydantic import BaseModel, Field

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
    stages: List[StageConfig] = Field(default_factory=list)


def load_spec(path: Path) -> PipelineSpec:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return PipelineSpec.model_validate(data)


def run_spec(spec: PipelineSpec) -> Path:
    records: Iterator[Dict[str, Any]] = ingest(spec.input)
    stream: Iterator[ConversationRecord] = normalize(records)
    # Orchestrate stages
    if spec.orchestrator == "strands":
        from .orchestrators.strands import run_strands_pipeline

        stream = run_strands_pipeline(
            [s.model_dump() for s in spec.stages], stream
        )
    else:
        # Local in-process registry
        for st in spec.stages:
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
