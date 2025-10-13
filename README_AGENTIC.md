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
- agentic-datasets metrics: Summarize tool_calls, tool messages, and backend/via counts
- agentic-datasets doctor: Environment diagnostics for Strands/Ollama/tools

## Examples

- List transforms
  agentic-datasets transforms

- Run sample YAML pipeline
  agentic-datasets run-config examples/pipeline.example.yaml

- Run with local Ollama (Qwen3 8B)
  1) Install extras and Ollama client: pip install -e .[dev,ollama]
  2) Install and start Ollama: https://ollama.com/download
  3) Pull model: ollama pull qwen3:8b
  4) Run: agentic-datasets run-config examples/pipeline.ollama.yaml

- List catalog entries
  agentic-datasets catalog:list catalog.yaml

- Push to Hugging Face
  agentic-datasets hf:push sample-conversations your-org/sample-conversations examples/sample.jsonl --catalog catalog.yaml --private

Notes
- Set HF token: huggingface-cli login
- CI runs lint/type-check/tests on PRs; release workflow publishes to PyPI on tags (requires PYPI_API_TOKEN secret)

## APIGenMT (Tool-call injection)

- APIGenMT uses a Strands-first path similar to S2M. It formats the current conversation and a tools catalog via prompts in `src/agentic_datasets/agents/prompts.py`, calls a Strands Agent backed by Ollama, then parses returned JSON into Message/ToolCall schema.
- If Strands or the model isn't available, it falls back gracefully by tagging metadata and passing messages through unchanged.
- Provide a tools catalog via the stage config (`tools: [...]`) to guide which functions can be injected.
- Parsing is hardened to handle JSON arrays wrapped in prose and merges consecutive turns to satisfy schema alternation. If tools execute, injected tool messages include a backend indicator (e.g., `local_tools`).

## Self-hosted runner with Ollama (CI)

If you need model-backed stages (e.g., S2M with Ollama) in CI, the simplest approach is a self-hosted runner with Ollama installed.

Steps (macOS or Linux host):

1) Create/assign a self-hosted runner to this repo or org
  - GitHub → Settings → Actions → Runners → New self-hosted runner
  - Follow the registration script on the target machine

2) Install Ollama and pull models on the runner
  - Install Ollama (https://ollama.com/download)
  - Ensure the service is running and pre-pull models to cache, e.g.: `ollama pull qwen3:8b`

3) Trigger the workflow
  - Workflow: `.github/workflows/self_hosted_ollama.yml`
  - Run it from GitHub Actions (workflow_dispatch) and optionally override the `config` input

The workflow verifies http://localhost:11434, installs `agentic-datasets` with `[ollama]` extra, runs the pipeline, and uploads `out*.jsonl` files as artifacts. No OLLAMA_HOST is needed beyond localhost.

Labels and preflight
- Label your runner with `ollama` so only machines with Ollama pick up the job (`runs-on: [self-hosted, ollama]`).
- Optional preflight on the runner:
  - scripts/runner_preflight_ollama.sh (defaults to qwen3:8b)
  - Example:
    - `bash scripts/runner_preflight_ollama.sh`

Hosted smoke checks
- For fast PR feedback without models, use `.github/workflows/smoke_hosted.yml`.
  - Runs lint, typecheck, tests, and a deterministic example pipeline on regular hosted runners.

## Strands-SDK Docs:

- Quick Start:
https://strandsagents.com/latest/documentation/docs/user-guide/quickstart/

### Agents

- Agent Loop:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/agent-loop/

- State:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/state/

- Session Management:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/session-management/

- Prompts:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/prompts/

- Hooks:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/hooks/

- Structured Output:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/structured-output/

- Conversation Management:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/conversation-management/

### Tools

- Overview:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/tools_overview/

- Model Context Protocol (MCP):
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/mcp-tools/

- Tools Package:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/community-tools-package/

### Streaming

- Overview:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/streaming/overview/

- Async Iterators:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/streaming/async-iterators/

- Callback Handlers:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/streaming/callback-handlers/

### Multi Agent

- A2A: 
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/

- Agents As Tools:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/

- Swarm:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/

- Graph:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/

- Workflow: 
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/

- Multi Agent Patterns:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/multi-agent-patterns/

### Observability & Eval

- Observability:
https://strandsagents.com/latest/documentation/docs/user-guide/observability-evaluation/observability/

- Metrics:
https://strandsagents.com/latest/documentation/docs/user-guide/observability-evaluation/metrics/

- Traces:
https://strandsagents.com/latest/documentation/docs/user-guide/observability-evaluation/traces/

- Logs:
https://strandsagents.com/latest/documentation/docs/user-guide/observability-evaluation/logs/

- Eval:
https://strandsagents.com/latest/documentation/docs/user-guide/observability-evaluation/evaluation/

### Model Provider:

- Bedrock:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/amazon-bedrock/

- Anthropic:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/anthropic/

- OpenAI:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/openai/

- MistralAI:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/mistral/

- llama.cpp:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/llamacpp/

- ollama:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/ollama/
  Notes: Requires local Ollama daemon (default http://localhost:11434). Use `ollama pull qwen3:8b`.

## Local Ollama notes

- Set OLLAMA_HOST if your daemon isn't on http://localhost:11434, e.g. `export OLLAMA_HOST=http://remote-host:11434`.
- The S2M stage prefers a Strands Agent with OllamaModel and S2M prompts. If Strands isn't installed, it falls back to a direct Ollama HTTP call.
- Use `examples/pipeline.ollama.yaml` (with `orchestrator: strands`) to exercise the agent path locally.

- LiteLLM:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/litellm/

- LlamaAPI:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/llamaapi/