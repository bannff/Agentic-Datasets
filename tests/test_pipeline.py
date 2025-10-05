from __future__ import annotations

import json
from pathlib import Path

from agentic_datasets.config import PipelineConfig
from agentic_datasets.pipeline import run_pipeline


def write_sample_jsonl(path: Path, n: int = 3) -> None:
    msgs = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello"},
        {"role": "user", "content": "Tell me about X"},
        {"role": "assistant", "content": "Sure"},
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for i in range(n):
            rec = {"id": f"ex-{i}", "messages": msgs}
            f.write(json.dumps(rec) + "\n")


def test_run_pipeline_tmp(tmp_path: Path) -> None:
    input_path = tmp_path / "in.jsonl"
    output_path = tmp_path / "out.jsonl"
    write_sample_jsonl(input_path, n=5)

    cfg = PipelineConfig(input_path=input_path, output_path=output_path, max_records=4)
    out = run_pipeline(cfg)

    assert out == output_path
    assert output_path.exists()
    lines = output_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 4
    # Ensure roundtrip JSONL
    for line in lines:
        obj = json.loads(line)
        assert "messages" in obj and isinstance(obj["messages"], list)
