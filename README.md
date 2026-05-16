<div align="center">

# 🤖 Agentic Datasets

**Config-driven, multi-turn pipelines for building agentic training data.**  
*Professionalized for AI-Native development.*

[![CI](https://github.com/danielrodrigo/datasets/actions/workflows/ci.yml/badge.svg)](https://github.com/danielrodrigo/datasets/actions)
[![License](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

## 🌟 Vision
Agentic Datasets bridges the gap between single-turn data and the complex, multi-turn reality of AI agents fighting to solve autonomous tasks. This pipeline allows you to seamlessly construct, validate, and execute synthetic data pipelines that incorporate tool interactions and complex reasoning behaviors.

---

## 🏗️ Architecture Overview

The codebase is governed by **strict modularity** (<200 LOC per file) and an **agnostic design pattern**.

- **Orchestrator (`cli.py`)**: Strands-first orchestration driven purely by declarative YAML. 
- **Pipeline Stages (`src/agentic_datasets/stages/`)**:
  - `AgentInstruct`: Expands and dedupes initial instructions.
  - `S2M`: Migrates single-turn data to coherent multi-turn structures.
  - `APIGenMT`: Injects synthetically generated JSON tool calls.
  - `ReviewInstruct`: Provides multi-agent refinement (chairman logic).
- **Core Abstractions**: Foundational models isolated in `src/agentic_datasets/schemas/` to strictly enforce domain boundaries.

---

## 🚀 Quick Start

Ensure you have Python 3.9+ and pip installed. We highly recommend using a virtual environment.

```bash
# 1. Clone and install in editable mode
pip install -e .[dev]

# 2. Run the core example pipeline
agentic-datasets run-config examples/pipeline.example.yaml

# 3. List available catalog entries
agentic-datasets catalog:list catalog.yaml
```

### 🧠 Strands & Ollama Integration
For optimal local testing, run with **Ollama**:
1. Install Ollama and pull `qwen3:8b` (default fallback).
2. Execute the test configuration:
```bash
agentic-datasets run-config examples/pipeline.ollama.yaml
```

*Note on Local Ollama*: 
- Set `OLLAMA_HOST` if your daemon isn't on `http://localhost:11434`.
- The `S2M` stage prefers a Strands Agent with OllamaModel. If Strands isn't installed, it falls back to a direct Ollama HTTP call cleanly.

### 📚 CLI Reference Overview

- `agentic-datasets run`: Ingest -> normalize -> validate -> export
- `agentic-datasets chunk`: Token-aware chunking of a JSONL dataset
- `agentic-datasets run-config`: Run a YAML pipeline spec with registered transforms
- `agentic-datasets transforms`: List available transforms
- `agentic-datasets catalog:list`, `catalog:show`: Inspect dataset catalog
- `agentic-datasets hf:push`: Push a JSONL dataset to Hugging Face with dataset card from catalog
- `agentic-datasets metrics`: Summarize tool_calls, tool messages, and backend/via metrics
- `agentic-datasets doctor`: Environment diagnostics for Strands/Ollama/tools

### 🛠️ Key Pipeline Feature: APIGenMT (Tool-Call Injection)

- `APIGenMT` uses a Strands-first path similar to S2M. It formats the current conversation and a tools catalog via prompts in `src/agentic_datasets/agents/prompts.py`, calls a Strands Agent backed by Ollama, then parses the returned JSON into a strict `Message` schema.
- If Strands or the model isn't available, it falls back gracefully by tagging metadata and passing messages through unchanged.
- Provide a tools catalog via the stage config (`tools: [...]`) to guide which functions can be injected.
- Fully compatible with Model Context Protocol (MCP) integrations.

### ⚙️ Self-Hosted CI Runner (Ollama)
If you require model-backed stages (e.g., S2M with Ollama) executed natively in CI:
1. Create a self-hosted runner matching label `ollama`.
2. Pre-pull models on the runner cache (`ollama pull qwen3:8b`).
3. Trigger `.github/workflows/self_hosted_ollama.yml` to execute end-to-end dataset builds and output verified JSONL artifacts.

For fast PR feedback without model footprints, `.github/workflows/smoke_hosted.yml` runs deterministically on standard GitHub-hosted UI runners.

---

## 🛡️ Professional Governance

This repository adheres to the highest level of AI-native engineering standards:
- **Agent Control Plane**: Governed by Kiro and Beads (`.kiro/`, `.agents/`, `.beads/`).
- **Development Principles**: Strict enforcement of SRP, Clean Architecture, and <200 LOC limits.
- **Licensing**: **Business Source License 1.1** (Transitions to Apache 2.0 in 2030).

For detailed contributor guidelines and agent steering instructions, please see [AGENTS.md](AGENTS.md).  
For extensive documentation on the orchestration SDK utilized internally, refer to the [Strands SDK Reference](docs/STRANDS_REFERENCE.md).

---
<div align="center">
  <em>Built for the future of Software Factories.</em>
</div>