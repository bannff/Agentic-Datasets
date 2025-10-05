from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from datetime import datetime

from pydantic import BaseModel, Field, field_validator
from pydantic import ValidationInfo


Role = Literal["system", "user", "assistant", "tool"]


class ToolCall(BaseModel):
    id: Optional[str] = None
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    # Optional execution info if available
    status: Optional[Literal["requested", "completed", "failed"]] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    error: Optional[str] = None


class Message(BaseModel):
    role: Role
    content: str = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None
    # Assistant can request tool calls; tools can return outputs
    tool_calls: Optional[List[ToolCall]] = None
    tool_name: Optional[str] = None  # set when role == "tool"
    tool_call_id: Optional[str] = None  # correlates to assistant's tool_calls[].id
    tool_output: Optional[Dict[str, Any]] = None  # structured output from tool

    @field_validator("content")
    @classmethod
    def _strip_content(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("content cannot be empty after stripping")
        return s

    @field_validator("tool_name")
    @classmethod
    def _validate_tool_fields(cls, v: Optional[str], info: ValidationInfo):
        # If role is 'tool', require tool_name
        role = (info.data or {}).get("role")
        if role == "tool" and not v:
            raise ValueError("tool messages must include tool_name")
        return v


class ConversationRecord(BaseModel):
    messages: List[Message] = Field(..., min_length=1)
    id: Optional[str] = Field(None, description="Optional unique identifier")
    source: Optional[str] = Field(None, description="Dataset/source provenance")
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("messages")
    @classmethod
    def _validate_message_order(cls, v: List[Message]) -> List[Message]:
        # Light check: no two assistants in a row, no two users in a row.
        last_role: Optional[Role] = None
        for m in v:
            if last_role == m.role and m.role in ("user", "assistant"):
                raise ValueError("Consecutive messages with same conversational role are not allowed")
            last_role = m.role
        return v
