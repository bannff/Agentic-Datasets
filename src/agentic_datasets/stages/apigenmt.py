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
    ) -> None:
        self.provider = provider
        self.model_name = model_name or ("qwen3:8b" if provider == "ollama" else None)
        self.temperature = max(0.0, min(1.0, temperature))
        self.enabled = enabled
        self.tools = tools or []


def apigenmt(
    records: Iterable[ConversationRecord],
    config: Optional[APIGenMTConfig | dict] = None,
) -> Iterator[ConversationRecord]:
    """APIGenMT stage: inject tool calls into conversations using Strands-first path.

    - Prefer Strands Agent with Ollama model (dynamic import)
    - Parse assistant messages with tool_calls and append corresponding tool messages
    - Fallback: set metadata flag if agent/model not available
    """
    # Coerce config
    if config is None:
        cfg = APIGenMTConfig()
    elif isinstance(config, dict):
        cfg = APIGenMTConfig(**config)
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

    for rec in records:
        if strands_agent is None:
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
            meta = {**(rec.metadata or {}), "stage": "apigenmt", "agentic": True, "via": "fallback"}
            yield ConversationRecord(messages=rec.messages, metadata=meta, source=rec.source, id=rec.id)
