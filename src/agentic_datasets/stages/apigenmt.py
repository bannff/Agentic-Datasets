from __future__ import annotations

import importlib
import json
import logging
from typing import Iterable, Iterator, Optional, Any, Dict, List

from ..schemas.messages import ConversationRecord, Message, ToolCall
from ..agents.prompts import (
    APIGENMT_SYSTEM_PROMPT,
    APIGENMT_USER_TEMPLATE,
    format_conversation_for_review,
    format_tools_catalog,
)

logger = logging.getLogger(__name__)


class APIGenMTConfig:
    def __init__(
        self,
        provider: str = "ollama",
        model_name: Optional[str] = None,
        temperature: float = 0.2,
        enabled: bool = True,
        tools: Optional[List[Dict[str, Any]]] = None,
        synthesize_on_fallback: bool = False,
    ) -> None:
        self.provider = provider
        self.model_name = model_name or ("qwen3:8b" if provider == "ollama" else None)
        self.temperature = max(0.0, min(1.0, temperature))
        self.enabled = enabled
        self.tools = tools or []
        # When no agent/model available, optionally synthesize one assistant tool_call
        # so downstream tool execution/injection can be tested deterministically.
        self.synthesize_on_fallback = synthesize_on_fallback


def apigenmt(
    records: Iterable[ConversationRecord],
    config: Optional[APIGenMTConfig | dict] = None,
    **kwargs: Any,
) -> Iterator[ConversationRecord]:
    """APIGenMT stage: inject tool calls into conversations using Strands-first path.

    - Prefer Strands Agent with Ollama model (dynamic import)
    - Parse assistant messages with tool_calls and append corresponding tool messages
    - Fallback: set metadata flag if agent/model not available
    """
    # Coerce config. Support both nested `config: {...}` and top-level params like `tools:` in YAML.
    if config is None and kwargs:
        # Treat top-level kwargs as config fields (e.g., tools, provider, model_name)
        cfg = APIGenMTConfig(**kwargs)
    elif isinstance(config, dict):
        # Merge explicit config dict with any kwargs overrides if present
        merged: Dict[str, Any] = {**config, **kwargs}
        cfg = APIGenMTConfig(**merged)
    elif config is None:
        # No config provided at all; use defaults
        cfg = APIGenMTConfig()
    else:
        # Already an APIGenMTConfig instance; allow kwargs to override common fields
        if kwargs:
            # Reconstruct applying overrides to keep immutability semantics simple
            cfg = APIGenMTConfig(
                provider=kwargs.get("provider", config.provider),
                model_name=kwargs.get("model_name", config.model_name),
                temperature=kwargs.get("temperature", config.temperature),
                enabled=kwargs.get("enabled", config.enabled),
                tools=kwargs.get("tools", config.tools),
            )
        else:
            cfg = config

    if not cfg.enabled:
        yield from records
        return

    # Try to set up Strands Agent when provider is ollama
    strands_agent = None
    if cfg.provider.lower() == "ollama":
        try:
            strands_module = importlib.import_module("strands")
            ollama_module = importlib.import_module("strands.models.ollama")
            Agent = getattr(strands_module, "Agent")
            OllamaModel = getattr(ollama_module, "OllamaModel")

            import os

            host = os.getenv("OLLAMA_HOST") or "http://localhost:11434"
            model = OllamaModel(host=host, model_id=cfg.model_name or "qwen3:8b")
            strands_agent = Agent(model=model)
        except Exception as e:
            logger.debug(f"Strands unavailable for APIGenMT: {e}")
            strands_agent = None

    # Helper to parse tool_calls JSON element into schema
    def _parse_tool_calls(tc_list: List[Dict[str, Any]]) -> List[ToolCall]:
        out: List[ToolCall] = []
        for raw in tc_list:
            try:
                # Support either OpenAI-style {id,type,function:{name,arguments}} or flat {id,name,arguments}
                if "function" in raw:
                    fn = raw["function"] or {}
                    name = fn.get("name")
                    args = fn.get("arguments")
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {"__raw__": args}
                    out.append(
                        ToolCall(
                            id=raw.get("id"),
                            name=name or "unknown",
                            arguments=args or {},
                            status="requested",
                        )
                    )
                else:
                    args = raw.get("arguments", {})
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except Exception:
                            args = {"__raw__": args}
                    out.append(
                        ToolCall(
                            id=raw.get("id"),
                            name=(raw.get("name") or "unknown"),
                            arguments=args or {},
                            status="requested",
                        )
                    )
            except Exception as e:
                logger.debug(f"Failed to parse tool_call {raw}: {e}")
        return out

    def _synthesize_tool_call_record(rec: ConversationRecord) -> ConversationRecord:
        tool = cfg.tools[0] or {}
        name = tool.get("name") or "tool"
        params = tool.get("parameters") or {}
        args: Dict[str, Any] = {}
        for k, spec in params.items():
            t = (spec or {}).get("type")
            if t == "string":
                if k.lower() in ("keyword", "query"):
                    last_user = next((m.content for m in reversed(rec.messages) if m.role == "user"), "example")
                    args[k] = (last_user.split()[:2] or ["example"])[:1][0]
                elif k.lower() in ("hostname", "domain"):
                    args[k] = "example.com"
                else:
                    args[k] = "example"
            else:
                args[k] = None
        tool_call = ToolCall(id="tc1", name=name, arguments=args, status="requested")
        # Attach to last assistant if present to avoid consecutive assistant messages
        new_messages = list(rec.messages)
        if new_messages and new_messages[-1].role == "assistant":
            last = new_messages[-1]
            existing = list(last.tool_calls or [])
            existing.append(tool_call)
            # Replace last message with updated tool_calls
            new_messages[-1] = Message(
                role=last.role,
                content=last.content or "[Invoking tool]",
                metadata=last.metadata,
                tool_calls=existing,
            )
        else:
            synth_msg = Message(role="assistant", content="[Invoking tool]", tool_calls=[tool_call])
            new_messages.append(synth_msg)
        meta = {**(rec.metadata or {}), "stage": "apigenmt", "agentic": True, "via": "fallback-synth"}
        return ConversationRecord(messages=new_messages, metadata=meta, source=rec.source, id=rec.id)

    for rec in records:
        if strands_agent is None:
            # Fallback path: optionally synthesize a tool_call to enable tool execution tests
            if cfg.synthesize_on_fallback and cfg.tools:
                try:
                    yield _synthesize_tool_call_record(rec)
                    continue
                except Exception as e:
                    logger.debug(f"APIGenMT synthesize_on_fallback failed: {e}")
            # Metadata-only fallback
            meta = {**(rec.metadata or {}), "stage": "apigenmt", "agentic": True, "via": "fallback"}
            yield ConversationRecord(messages=rec.messages, metadata=meta, source=rec.source, id=rec.id)
            continue

        # Build prompt inputs
        conv_text = format_conversation_for_review(rec.messages)
        tools_catalog_text = format_tools_catalog(cfg.tools)
        user_prompt = APIGENMT_USER_TEMPLATE.format(
            conversation_text=conv_text,
            tools_catalog=tools_catalog_text,
        )

        try:
            result = strands_agent(
                user_prompt,
                system_prompt=APIGENMT_SYSTEM_PROMPT,
                params={"temperature": cfg.temperature},
            )
            text = getattr(result, "text", None) or getattr(result, "content", None) or str(result)
            data = json.loads(text)

            new_messages: List[Message] = []
            for m in data:
                role = m.get("role")
                content = (m.get("content") or "").strip()
                if not role or not content:
                    continue
                # Assistant messages may contain tool_calls
                tool_calls_data = m.get("tool_calls") or []
                tool_calls = _parse_tool_calls(tool_calls_data) if tool_calls_data else None

                if role == "tool":
                    # Expect name and optional tool_call_id / output
                    name = m.get("name") or m.get("tool_name")
                    tcid = m.get("tool_call_id") or (tool_calls_data[0].get("id") if tool_calls_data else None)
                    tool_output = m.get("tool_output") if isinstance(m.get("tool_output"), dict) else None
                    new_messages.append(
                        Message(
                            role="tool",
                            content=content,
                            tool_name=name,
                            tool_call_id=tcid,
                            tool_output=tool_output,
                        )
                    )
                else:
                    new_messages.append(
                        Message(role=role, content=content, tool_calls=tool_calls)
                    )

            if not new_messages:
                raise ValueError("APIGenMT returned empty/invalid conversation")

            yield ConversationRecord(
                messages=new_messages,
                metadata={**(rec.metadata or {}), "stage": "apigenmt", "via": "strands", "provider": cfg.provider, "model": cfg.model_name},
                source=rec.source,
                id=rec.id,
            )
        except Exception as e:
            logger.warning(f"APIGenMT agent failed for {rec.id}: {e}. Using fallback metadata.")
            if cfg.synthesize_on_fallback and cfg.tools:
                try:
                    yield _synthesize_tool_call_record(rec)
                    continue
                except Exception as se:
                    logger.debug(f"APIGenMT synthesize_on_fallback (error path) failed: {se}")
            meta = {**(rec.metadata or {}), "stage": "apigenmt", "agentic": True, "via": "fallback"}
            yield ConversationRecord(messages=rec.messages, metadata=meta, source=rec.source, id=rec.id)
