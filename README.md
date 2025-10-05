# Agentic Datasets

![CI](https://github.com/bannff/datasets/actions/workflows/ci.yml/badge.svg)
![Smoke](https://github.com/bannff/datasets/actions/workflows/smoke.yml/badge.svg)
![Docker](https://github.com/bannff/datasets/actions/workflows/docker.yml/badge.svg)
![Run Pipeline](https://github.com/bannff/datasets/actions/workflows/run_pipeline.yml/badge.svg)

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
- Publish to Hugging Face on tag: .github/workflows/publish_hf_on_tag.yml
 - Run pipeline on-demand (cloud): .github/workflows/run_pipeline.yml

Repo secret required for publish: HUGGINGFACE_HUB_TOKEN

Auto-publish on tag (optional):
- Add repository Variables: PUBLISH_ENTRY_ID (catalog entry id), PUBLISH_REPO_ID (e.g., your-org/your-dataset), PUBLISH_DATA_PATH (path to JSONL to publish)
- Push a tag named dataset-<anything> (e.g., dataset-2025-10-05)
- The workflow will run and call: agentic-datasets hf:push "$PUBLISH_ENTRY_ID" "$PUBLISH_REPO_ID" "$PUBLISH_DATA_PATH"

## Codespaces

Devcontainer is included (.devcontainer/devcontainer.json). Open in Codespaces to get a ready-to-run environment.

## Notes
## Cloud-first: run pipelines in Actions

You can execute pipelines without Docker or local Python by triggering the on-demand workflow:

1. Go to GitHub → Actions → "Run Agentic Pipeline (on-demand)"
2. Click "Run workflow" and provide a YAML config path (default: examples/pipeline.example.yaml)
3. The job installs dependencies, runs the pipeline, and uploads any out*.jsonl files as artifacts

For publishing to HF, use the manual workflow (publish_hf.yml) or tag-triggered one (publish_hf_on_tag.yml).

- See `README_AGENTIC.md` for a brief CLI reference.
- Legacy/large directories are archived; see `docs/LEGACY.md`.
