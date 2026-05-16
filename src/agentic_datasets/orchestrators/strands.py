from __future__ import annotations

from typing import Any, Union
from collections.abc import Iterable, Iterator
import importlib
import os

from ..schemas.messages import ConversationRecord, Message, ToolCall


def run_strands_pipeline(
    stages: list[dict[str, Any]],
    records: Iterable[ConversationRecord],
) -> Iterator[ConversationRecord]:
    """Placeholder for Strands-SDK based orchestration.

    This will:
      - Construct a graph/swarm of strands agents/tools per configured stages
      - Stream records through stages with retry/timeouts
      - Optionally persist intermediates to artifact store
    For now, it executes using in-process registry until Strands wiring is added.
    """
    # Lazy import to avoid hard dep at base install
    from ..registry import registry

    def _maybe_exec_tool(tool_call: ToolCall) -> Message | None:
        """Try to execute a tool_call using configured backends.

        Backend order is controlled by env AGENTIC_TOOLS_BACKENDS (comma-separated),
        defaulting to "strands" (strict). Returns a tool message on success; None if no backend resolves.
        """
        env_backends = os.getenv("AGENTIC_TOOLS_BACKENDS")
        backend_order = [
            b.strip()
            for b in (env_backends if env_backends is not None else "strands,local")
            .lower()
            .split(",")
            if b.strip()
        ]
        # Always include 'local' as last-resort fallback for deterministic stub tools
        if "local" not in backend_order:
            backend_order.append("local")

        def _resolve_fn(name: str) -> tuple[Any | None, str | None]:
            for backend in backend_order:
                if backend == "strands":
                    # Try community tools top-level first, then submodule
                    try:
                        st = importlib.import_module("strands_tools")
                        fn = getattr(st, name)
                        return fn, "strands_tools"
                    except Exception:
                        pass
                    try:
                        mod = importlib.import_module(f"strands_tools.{name}")
                        fn = getattr(mod, name, None)
                        if fn:
                            return fn, "strands_tools"
                    except Exception:
                        pass
                elif backend == "local":
                    try:
                        lt = importlib.import_module("agentic_datasets.local_tools")
                        fn = getattr(lt, name)
                        return fn, "local_tools"
                    except Exception:
                        pass
            return None, None

        tool_fn, backend_used = _resolve_fn(tool_call.name)
        if tool_fn is None:
            return None

        # Build a minimal 'ToolUse' compatible dict input
        tool_input: dict[str, Union[str, dict[str, Any]]] = {
            "input": tool_call.arguments,
            "toolUseId": tool_call.id or "call",
        }
        try:
            result = tool_fn(tool_input)
            # Annotate backend in the tool output for transparency
            if isinstance(result, dict):
                result = {**result, "backend": backend_used or "unknown", "ok": True}
            output_text = "\n".join(
                [
                    c.get("text", "")
                    for c in (result.get("content", []) if isinstance(result, dict) else [])
                ]
            )
            return Message(
                role="tool",
                content=output_text or "",
                tool_name=tool_call.name,
                tool_call_id=tool_call.id,
                tool_output=result
                if isinstance(result, dict)
                else {
                    "backend": backend_used or "unknown",
                    "content": [],
                    "raw": str(result),
                    "ok": True,
                },
            )
        except Exception as e:
            return Message(
                role="tool",
                content=f"tool {tool_call.name} failed: {e}",
                tool_name=tool_call.name,
                tool_call_id=tool_call.id,
                tool_output={
                    "status": "error",
                    "error": str(e),
                    "backend": backend_used or "unknown",
                    "ok": False,
                },
            )

    def _inject_tool_messages(stream: Iterable[ConversationRecord]) -> Iterator[ConversationRecord]:
        for rec in stream:
            new_msgs: list[Message] = []
            for m in rec.messages:
                new_msgs.append(m)
                if m.role == "assistant" and m.tool_calls:
                    for tc in m.tool_calls:
                        tool_msg = _maybe_exec_tool(tc)
                        if tool_msg is not None:
                            new_msgs.append(tool_msg)
            if len(new_msgs) != len(rec.messages):
                yield ConversationRecord(
                    messages=new_msgs,
                    metadata=rec.metadata,
                    source=rec.source,
                    id=rec.id,
                )
            else:
                yield rec

    stream: Iterable[ConversationRecord] = records
    for s in stages:
        name = s["name"]
        params = dict(s.get("params", {}))
        fn = registry.get(name)
        stream = fn(stream, **params)
        # After each stage, inject tool results if any tool_calls present
        stream = _inject_tool_messages(stream)

    yield from stream
