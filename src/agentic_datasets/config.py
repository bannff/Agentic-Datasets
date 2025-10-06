from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PipelineConfig(BaseModel):
    input_path: Path = Field(
        ..., description="Path to input JSONL or directory of JSONL files"
    )
    output_path: Path = Field(..., description="Where to write processed dataset JSONL")
    max_records: Optional[int] = Field(
        None, description="Optional cap for records during debug runs"
    )

    @field_validator("input_path", "output_path", mode="before")
    @classmethod
    def _expand_path(cls, v: str | Path) -> Path:
        return Path(v).expanduser().resolve()
