"""Agent utilities for Strands SDK integration.

This module provides:
- Agent configuration and factory functions
- Model provider setup and validation
- Stage-specific prompt templates
- Tool catalog parsing and management
"""

from .base import (
    AgentConfig,
    create_agent,
    validate_provider_credentials,
    get_provider_setup_instructions,
)

from .prompts import (
    S2M_SYSTEM_PROMPT,
    S2M_USER_TEMPLATE,
    APIGENMT_SYSTEM_PROMPT,
    APIGENMT_USER_TEMPLATE,
    CANDIDATE_SYSTEM_PROMPT,
    QUALITY_REVIEWER_SYSTEM_PROMPT,
    SAFETY_REVIEWER_SYSTEM_PROMPT,
    DIVERSITY_REVIEWER_SYSTEM_PROMPT,
    COHERENCE_REVIEWER_SYSTEM_PROMPT,
    CHAIRMAN_SYSTEM_PROMPT,
    CHAIRMAN_USER_TEMPLATE,
    format_conversation_for_review,
    format_tools_catalog,
)

__all__ = [
    "AgentConfig",
    "create_agent",
    "validate_provider_credentials",
    "get_provider_setup_instructions",
    "S2M_SYSTEM_PROMPT",
    "S2M_USER_TEMPLATE",
    "APIGENMT_SYSTEM_PROMPT",
    "APIGENMT_USER_TEMPLATE",
    "CANDIDATE_SYSTEM_PROMPT",
    "QUALITY_REVIEWER_SYSTEM_PROMPT",
    "SAFETY_REVIEWER_SYSTEM_PROMPT",
    "DIVERSITY_REVIEWER_SYSTEM_PROMPT",
    "COHERENCE_REVIEWER_SYSTEM_PROMPT",
    "CHAIRMAN_SYSTEM_PROMPT",
    "CHAIRMAN_USER_TEMPLATE",
    "format_conversation_for_review",
    "format_tools_catalog",
]
