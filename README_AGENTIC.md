# Agentic Datasets Quickstart

This repo now includes a modular, config-driven pipeline for building agentic, multi-turn datasets.

## Install (editable)

1. Create/activate a virtualenv
2. Install the package in editable mode with extras

## CLI Overview

- agentic-datasets run: Ingest -> normalize -> validate -> export
- agentic-datasets chunk: Token-aware chunking of a JSONL dataset
- agentic-datasets run-config: Run a YAML pipeline spec with registered transforms
- agentic-datasets transforms: List available transforms
- agentic-datasets catalog:list, catalog:show: Inspect dataset catalog
- agentic-datasets hf:push: Push a JSONL dataset to Hugging Face with dataset card from catalog

## Examples

- List transforms
  agentic-datasets transforms

- Run sample YAML pipeline
  agentic-datasets run-config examples/pipeline.example.yaml

- List catalog entries
  agentic-datasets catalog:list catalog.yaml

- Push to Hugging Face
  agentic-datasets hf:push sample-conversations your-org/sample-conversations examples/sample.jsonl --catalog catalog.yaml --private

Notes
- Set HF token: huggingface-cli login
- CI runs lint/type-check/tests on PRs; release workflow publishes to PyPI on tags (requires PYPI_API_TOKEN secret)