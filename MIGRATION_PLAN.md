### Orchestration Choice (Now vs Later)
- Now: Strands-SDK (graph) — our pipeline is a linear/DAG flow (S2M → APIGenMT → ReviewInstruct), so graph orchestration is the right fit. We'll extend to swarm later for multi-agent reviews if needed.
- Use strands-tools to expose required capabilities for agents (file IO, HTTP, logging) in a controlled way.
- Fallback Later: LangChain RunnableGraph for local experimentation.
 - Add Strands graph orchestrator path for production runs
 - Add strands orchestrator example config and usage docs
 - CI builds and publishes container images to GHCR on tags and main
  - Container images: Build and push via GitHub Actions to GHCR (ghcr.io/<org>/<name>)
  - Legacy directories: `PyScience/`, `cybersecurity_datasets/`, `cybersecurity_finetuned_models/` are deprecated. They are .gitignored and will be archived or migrated to separate repos. No new code should reference them.
# Migration Plan: Agentic Multi‑Turn Datasets Refactor

Date: 2025-10-05
Owner: datasets maintainers

## Purpose
Refactor this repository into a reusable, showcase‑ready project that:
- Builds agentic, multi‑turn datasets from existing inputs via a configurable pipeline
- Publishes polished datasets in a referenceable way (e.g., Hugging Face Hub)
- Adheres to Beast Mode best practices: package, CLI, tests, CI, docs, examples, governance

---

## Current State (Summary)
- Many standalone Python scripts in `scripts/` mixing cleaning, chunking, augmentation, validation, training, chat utilities
- Data scattered (`PyScience/`, `cybersecurity_datasets/`), no dataset catalog/manifest, no publishing automation
- No Python package (`pyproject.toml`), no tests/CI/pre‑commit/mypy/ruff, no Docker
- README points to external `PyScience/`, but not self‑contained here

Pain points: hard to reuse, trust, onboard, and reference datasets.

---

## Target Architecture

```
.
├── README.md                       # Intro + Quickstart
├── LICENSE | SECURITY.md | CONTRIBUTING.md | CODE_OF_CONDUCT.md
├── pyproject.toml                  # package + tools (ruff, black, mypy, pytest)
├── .pre-commit-config.yaml | .gitignore
├── .github/workflows/ci.yml        # lint/type/test/build
├── docs/                           # mkdocs or sphinx
│   ├── index.md
│   ├── quickstart.md
│   ├── pipelines.md
│   ├── datasets.md                 # catalog (generated from catalog.yaml)
│   └── api/
├── examples/
│   ├── minimal_agentic_pipeline.py
│   ├── notebooks/agentic_pipeline_walkthrough.ipynb
│   └── configs/minimal.yaml
├── configs/
│   ├── default.yaml
│   ├── chunking/{conservative.yaml, aggressive.yaml}
│   └── filters/safety.yaml
├── src/agentic_datasets/
│   ├── __init__.py
│   ├── cli.py                      # Typer/Click CLI
│   ├── config.py                   # Pydantic/yaml
│   ├── logging.py
│   ├── io/{readers.py, writers.py}
│   ├── schemas/{records.py, messages.py}
│   ├── normalize/normalize.py
│   ├── augment/{templates.py, augmenters.py}
│   ├── chunking/{base.py, conservative.py, aggressive.py}
│   ├── filters/{safety.py, dedupe.py}
│   ├── validate/{schema.py, quality.py}
│   ├── export/{huggingface.py, registry.py}
│   ├── stages/                     # Pure-function adapters for external tools
│   │   ├── base.py                 # Stage protocol: inputs/outputs/contracts
│   │   ├── s2m.py                  # S2M adapter
│   │   ├── apigenmt.py             # APIGenMT adapter
│   │   └── reviewinstruct.py       # ReviewInstruct adapter
│   ├── orchestrators/
│   │   ├── strands.py              # Preferred: Strands-SDK orchestrator
│   │   └── langgraph.py            # Fallback: LangChain RunnableGraph
│   └── pipeline.py                 # Orchestrator entry + YAML wiring
├── tests/
│   ├── test_cli.py | test_chunking.py | test_validate.py | test_export.py
├── data/samples/                   # tiny sample inputs (git‑tracked)
├── Dockerfile
└── catalog.yaml                    # dataset catalog source
```

Focus: dataset pipeline + catalog. Training/chat moved to `examples/` or separate repo.

---

## Pipeline Contract
- Inputs: raw dataset(s) (jsonl/csv/dir/HF id), YAML config
- Stages (agentic generation path):
  1) S2M: convert single‑turn prompts/answers into coherent multi‑turn conversations
  2) APIGenMT: enrich multi‑turn with tool/API invocation structure to make it agentic
  3) ReviewInstruct: critique and refine conversations for clarity, safety, and conversational naturalness
  4) Optional: chunk → filter/dedupe/safety → validate
  5) Export: JSONL and publish to Hugging Face with dataset card/versioning
- Outputs: artifacts (sharded jsonl), manifest, optional HF dataset push with card and version
- Errors: schema/validation or stage failures exit non‑zero with diagnostics
- Success: deterministic output given same inputs + config; validator passes

### Stage Interface (Single Responsibility)
- Each stage is a pure function: (List[ConversationRecord], StageConfig) -> Iterator[ConversationRecord]
- Stages are stateless and side-effect free; external calls encapsulated, inputs/outputs validated with Pydantic
- Errors are explicit exceptions with actionable messages; partial failures are recoverable via retry policies

### Artifact Handoff (Modularity)
- Intermediate outputs are JSONL sharded files with a small manifest (provenance, stage params, hashes)
- Orchestrators can run in-process (Python) or cross-process (containers) using a shared artifact store (local dir/S3)
- Reproducibility via content-addressed paths and pinned configs; each stage logs input/output digests

---

## Mapping Existing Code → Modules
- Chunkers: `bulletproof_chunker.py`, `extremely_conservative_chunker.py`, `ultra_*chunk*.py`, `chunk_dataset_*` → `chunking/{base,conservative,aggressive}.py`
- Converters/formatters: `convert_*`, `transform_to_agentic.py`, `convert_to_messages_format.py`, `complete_dataset_converter.py` → `normalize/` + `schemas/messages.py`
- Augmentation: `augment_agentic_conversations.py`, `enhanced_dataset_collector.py`, `enhance_coding_vulnerabilities.py`, `extract_agentic_pairs.py` → `augment/{templates.py, augmenters.py}`
- Filters/validators: `filter_*`, `validate_agentic_dataset.py`, `manual_dataset_validator.py`, `analyze_dataset_quality.py` → `filters/` + `validate/`
- IO/utils: `clean_*`, `fix_*`, `utilities/utils.py`, token fixers → `io/{readers,writers}.py` + shared utilities
- Export/publishing: `verify_huggingface.py`, dataset card/upload → `export/{huggingface.py, registry.py}`
- Training/chat: `train_*`, `mamba_*`, `chat_*` → `examples/` (minimal) or separate downstream repo

---

## Phased Migration Plan

Phase 3: Agentic Generation (S2M → APIGenMT → ReviewInstruct)
 - Status: Pure-function adapters scaffolded and registered (s2m, apigenmt, reviewinstruct)
 - Status: Tool-call schema added (assistant tool_calls, tool messages)
 - Status: YAML pipeline + tests working (in-process + strands flag routes to orchestrator scaffold)
 - Next: Wire actual Strands Graph + strands-tools to execute tool_calls and emit tool messages

Phase 0: Repo Hygiene
- Add LICENSE, SECURITY, CONTRIBUTING, CODE_OF_CONDUCT, .gitignore
- Add pyproject.toml with pinned deps + ruff/black/mypy/pytest
- Add pre‑commit config
- Add CI workflow stub (lint/type/test)
- Scaffold docs site structure

Phase 1: Package + CLI Skeleton
- Scaffold `src/agentic_datasets/` and `agentic-ds` CLI (Typer/Click)
- Implement minimal E2E: read small jsonl → normalize → validate → export jsonl
- Add unit tests (CLI happy path + schema error)
- Add examples/minimal config + tiny sample data

Phase 2: Port Core Functions
- Migrate chunkers (conservative/aggressive), validators, converters to typed modules
- Provide thin script shims that call the new CLI; mark legacy as deprecated

Phase 3: Agentic Generation (S2M → APIGenMT → ReviewInstruct)
- Add adapters/wrappers for S2M, APIGenMT, and ReviewInstruct as orchestrated stages
- Define strict I/O contracts between stages (messages schema + tool call annotations)
- Add tests with tiny fixtures to validate stage handoffs and error handling
 - Provide both in-process pipeline and containerized pipeline modes

Phase 4: Catalog + Publishing (Hugging Face)

  - Status: HF export utility and CLI `hf:push` implemented (requires HF token)
  - Status: Manual-dispatch GH Action `publish_hf.yml` added (expects HUGGINGFACE_HUB_TOKEN secret)
- Introduce `catalog.yaml` → generate `docs/datasets.md` + dataset cards
- Implement HF push with versioning; add manual dispatch GH workflow using secrets
  - Status: catalog.yaml scaffolded; CLI commands `catalog:list`, `catalog:show` added
  - Status: HF export utility and CLI `hf:push` implemented (requires HF token)

Phase 5: Docs + Examples
- Fill Quickstart, pipelines, API docs; add runnable examples and one notebook
 - Document two deployment patterns:
   1) Monolith container: one image with all stages, runs in-process (fastest dev path)
   2) Micro-stages: each stage as its own container; orchestrator coordinates via artifact store
 - Provide a minimal example for each pattern

Phase 6: Release v0.1.0
- Tag release, publish docs; optionally publish package to PyPI
- Archive/move legacy scripts to `examples/legacy/`

---

## Acceptance Criteria

 - Strands graph execution used in at least one example pipeline and test
- One‑command Quickstart creates a valid small agentic multi‑turn dataset
- CI passes (ruff/black --check, mypy, pytest)
- >80% coverage on core modules
- Catalog lists at least one published dataset with card + link
- Legacy scripts either replaced or shimmed with deprecation notes
 - Docker builds reproduce the same outputs across environments; CI proves this on a small sample

---

## Initial Implementation Checklist
- pyproject.toml (deps: typer, pydantic, pyyaml, datasets, ruff, black, mypy, pytest)
- src skeleton: `cli.py`, `pipeline.py`, `config.py`, `schemas/messages.py`
- Minimal CLI pipeline + tests
- docs scaffold + Quickstart
- CI + pre‑commit + Dockerfile
- `catalog.yaml` + simple generator for `docs/datasets.md`

---

## Risks & Mitigations
- Large data in git → keep tiny samples in repo; use DVC or HF datasets for real data
- Licensing/PII in datasets → enforce licenses in catalog; add PII/safety filters; document policy
- Publishing secrets → store in GH Actions secrets; manual publish workflow

---

## Quick Usage (after refactor)
- Run pipeline:
  - `agentic-ds run --config configs/default.yaml`
- Validate only:
  - `agentic-ds validate --input out/dataset.jsonl`
- Export to HF Hub:
  - `agentic-ds export hf --repo your-org/agentic-cybersec-v1 --push`

---

## Notes
- Orchestration: Prefer Strands‑SDK for stage coordination; fall back to LangChain runnable graph if Strands is unsuitable. Each stage implemented as a pure function adapter to keep tests simple and allow headless runs.
- Primary focus: dataset pipelines and catalog. Training is downstream and optional in this repo.
 - Development Preferences mapping:
   * Single responsibility: each stage is one thing; orchestration isolated; export isolated
   * Taxonomy: clear package structure for stages/orchestrators/filters/export
   * Pure functions: adapters return new records; no hidden state
   * Comments/naming: docstrings + descriptive names; configs validated with Pydantic
   * Tests: unit + integration via tiny fixtures and YAML pipeline runs
   * Version control: small, frequent commits; deprecation shims
   * Modularity/reuse: registry-based stages, YAML wiring, optional container boundaries
   * Self-contained & plug-and-play: pyproject, Dockerfile, example configs/data, no external setup
   * Containers: base image with pinned deps; optional per-stage images
   * CI/CD: lint/type/test + optional HF publish job
   * Reuse mature libs: Pydantic, Typer, Hugging Face, LangChain/Strands, tiktoken, datasketch, cleanlab (optional)
