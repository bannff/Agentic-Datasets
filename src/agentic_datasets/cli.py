from __future__ import annotations

from pathlib import Path
from typing import Optional, Any

import typer

from .config import PipelineConfig
from .pipeline import run_pipeline
from .pipeline import ingest, normalize, export
from .metrics import summarize_metrics
from .transforms.chunking import chunk_dataset
from .register_defaults import register_defaults
from .catalog import load_catalog
from .hf_export import push_jsonl
from .pipeline_config import load_spec, run_spec
from .registry import registry
import os
import json

app = typer.Typer(help="Agentic datasets pipeline CLI")
register_defaults()


@app.command()
def run(
    input_path: Path = typer.Argument(..., help="Input JSONL file or directory of JSONL files"),
    output_path: Path = typer.Argument(..., help="Output JSONL file"),
    max_records: Optional[int] = typer.Option(None, help="Limit number of records (debug)"),
) -> None:
    cfg = PipelineConfig(input_path=input_path, output_path=output_path, max_records=max_records)
    out = run_pipeline(cfg)
    typer.echo(f"Wrote: {out}")


@app.command()
def validate(
    input_path: Path = typer.Argument(..., help="Input JSONL file or directory of JSONL files"),
    max_records: Optional[int] = typer.Option(10, help="Validate N records (default: 10)"),
) -> None:
    # Reuse pipeline's initial steps to validate structure by attempting normalization only
    cfg = PipelineConfig(
        input_path=input_path, output_path=Path("/dev/null"), max_records=max_records
    )
    count = 0
    for rec in normalize(ingest(cfg.input_path)):
        count += 1
        if max_records is not None and count >= max_records:
            break
    typer.echo(f"Validated {count} records successfully")


@app.command()
def chunk(
    input_path: Path = typer.Argument(..., help="Input JSONL file or directory of JSONL files"),
    output_path: Path = typer.Argument(..., help="Output JSONL file"),
    model_name: str = typer.Option("gpt-4o-mini", help="Model encoding name for tokenization"),
    max_tokens: int = typer.Option(512, help="Max tokens per chunk"),
    overlap: int = typer.Option(50, help="Token overlap between chunks"),
) -> None:
    cfg = PipelineConfig(input_path=input_path, output_path=output_path, max_records=None)
    recs = normalize(ingest(cfg.input_path))
    chunked = chunk_dataset(recs, model_name=model_name, max_tokens=max_tokens, overlap=overlap)
    export(chunked, cfg.output_path)
    typer.echo(f"Chunked output written to: {cfg.output_path}")


@app.command()
def run_config(
    config_path: Path = typer.Argument(..., help="YAML pipeline config file"),
) -> None:
    spec = load_spec(config_path)
    # run_spec handles max_records inside spec
    out = run_spec(spec)
    typer.echo(f"Pipeline completed: {out}")


@app.command()
def transforms() -> None:
    names = sorted(registry.list().keys())
    for n in names:
        typer.echo(n)


@app.command()
def metrics(
    data: Path = typer.Argument(..., help="Path to a JSONL output to summarize"),
    limit: Optional[int] = typer.Option(None, help="Limit number of records for quick summary"),
) -> None:
    """Summarize tool_calls, tool messages, backends, and via flags from a JSONL file."""
    res = summarize_metrics(data, limit=limit)
    typer.echo(res)


@app.command()
def doctor() -> None:
    """Check environment for LLM/Strands/Ollama/tools readiness."""
    report: dict[str, dict[str, Any]] = {
        "python": {
            "version": f"{typer.__version__}",
        },
        "env": {
            "AGENTIC_LLM_MODEL": os.getenv(
                "AGENTIC_LLM_MODEL", "<unset, default: ollama/qwen3:8b>"
            ),
            "AGENTIC_LLM_TEMPERATURE": os.getenv(
                "AGENTIC_LLM_TEMPERATURE", "<unset, default: 0.7>"
            ),
            "OLLAMA_HOST": os.getenv("OLLAMA_HOST", "<unset, default: http://localhost:11434>"),
            "AGENTIC_TOOLS_BACKENDS": os.getenv("AGENTIC_TOOLS_BACKENDS", "<unset>"),
        },
        "llm": {},
        "imports": {},
        "tools_resolution": {},
    }

    # Check LiteLLM and LLM provider
    try:
        report["imports"]["litellm"] = True

        # Try to validate the configured provider
        try:
            from .llm import validate_provider, get_default_config

            cfg = get_default_config()
            report["llm"]["configured_model"] = cfg.model
            result = validate_provider()
            report["llm"]["provider_ok"] = result.get("ok", False)
            if not result.get("ok"):
                report["llm"]["error"] = result.get("error", "Unknown error")
        except Exception as e:
            report["llm"]["provider_ok"] = False
            report["llm"]["error"] = str(e)
    except Exception as e:
        report["imports"]["litellm"] = f"Error: {e}"
        report["llm"]["error"] = "LiteLLM not installed"

    # Check Strands imports
    try:
        report["imports"]["strands"] = True
    except Exception as e:
        report["imports"]["strands"] = f"Error: {e}"
    try:
        report["imports"]["strands.models.ollama"] = True
    except Exception as e:
        report["imports"]["strands.models.ollama"] = f"Error: {e}"

    # Tools backends order
    backends = [
        b.strip()
        for b in os.getenv("AGENTIC_TOOLS_BACKENDS", "strands,local").split(",")
        if b.strip()
    ]
    report["tools_resolution"]["backend_order"] = backends

    # Try resolving a couple known tools by name
    try:
        report["tools_resolution"]["local_tools"] = True
    except Exception as e:
        report["tools_resolution"]["local_tools"] = f"Error: {e}"
    try:
        import importlib

        st = importlib.import_module("strands_tools")
        hasattr(st, "search_cve")
        report["tools_resolution"]["strands_tools"] = True
    except Exception as e:
        report["tools_resolution"]["strands_tools"] = f"Error: {e}"

    typer.echo(json.dumps(report, indent=2))


@app.command("catalog:list")
def catalog_list(
    catalog: str = typer.Argument("catalog.yaml", help="Path to catalog YAML"),
) -> None:
    """List catalog entries."""
    cat = load_catalog(Path(catalog))
    for e in cat.entries:
        typer.echo(f"{e.id}\t{e.name}\t{e.version}")


@app.command("catalog:show")
def catalog_show(entry_id: str, catalog: str = typer.Argument("catalog.yaml")) -> None:
    """Show a catalog entry details."""
    cat = load_catalog(Path(catalog))
    e = cat.get(entry_id)
    typer.echo(e.model_dump_json(indent=2))


@app.command("hf:push")
def hf_push(
    entry_id: str,
    repo_id: str,
    data: str = typer.Argument(..., help="Path to JSONL to push"),
    catalog: str = typer.Option("catalog.yaml", help="Path to catalog YAML"),
    private: bool = typer.Option(False, help="Create private repo"),
) -> None:
    """Push a dataset JSONL file to Hugging Face Hub, with dataset card from catalog."""
    from .catalog import make_dataset_card, load_catalog

    cat = load_catalog(Path(catalog))
    entry = cat.get(entry_id)
    card = make_dataset_card(entry)
    push_jsonl(repo_id=repo_id, path=Path(data), dataset_card=card, private=private)
    typer.echo(f"Pushed {data} to hf://datasets/{repo_id}")


if __name__ == "__main__":
    app()
