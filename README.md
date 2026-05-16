# Agentic Datasets

Config-driven pipelines for building agentic, multi-turn datasets with validation, optional tool-call execution, and Hugging Face publishing. Includes a Typer CLI, tests, CI workflows, and Docker.

License: Business Source License 1.1. See [LICENSE](LICENSE) for the full text and Change Date.

Badges (workflows may vary by fork):
- CI: .github/workflows/ci.yml
- Smoke (hosted): .github/workflows/smoke_hosted.yml
- Self-hosted (Ollama): .github/workflows/self_hosted_ollama.yml
- Run pipeline (on-demand): .github/workflows/run_pipeline.yml

## Quickstart

1) Create a virtualenv and install in editable mode with dev extras
- pip install -e .[dev]

2) Run an example pipeline
- agentic-datasets run-config examples/pipeline.example.yaml
- agentic-datasets run-config examples/pipeline.agentic.yaml

3) List transforms and catalog entries
- agentic-datasets transforms
- agentic-datasets catalog:list catalog.yaml

4) Publish a JSONL to Hugging Face (requires login/token)
- agentic-datasets hf:push <entry_id> <repo_id> <path-to.jsonl> --catalog catalog.yaml

## Local model (Ollama) and Strands-first

- Stages prefer the Strands Agents SDK path and fall back gracefully if unavailable.
- For local experiments, install Ollama and pull a model (default we use qwen3:8b):
   - https://ollama.com/download
   - ollama pull qwen3:8b
- Use the provided config to exercise the Strands-first S2M/APIGenMT/ReviewInstruct path locally:
   - agentic-datasets run-config examples/pipeline.ollama.yaml
- Set OLLAMA_HOST if your daemon is not at http://localhost:11434 (e.g., export OLLAMA_HOST=http://remote:11434).

## Stages implemented

- AgentInstruct: Expand and dedupe instructions prior to multi-turn generation.
- S2M (Single → Multi-turn): Converts single-turn pairs to coherent multi-turn conversations.
- APIGenMT: Injects JSON tool calls and tool responses (APIGen-style) when applicable.
- ReviewInstruct: Multi-agent review with a chairman accept/refine decision and optional refinement.

All stages are wired Strands-first with tested fallbacks. Schemas are strict (Pydantic v2) and export excludes None fields.

## CLI overview

- agentic-datasets run: Ingest → normalize → validate → export
- agentic-datasets chunk: Token-aware chunking
- agentic-datasets run-config: Run a YAML pipeline spec
- agentic-datasets transforms: List registered transforms
- agentic-datasets catalog:list/show: Inspect dataset catalog
- agentic-datasets hf:push: Push JSONL to Hugging Face with dataset card
- agentic-datasets metrics: Summarize tool_calls, tool messages, backends, via
- agentic-datasets doctor: Check Strands/Ollama/tools environment readiness

Examples in repo:
- examples/pipeline.example.yaml
- examples/pipeline.agentic.yaml
- examples/pipeline.ollama.yaml

## APIGenMT tools (how to wire)

APIGenMT suggests and injects tool calls when you provide a tools catalog in the stage params. We pass that catalog into the prompt so the model knows what’s available, and we then parse JSON tool calls out of assistant messages. After a stage completes, the orchestrator attempts to execute any tool calls via `strands_tools` and inject a `role: tool` message with the result. If a tool isn’t available, we keep the tool call but skip execution.

Minimal example (add to your APIGenMT stage):

```yaml
stages:
   - name: apigenmt
      params:
         tools:
            - name: search_cve
               description: "Search CVE database by keyword and return recent CVEs."

      ### Robust parsing and turn alternation

      - APIGenMT is hardened to extract a top-level JSON array even when the model wraps it with prose.
      - It tolerates `function`-style and flat tool_call formats and safely parses stringified `arguments`.
      - It merges consecutive user/assistant turns to satisfy schema alternation rules, reducing validation failures on noisy model outputs.
               parameters:
                  keyword:
                     type: string
      - Default backend order is `strands` then `local` (deterministic stubs) so we prefer real `strands_tools` when available.
      - The orchestrator always appends `local` as a last-resort fallback for deterministic demos/tests.
      - Reorder with env (note: `local` remains a final fallback):
            - name: dns_lookup
               description: "Resolve DNS records for a hostname."
               parameters:
      # or local first for offline demos:
      export AGENTIC_TOOLS_BACKENDS=local,strands
                     description: "Domain to resolve"
                     required: true
```

      ## Metrics and diagnostics

      - Summarize an output JSONL:

         - `agentic-datasets metrics path/to/out.jsonl`

         Example output (truncated):

         ```json
         {
            "records": 50,
            "assistant_tool_calls": 12,
            "tool_messages": 74,
            "backend_counts": { "local_tools": 24 },
            "via_counts": { "strands": 13, "fallback": 37 }
         }
         ```

      - Environment doctor:

         - `agentic-datasets doctor` → prints OLLAMA_HOST, AGENTIC_TOOLS_BACKENDS, Strands/Ollama importability, and tool backend resolution.

Notes
- APIGen doesn’t require MCP specifically; our implementation uses Strands-first prompts and best-effort execution via `strands_tools` if installed. Without it, you’ll still see tool_calls in assistant messages but no tool messages.
- We parse OpenAI-style function calls or a flat schema; see `ToolCall` in `src/agentic_datasets/schemas/messages.py`.
- For true MCP-backed tools, you can integrate an MCP tool server with Strands; this repo keeps it simple by using community tools.

### Tool execution backends

- Default backend order is `strands` then `local` (deterministic stubs) so we prefer real `strands_tools` when available.
- Override with env:

```zsh
export AGENTIC_TOOLS_BACKENDS=strands,local   # default
# or strictly strands only (fail if not found):
export AGENTIC_TOOLS_BACKENDS=strands
# or local first for offline demos:
export AGENTIC_TOOLS_BACKENDS=local,strands
```

- Tool messages include `tool_output.backend` so you can see which backend executed.


## CI/CD (summary)

- Hosted smoke checks: .github/workflows/smoke_hosted.yml
- Self-hosted Ollama pipeline: .github/workflows/self_hosted_ollama.yml (labels: [self-hosted, ollama])
- Nightly: .github/workflows/nightly.yml (manual-only by design)
- Publish to Hugging Face on tag: .github/workflows/publish_hf_on_tag.yml
- On-demand pipeline runner: .github/workflows/run_pipeline.yml (artifact uploads of out*.jsonl)

Secrets/vars for publishing:
- HUGGINGFACE_HUB_TOKEN (secret)
- Optional tag-publish vars: PUBLISH_ENTRY_ID, PUBLISH_REPO_ID, PUBLISH_DATA_PATH

## Strands SDK docs (preserved links)

- Quick Start:
   https://strandsagents.com/latest/documentation/docs/user-guide/quickstart/

Agents
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

Tools
- Overview:
   https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/tools_overview/
- Model Context Protocol (MCP):
   https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/mcp-tools/
- Community Tools Package:
   https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/community-tools-package/

Streaming
- Overview:
   https://strandsagents.com/latest/documentation/docs/user-guide/concepts/streaming/overview/
- Async Iterators:
   https://strandsagents.com/latest/documentation/docs/user-guide/concepts/streaming/async-iterators/
- Callback Handlers:
   https://strandsagents.com/latest/documentation/docs/user-guide/concepts/streaming/callback-handlers/

Multi Agent
- Agent-to-Agent:
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

Observability & Eval
- Observability:
   https://strandsagents.com/latest/documentation/docs/user-guide/observability-evaluation/observability/
- Metrics:
   https://strandsagents.com/latest/documentation/docs/user-guide/observability-evaluation/metrics/
- Traces:
   https://strandsagents.com/latest/documentation/docs/user-guide/observability-evaluation/traces/
- Logs:
   https://strandsagents.com/latest/documentation/docs/user-guide/observability-evaluation/logs/
- Evaluation:
   https://strandsagents.com/latest/documentation/docs/user-guide/observability-evaluation/evaluation/

Model Providers
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
- Ollama:
   https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/ollama/
- LiteLLM:
   https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/litellm/
- LlamaAPI:
   https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/llamaapi/

## Repo notes

- Examples live in examples/ (sample JSONL and pipelines).
- Legacy/large directories are archived; see docs/LEGACY.md.
- If your IDE flags GitHub Actions contexts (vars/secrets) as unknown, those are benign local warnings.

## Status (high level)

- Stages: AgentInstruct, S2M, APIGenMT, ReviewInstruct are implemented with Strands-first paths and tested fallbacks. Unit tests cover key behaviors (including tool-call JSON parsing and review decisions). Nightly workflow is manual-only by design.
- Publishing: Manual and tag-triggered flows available. Artifacts are uploaded for on-demand runs.

Questions or issues? Open an issue with the pipeline config you’re trying to run and the stage of failure.