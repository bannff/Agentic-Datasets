from __future__ import annotations

from typing import Any, Union
from collections.abc import Iterable, Iterator
import importlib

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
        """Try to execute a tool_call using strands-tools if available.

        Returns a tool message on success; None on failure/unavailable.
        """
        tool_fn = None
        # First try top-level export (e.g., from strands_tools import file_read)
        try:
            st = importlib.import_module("strands_tools")
            tool_fn = getattr(st, tool_call.name)
        except Exception:
            tool_fn = None

        # Next, try submodule with same name (e.g., strands_tools.browser)
        if tool_fn is None:
            try:
                mod = importlib.import_module(f"strands_tools.{tool_call.name}")
                tool_fn = getattr(mod, tool_call.name, None)
            except Exception:
                tool_fn = None

        if tool_fn is None:
            return None

        # Build a minimal 'ToolUse' compatible dict input
        tool_input: dict[str, Union[str, dict[str, Any]]] = {
            "input": tool_call.arguments,
            "toolUseId": tool_call.id or "call",
        }
        try:
            result = tool_fn(tool_input)
            # Expect dict with content list of {text: ...}
            output_text = "\n".join([c.get("text", "") for c in result.get("content", [])])
            return Message(
                role="tool",
                content=output_text or "",
                tool_name=tool_call.name,
                tool_call_id=tool_call.id,
                tool_output=result,
            )
        except Exception as e:
            return Message(
                role="tool",
                content=f"tool {tool_call.name} failed: {e}",
                tool_name=tool_call.name,
                tool_call_id=tool_call.id,
                tool_output={"status": "error", "error": str(e)},
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
