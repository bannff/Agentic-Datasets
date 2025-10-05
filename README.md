# Agentic Datasets

Config-driven pipelines for building agentic, multi-turn datasets with chunking, validation, optional tool-call execution, and Hugging Face publishing. Includes CLI, tests, CI, Docker image, and Codespaces devcontainer.

## Quickstart

1. Create and activate a virtual environment
2. Install in editable mode:
   - pip install -e .[dev]

CLI commands:
- agentic-datasets run: Ingest → normalize → validate → export
- agentic-datasets chunk: Token-aware chunking
- agentic-datasets run-config: Run a YAML pipeline spec
- agentic-datasets transforms: List registered transforms
- agentic-datasets catalog:list/show: Inspect dataset catalog
- agentic-datasets hf:push: Push JSONL to Hugging Face with dataset card

Examples:
- agentic-datasets run-config examples/pipeline.example.yaml
- agentic-datasets run-config examples/pipeline.agentic.yaml

## CI/CD

- Lint/Tests: .github/workflows/ci.yml
- Devcontainer build + tests: .github/workflows/devcontainer-ci.yml
- Smoke (Docker image): .github/workflows/smoke.yml
- Docker build/push to GHCR: .github/workflows/docker.yml
- Publish to Hugging Face (manual): .github/workflows/publish_hf.yml

Repo secret required for publish: HUGGINGFACE_HUB_TOKEN

## Codespaces

Devcontainer is included (.devcontainer/devcontainer.json). Open in Codespaces to get a ready-to-run environment.

## Notes

- See `README_AGENTIC.md` for a brief CLI reference.
- Legacy/large directories are archived; see `docs/LEGACY.md`.
