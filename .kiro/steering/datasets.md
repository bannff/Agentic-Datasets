---
inclusion: always
---
# Agentic Datasets — Agent Operating Manual

Config-driven pipelines for building agentic, multi-turn datasets.

## RULES

ARCHITECTURE — Clean, staged pipelines. <150 LOC per file. SRP. Pipeline logic in `src/agentic_datasets/`, CLI in `src/agentic_datasets/cli.py`.

STAGES — Every stage follows the `Stage` base class. Main stages: `AgentInstruct`, `S2M`, `APIGenMT`, `ReviewInstruct`. Strands-first implementation with LiteLLM/Ollama fallbacks.

TESTING — Pytest required for all new transforms and stages. Run `pytest` before and after changes.

MEMORY — Use companion-x memory brick. `memory_store`, `memory_retrieve` via `mcp_companion_x_call_brick_tool`. Always pass `user_id: "kiro-agent"`. Details: `.agents/steering/companion-memory.md`

ISSUE TRACKING — Beads (`bd`) is the preferred local tracker. GitHub Issues/Discussions/Projects for public roadmap. Details: `.agents/steering/beads-workflow.md`

SHELL SAFETY — Always use non-interactive flags: `cp -f`, `mv -f`, `rm -f`, `rm -rf`. Never let shell commands hang on prompts.

## SESSION PROTOCOL

1. Check GitHub Issues or `bd ready` for work.
2. Claim work by labeling the issue `status/in-progress` or `bd update <id> --claim`.
3. Work in small, verifiable increments.
4. Run CI checks before pushing: `ruff check src`, `mypy src`, `pytest`.
5. When done: close issue and push.
