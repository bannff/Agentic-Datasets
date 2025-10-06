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

- LiteLLM:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/litellm/

- LlamaAPI:
https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/llamaapi/