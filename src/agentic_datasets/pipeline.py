from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Iterator, List

from .config import PipelineConfig
from .schemas.messages import ConversationRecord


def _iter_jsonl(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def ingest(input_path: Path) -> Iterator[dict]:
    if input_path.is_dir():
        for p in sorted(input_path.glob("*.jsonl")):
            yield from _iter_jsonl(p)
    else:
        yield from _iter_jsonl(input_path)


def normalize(records: Iterable[dict]) -> Iterator[ConversationRecord]:
    for r in records:
        yield ConversationRecord.model_validate(r)


def validate(records: Iterable[ConversationRecord]) -> List[ConversationRecord]:
    out: List[ConversationRecord] = []
    for rec in records:
        out.append(rec)
    return out


def export(records: Iterable[ConversationRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec.model_dump(), ensure_ascii=False) + "\n")


def run_pipeline(cfg: PipelineConfig) -> Path:
    raw = ingest(cfg.input_path)
    norm = normalize(raw)
    validated = validate(norm)
    if cfg.max_records is not None:
        items = []
        for i, rec in enumerate(validated):
            if i >= cfg.max_records:
                break
            items.append(rec)
    else:
        items = list(validated)
    export(items, cfg.output_path)
    return cfg.output_path
