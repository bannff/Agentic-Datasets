"""LLM Provider Abstraction Layer.

This module provides a unified interface for LLM providers using LiteLLM.
Configure once, use everywhere across all pipeline stages.

Supported providers:
- ollama/qwen3:8b (local, default)
- openai/gpt-4o, openai/gpt-4o-mini
- anthropic/claude-4-sonnet, anthropic/claude-4-opus
- bedrock/anthropic.claude-v2
- Together, Groq, Mistral, and 100+ other LiteLLM-supported providers

Usage:
    from agentic_datasets.llm import get_completion, LLMConfig

    # Use default (from env or ollama)
    response = get_completion("Explain SQL injection")

    # Or configure explicitly
    config = LLMConfig(model="openai/gpt-4o", temperature=0.7)
    response = get_completion("Explain SQL injection", config=config)
"""

from .provider import (
    LLMConfig,
    get_completion,
    get_completion_with_schema,
    get_default_config,
    set_default_config,
    validate_provider,
)

__all__ = [
    "LLMConfig",
    "get_completion",
    "get_completion_with_schema",
    "get_default_config",
    "set_default_config",
    "validate_provider",
]
