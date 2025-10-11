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

- LiteLLM:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/litellm/

- LlamaAPI:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/llamaapi/