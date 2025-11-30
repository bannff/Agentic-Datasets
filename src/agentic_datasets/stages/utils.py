"""Shared utilities for LLM-powered stages.

This module extracts common patterns from the v2 stages to reduce duplication:
- JSON parsing from LLM responses
- LLM config initialization with legacy support
- Conversation formatting for prompts
- Metadata update helpers
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional, TypeVar, Union

from ..llm import LLMConfig, get_default_config
from ..schemas.messages import ConversationRecord, Message

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ─────────────────────────────────────────────────────────────────────────────
# LLM Config Handling
# ─────────────────────────────────────────────────────────────────────────────


def create_llm_config(
    llm_config: Optional[Dict[str, Any]] = None,
    legacy_config: Optional[Dict[str, Any]] = None,
) -> LLMConfig:
    """Create LLMConfig with legacy parameter support.
    
    Args:
        llm_config: Primary config dict
        legacy_config: Deprecated config dict (fallback if llm_config is None)
    
    Returns:
        LLMConfig instance
    """
    if legacy_config and not llm_config:
        llm_config = legacy_config
    return LLMConfig(**(llm_config or {})) if llm_config else get_default_config()


# ─────────────────────────────────────────────────────────────────────────────
# JSON Parsing from LLM Responses
# ─────────────────────────────────────────────────────────────────────────────


def parse_json_from_response(
    text: str,
    expected_type: str = "object",
    default: Optional[T] = None,  # type: ignore[type-var]
) -> Union[Dict[str, Any], List[Any], T]:
    """Extract JSON from an LLM response that may contain markdown.
    
    Handles common LLM output patterns:
    - ```json ... ``` code blocks
    - ``` ... ``` generic code blocks
    - Raw JSON strings
    
    Args:
        text: Raw LLM response text
        expected_type: "object" for dict, "array" for list
        default: Value to return on parse failure
    
    Returns:
        Parsed JSON or default value
    """
    if not text:
        return default if default is not None else ({} if expected_type == "object" else [])  # type: ignore[return-value]
    
    # Try markdown JSON block first
    json_match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try generic code block
    code_match = re.search(r"```\s*([\s\S]*?)\s*```", text)
    if code_match:
        try:
            return json.loads(code_match.group(1))
        except json.JSONDecodeError:
            pass
    
    # Try raw JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    
    # Return default
    return default if default is not None else ({} if expected_type == "object" else [])  # type: ignore[return-value]


def parse_json_object(text: str) -> Dict[str, Any]:
    """Parse JSON object from LLM response."""
    result = parse_json_from_response(text, expected_type="object", default={})
    return result if isinstance(result, dict) else {}


def parse_json_array(text: str) -> List[Any]:
    """Parse JSON array from LLM response."""
    result = parse_json_from_response(text, expected_type="array", default=[])
    return result if isinstance(result, list) else []


# ─────────────────────────────────────────────────────────────────────────────
# Conversation Formatting
# ─────────────────────────────────────────────────────────────────────────────


def format_messages_for_prompt(
    messages: List[Message],
    include_tool_calls: bool = False,
    max_messages: Optional[int] = None,
) -> str:
    """Format conversation messages for use in a prompt.
    
    Args:
        messages: List of Message objects
        include_tool_calls: Whether to include tool call information
        max_messages: Maximum number of messages to include (None = all)
    
    Returns:
        Formatted string representation
    """
    lines: List[str] = []
    msgs = messages[:max_messages] if max_messages else messages
    
    for msg in msgs:
        role = msg.role.upper()
        content = msg.content or ""
        
        if include_tool_calls and msg.tool_calls:
            tool_names: List[str] = [tc.name for tc in msg.tool_calls]
            tool_info = ", ".join(tool_names)
            lines.append(f"{role} (tools: {tool_info}): {content}")
        else:
            lines.append(f"{role}: {content}")
    
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Metadata Helpers
# ─────────────────────────────────────────────────────────────────────────────


def update_record_metadata(
    record: ConversationRecord,
    stage_name: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Create updated metadata dict for a record.
    
    Args:
        record: Source conversation record
        stage_name: Name of the processing stage
        **kwargs: Additional metadata fields
    
    Returns:
        New metadata dict (does not modify original)
    """
    meta: Dict[str, Any] = dict(record.metadata or {})
    meta["stage"] = stage_name
    meta.update(kwargs)
    return meta


def create_passthrough_record(
    record: ConversationRecord,
    stage_name: str,
    via: str = "passthrough",
    **extra_meta: Any,
) -> ConversationRecord:
    """Create a passthrough copy of a record with stage metadata.
    
    Use when a record should pass through unchanged but with tracking info.
    
    Args:
        record: Source record
        stage_name: Name of the stage
        via: Processing method indicator
        **extra_meta: Additional metadata
    
    Returns:
        New ConversationRecord with updated metadata
    """
    meta = update_record_metadata(record, stage_name, via=via, **extra_meta)
    return ConversationRecord(
        messages=record.messages,
        id=record.id,
        source=record.source,
        metadata=meta,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Constants for Stage Configuration
# ─────────────────────────────────────────────────────────────────────────────


class StageDefaults:
    """Default configuration values for stages.
    
    Centralizes magic numbers and default settings.
    """
    # Temperature settings by task type
    TEMPERATURE_CREATIVE = 0.8  # High diversity (agentinstruct variants)
    TEMPERATURE_BALANCED = 0.7  # Moderate (multi-turn expansion)
    TEMPERATURE_FOCUSED = 0.5  # Lower variance (tool injection)
    TEMPERATURE_PRECISE = 0.3  # Minimal variance (review/validation)
    
    # Token limits
    MAX_TOKENS_SHORT = 256   # Brief responses
    MAX_TOKENS_MEDIUM = 512  # Standard responses
    MAX_TOKENS_LONG = 1024   # Detailed responses
    MAX_TOKENS_MULTI = 2048  # Multi-turn conversations
    
    # Processing thresholds
    MIN_CONTENT_LENGTH = 10      # Minimum chars for meaningful content
    MAX_TOOL_CALLS_PER_MSG = 2   # Maximum tool calls to inject per message
    DIVERSITY_THRESHOLD = 0.3   # Minimum Jaccard diversity for dedup
