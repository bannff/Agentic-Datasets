from pathlib import Path

from agentic_datasets.catalog import load_catalog, make_dataset_card


def test_load_catalog(tmp_path: Path):
    cfg = tmp_path / "catalog.yaml"
    cfg.write_text(
        """
entries:
  - id: demo
    name: Demo Dataset
    version: 1.0.0
    description: Test
    license: mit
    tags: [demo]
    local_path: data/demo.jsonl
""".strip()
    )
    cat = load_catalog(cfg)
    e = cat.get("demo")
    assert e.name == "Demo Dataset"
    card = make_dataset_card(e)
    assert "Demo Dataset" in card
