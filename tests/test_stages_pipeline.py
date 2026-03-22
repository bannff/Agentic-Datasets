from pathlib import Path

from agentic_datasets.pipeline_config import load_spec, run_spec
from agentic_datasets.register_defaults import register_defaults


def test_agentic_pipeline_yaml(tmp_path: Path):
    register_defaults()
    # Copy sample files to tmp to avoid writing into repo
    sample = Path("examples/sample.jsonl")
    cfg = tmp_path / "pipeline.agentic.yaml"
    cfg.write_text(
        f"""
input: {sample}
output: {tmp_path / "out.jsonl"}
orchestrator: strands
stages:
  - name: agentinstruct
  - name: s2m
  - name: apigenmt
  - name: reviewinstruct
""".strip()
    )
    spec = load_spec(cfg)
    out = run_spec(spec)
    assert Path(out).exists()
