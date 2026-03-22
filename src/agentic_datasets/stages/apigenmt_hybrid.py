"""APIGenMT Hybrid: Fast semantic tool injection using local LLM.

Strategy:
1. For each assistant message in conversation, ask Qwen3 a lightweight question:
   "Should this assistant response include a tool call? If yes, which one? Answer: TOOL_NAME or NONE"
2. Parse single-word response (TOOL_NAME | NONE)
3. If tool selected, extract parameters from response text using keyword heuristics
4. Inject tool call directly (no JSON parsing, no full regeneration)

Speed: ~5-10 seconds per record (vs 3 minutes with full regeneration)
Quality: Semantically-selected tools (vs keyword matching alone)
"""

from __future__ import annotations

import logging
import os
from typing import Iterable, Iterator, Optional, Any, Dict, List

from ..schemas.messages import ConversationRecord, Message, ToolCall

logger = logging.getLogger(__name__)


class APIGenMTConfig:
    def __init__(
        self,
        provider: str = "ollama",
        model_name: Optional[str] = None,
        temperature: float = 0.1,  # Lower temp = more deterministic
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
    config: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Iterator[ConversationRecord]:
    """APIGenMT Hybrid: Fast semantic tool injection using local Qwen3.

    For each assistant message:
    1. Ask Qwen3 (local): "Should this use a tool? TOOL_NAME or NONE"
    2. Parse single-word response
    3. Inject tool call if selected
    4. Add synthetic response

    ~10x faster than full regeneration, semantically meaningful.
    """
    # Config coercion
    if config is None and kwargs:
        cfg = APIGenMTConfig(**kwargs)
    elif isinstance(config, dict):
        merged: Dict[str, Any] = {**config, **kwargs}
        cfg = APIGenMTConfig(**merged)
    elif config is None:
        cfg = APIGenMTConfig()
    else:
        if kwargs:
            cfg = APIGenMTConfig(
                provider=kwargs.get(
                    "provider", config.provider if hasattr(config, "provider") else "ollama"
                ),
                model_name=kwargs.get(
                    "model_name", config.model_name if hasattr(config, "model_name") else None
                ),
                temperature=kwargs.get(
                    "temperature", config.temperature if hasattr(config, "temperature") else 0.1
                ),
                enabled=kwargs.get(
                    "enabled", config.enabled if hasattr(config, "enabled") else True
                ),
                tools=kwargs.get("tools", config.tools if hasattr(config, "tools") else []),
            )
        else:
            cfg = config

    if not cfg.enabled:
        yield from records
        return

    # Try to import and set up Ollama
    strands_agent = None
    if cfg.provider.lower() == "ollama":
        try:
            import importlib

            strands_module = importlib.import_module("strands")
            ollama_module = importlib.import_module("strands.models.ollama")
            Agent = getattr(strands_module, "Agent")
            OllamaModel = getattr(ollama_module, "OllamaModel")

            host = os.getenv("OLLAMA_HOST") or "http://localhost:11434"
            model = OllamaModel(host=host, model_id=cfg.model_name or "qwen3:8b")
            strands_agent = Agent(model=model)
            logger.debug(f"Strands Agent initialized with {cfg.model_name} at {host}")
        except Exception as e:
            logger.warning(
                f"Strands Agent unavailable for APIGenMT: {e}. Will use keyword fallback."
            )
            strands_agent = None

    # Tool name list for prompting
    tool_names = [t.get("name", "unknown") for t in cfg.tools]  # type: ignore
    tool_list_str = ", ".join(tool_names) if tool_names else "none"

    for rec in records:
        if not cfg.tools:
            # No tools, pass through
            meta: Dict[str, Any] = {  # type: ignore
                **(rec.metadata or {}),
                "stage": "apigenmt",
                "agentic": False,
                "via": "passthrough",
            }
            yield ConversationRecord(
                messages=rec.messages, metadata=meta, source=rec.source, id=rec.id
            )
            continue

        try:
            new_messages = list(rec.messages)
            injected_count = 0

            # For each assistant message, ask LLM if it should have a tool call
            for i, msg in enumerate(new_messages):
                if msg.role == "assistant" and injected_count < 2:  # Max 2 tools per conversation
                    content = msg.content or ""

                    if strands_agent:
                        # Fast prompt: just ask which tool (if any)
                        tool_decision_prompt = f"""Given this assistant response, should it include a tool call?

Response: {content[:500]}

Available tools: {tool_list_str}

Answer with ONLY the tool name (e.g., "search_cve", "dns_lookup") or "NONE" if no tool needed. One word only."""

                        try:
                            result = strands_agent(
                                tool_decision_prompt,
                                params={"temperature": cfg.temperature},
                            )
                            tool_decision = (
                                (
                                    getattr(result, "text", None)
                                    or getattr(result, "content", None)
                                    or str(result)
                                )
                                .strip()
                                .split()[0]
                                .lower()
                            )
                        except Exception as e:
                            logger.debug(f"Tool decision failed: {e}. Using keyword fallback.")
                            tool_decision = "none"
                    else:
                        # Fallback: keyword matching
                        tool_decision = "none"
                        content_lower = content.lower()
                        for tool in cfg.tools:  # type: ignore
                            tool_name = tool.get("name", "").lower()  # type: ignore
                            if tool_name in content_lower:
                                tool_decision = tool_name
                                break

                    # Process tool decision
                    if tool_decision != "none":
                        # Find matching tool config
                        selected_tool = None
                        for tool in cfg.tools:  # type: ignore
                            if tool.get("name", "").lower() == tool_decision:  # type: ignore
                                selected_tool = tool
                                break

                        if selected_tool:
                            # Extract parameters from response content
                            params_spec = selected_tool.get("parameters", {})  # type: ignore
                            arguments: Dict[str, Any] = {}

                            for param_name in params_spec.keys():  # type: ignore
                                if param_name.lower() in ("keyword", "query", "search_term"):
                                    # Extract first few words
                                    words = content.split()[:3]
                                    arguments[param_name] = " ".join(words) if words else "security"
                                elif param_name.lower() in ("hostname", "domain"):
                                    arguments[param_name] = "example.com"
                                else:
                                    arguments[param_name] = ""

                            # Create and inject tool call
                            tool_call = ToolCall(
                                id=f"tc_{i}_{injected_count}",
                                name=selected_tool.get("name", "tool"),  # type: ignore
                                arguments=arguments or {},
                                status="requested",
                            )

                            existing_calls = list(msg.tool_calls or [])
                            existing_calls.append(tool_call)

                            new_messages[i] = Message(
                                role=msg.role,
                                content=msg.content,
                                metadata=msg.metadata,
                                tool_calls=existing_calls,
                            )

                            # Add synthetic tool response
                            tool_response = Message(
                                role="tool",
                                content=f"[Tool results from {selected_tool.get('name', 'tool')} - synthetic data]",  # type: ignore
                                tool_name=selected_tool.get("name", "tool"),  # type: ignore
                                tool_call_id=tool_call.id,
                            )
                            new_messages.insert(i + 1, tool_response)
                            injected_count += 1

            meta: Dict[str, Any] = {  # type: ignore
                **(rec.metadata or {}),
                "stage": "apigenmt",
                "agentic": True,
                "via": "hybrid",
                "tools_injected": injected_count,
                "provider": cfg.provider,
                "model": cfg.model_name,
            }
            yield ConversationRecord(
                messages=new_messages, metadata=meta, source=rec.source, id=rec.id
            )

        except Exception as e:
            logger.warning(f"APIGenMT hybrid failed for {rec.id}: {e}")
            meta: Dict[str, Any] = {  # type: ignore
                **(rec.metadata or {}),
                "stage": "apigenmt",
                "agentic": False,
                "via": "error",
            }
            yield ConversationRecord(
                messages=rec.messages, metadata=meta, source=rec.source, id=rec.id
            )
