from __future__ import annotations

from pathlib import Path

from agentic_datasets.pipeline_config import PipelineSpec, run_spec, StageConfig
from agentic_datasets.register_defaults import register_defaults


def test_run_spec_with_chunker(tmp_path: Path) -> None:
    register_defaults()

    # Prepare input
    input_path = tmp_path / "in.jsonl"
    input_path.write_text(
        "\n".join(
            ['{"messages":[{"role":"user","content":"Hello"},{"role":"assistant","content":"Hi"}]}']
            + ['{"messages":[{"role":"user","content":"%s"}]}' % ("hello " * 300)]
        ),
        encoding="utf-8",
    )

    out_path = tmp_path / "out.jsonl"

    spec = PipelineSpec(
        input=input_path,
        output=out_path,
        max_records=None,
        stages=[
            StageConfig(
                name="chunk",
                params={"model_name": "gpt-4o-mini", "max_tokens": 200, "overlap": 20},
            )
        ],
    )
    out = run_spec(spec)
    assert out == out_path
    assert out_path.exists()
    lines = out_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 2
