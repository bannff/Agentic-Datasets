"""APIGenMT Stage: LLM-powered semantic tool injection.

Uses LLM reasoning to identify where tool calls would genuinely help
in a conversation and inject them naturally following APIGen methodology.

Key improvements over keyword matching:
- LLM analyzes conversation semantics to determine tool relevance
- Parameters are extracted contextually, not via pattern matching
- Tool responses are generated to be realistic and helpful
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterable, Iterator, List, Optional

from ..llm import LLMConfig, get_completion, get_default_config
from ..llm.prompts import APIGENMT_SYSTEM, APIGENMT_ANALYZE, APIGENMT_GENERATE_RESPONSE
from ..schemas.messages import ConversationRecord, Message, ToolCall

logger = logging.getLogger(__name__)


def _format_conversation(messages: List[Message]) -> str:
    """Format messages for inclusion in prompts."""
    lines: List[str] = []
    for i, msg in enumerate(messages):
        lines.append(f"[{i}] {msg.role.upper()}: {msg.content}")
    return "\n".join(lines)


def _format_tools_catalog(tools: List[Dict[str, Any]]) -> str:
    """Format tools catalog for inclusion in prompts."""
    lines: List[str] = []
    for tool in tools:
        name = tool.get("name", "unknown")
        desc = tool.get("description", "")
        params = tool.get("parameters", {})

        lines.append(f"- {name}: {desc}")
        if params:
            param_strs: List[str] = []
            for pname, pinfo in params.items():
                ptype = pinfo.get("type", "string")
                required = " (required)" if pinfo.get("required") else ""
                param_strs.append(f"    {pname}: {ptype}{required}")
            lines.extend(param_strs)

    return "\n".join(lines)


def _parse_tool_analysis(text: str) -> Optional[Dict[str, Any]]:
    """Parse tool analysis JSON from LLM response."""
    text = text.strip()

    # Try direct parse
    try:
        data: Dict[str, Any] = json.loads(text)
        if isinstance(data, dict) and "tool_calls" in data:
            return data
    except json.JSONDecodeError:
        pass

    # Try to extract JSON from code blocks
    for marker in ["```json", "```"]:
        if marker in text:
            start = text.find(marker) + len(marker)
            end = text.find("```", start)
            if end > start:
                try:
                    data = json.loads(text[start:end].strip())
                    if isinstance(data, dict) and "tool_calls" in data:
                        return data
                except json.JSONDecodeError:
                    pass

    # Try to find JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            data = json.loads(text[start : end + 1])
            if isinstance(data, dict) and "tool_calls" in data:
                return data
        except json.JSONDecodeError:
            pass

    return None


def _analyze_for_tools(
    messages: List[Message],
    tools: List[Dict[str, Any]],
    config: LLMConfig,
) -> List[Dict[str, Any]]:
    """Use LLM to analyze conversation and identify tool injection points.

    Returns:
        List of tool call specifications with:
        - after_message_index: Which message to inject after
        - tool_name: Name of the tool
        - arguments: Dict of parameters
        - reasoning: Why this tool is relevant
    """
    conversation = _format_conversation(messages)
    tools_catalog = _format_tools_catalog(tools)

    prompt = APIGENMT_ANALYZE.format(
        conversation=conversation,
        tools=tools_catalog,
    )

    try:
        response = get_completion(
            prompt,
            system_prompt=APIGENMT_SYSTEM,
            config=config,
            temperature=0.5,  # Lower for more consistent analysis
            max_tokens=1024,
        )

        analysis = _parse_tool_analysis(response)
        if analysis and "tool_calls" in analysis:
            return analysis["tool_calls"]

        logger.warning("Failed to parse tool analysis response")
        return []

    except Exception as e:
        logger.warning(f"Tool analysis failed: {e}")
        return []


def _generate_tool_response(
    tool_name: str,
    arguments: Dict[str, Any],
    tool_desc: str,
    config: LLMConfig,
) -> str:
    """Generate a realistic tool response using LLM."""
    prompt = APIGENMT_GENERATE_RESPONSE.format(
        tool_name=tool_name,
        arguments=json.dumps(arguments),
        description=tool_desc,
    )

    try:
        response = get_completion(
            prompt,
            config=config,
            temperature=0.6,
            max_tokens=512,
        )
        return response.strip()
    except Exception as e:
        logger.warning(f"Tool response generation failed: {e}")
        return f"[{tool_name} result for {arguments}]"


def apigenmt(
    records: Iterable[ConversationRecord],
    *,
    tools: Optional[List[Dict[str, Any]]] = None,
    max_tools_per_conversation: int = 3,
    use_llm: bool = True,
    generate_responses: bool = True,
    llm_config: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,  # Legacy
) -> Iterator[ConversationRecord]:
    """Inject tool calls into conversations using LLM semantic analysis.

    Uses LLM reasoning to determine where tool calls would genuinely help,
    rather than simple keyword matching.

    Args:
        records: Input conversation records
        tools: List of tool definitions with name, description, parameters
        max_tools_per_conversation: Maximum tool calls to inject
        use_llm: Whether to use LLM for analysis (False = pass through)
        generate_responses: Whether to generate realistic tool responses
        llm_config: LLM configuration override
        config: Legacy config parameter

    Yields:
        Conversations with tool calls injected
    """
    # Handle legacy config
    if config and not llm_config:
        llm_config = config

    cfg = LLMConfig(**(llm_config or {})) if llm_config else get_default_config()

    if not tools:
        logger.info("APIGenMT: No tools configured, passing through")
        for rec in records:
            meta: Dict[str, Any] = dict(rec.metadata or {})
            meta.update({"stage": "apigenmt", "agentic": False})
            yield ConversationRecord(
                messages=rec.messages,
                metadata=meta,
                source=rec.source,
                id=rec.id,
            )
        return

    # Build tool description lookup
    tool_descs: Dict[str, str] = {t.get("name", ""): t.get("description", "") for t in tools}

    logger.info(f"APIGenMT: {len(tools)} tools, use_llm={use_llm}")
    if use_llm:
        logger.info(f"Using LLM: {cfg.model}")

    for rec in records:
        if not use_llm:
            # Pass through without tool injection
            meta: Dict[str, Any] = dict(rec.metadata or {})
            meta.update({"stage": "apigenmt", "agentic": False, "via": "disabled"})
            yield ConversationRecord(
                messages=rec.messages,
                metadata=meta,
                source=rec.source,
                id=rec.id,
            )
            continue

        try:
            # Analyze conversation for tool injection points
            tool_calls_spec = _analyze_for_tools(rec.messages, tools, cfg)

            if not tool_calls_spec:
                # No tools needed
                no_tools_meta: Dict[str, Any] = dict(rec.metadata or {})
                no_tools_meta.update({"stage": "apigenmt", "agentic": False, "via": "llm_no_tools"})
                yield ConversationRecord(
                    messages=rec.messages,
                    metadata=no_tools_meta,
                    source=rec.source,
                    id=rec.id,
                )
                continue

            # Limit tool calls
            tool_calls_spec = tool_calls_spec[:max_tools_per_conversation]

            # Build new message list with injected tool calls
            new_messages: List[Message] = list(rec.messages)
            injected_count = 0

            # Sort by index descending to insert from end (prevents index shift issues)
            tool_calls_spec.sort(key=lambda x: x.get("after_message_index", 0), reverse=True)

            for spec in tool_calls_spec:
                idx: int = spec.get("after_message_index", 0)
                tool_name: str = spec.get("tool_name", "")
                arguments: Dict[str, Any] = spec.get("arguments", {})

                if idx < 0 or idx >= len(new_messages):
                    continue

                msg: Message = new_messages[idx]

                # Check if this is an assistant message
                if msg.role != "assistant":
                    continue

                # Create tool call
                tool_call = ToolCall(
                    id=f"tc_{rec.id}_{injected_count}",
                    name=tool_name,
                    arguments=arguments,
                    status="completed",
                )

                # Add tool call to the assistant message
                existing_calls: List[ToolCall] = list(msg.tool_calls or [])
                existing_calls.append(tool_call)
                new_messages[idx] = Message(
                    role=msg.role,
                    content=msg.content,
                    metadata=msg.metadata,
                    tool_calls=existing_calls,
                )

                # Generate and insert tool response
                if generate_responses:
                    tool_response_content = _generate_tool_response(
                        tool_name,
                        arguments,
                        tool_descs.get(tool_name, ""),
                        cfg,
                    )
                else:
                    tool_response_content = f"[{tool_name} result]"

                tool_response = Message(
                    role="tool",
                    content=tool_response_content,
                    tool_name=tool_name,
                    tool_call_id=tool_call.id,
                )
                new_messages.insert(idx + 1, tool_response)
                injected_count += 1

            meta: Dict[str, Any] = dict(rec.metadata or {})
            meta.update(
                {
                    "stage": "apigenmt",
                    "agentic": True,
                    "via": "llm",
                    "model": cfg.model,
                    "tools_injected": injected_count,
                }
            )

            yield ConversationRecord(
                messages=new_messages,
                metadata=meta,
                source=rec.source,
                id=rec.id,
            )

        except Exception as e:
            logger.warning(f"APIGenMT failed for {rec.id}: {e}")
            meta_err: Dict[str, Any] = dict(rec.metadata or {})
            meta_err.update({"stage": "apigenmt", "agentic": False, "via": "error"})
            yield ConversationRecord(
                messages=rec.messages,
                metadata=meta_err,
                source=rec.source,
                id=rec.id,
            )
