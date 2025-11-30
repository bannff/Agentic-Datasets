"""Unified LLM Provider using LiteLLM.

LiteLLM provides a unified interface to 100+ LLM providers.
This module wraps it with sensible defaults and error handling.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Optional, Type, TypeVar

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Type variable for Pydantic models (must be bound to BaseModel)
_T = TypeVar("_T", bound=BaseModel)

# Global default config - can be set once at startup
_default_config: Optional[LLMConfig] = None


@dataclass
class LLMConfig:
    """Configuration for LLM provider.
    
    Model format follows LiteLLM convention: "provider/model_name"
    Examples:
        - "ollama/qwen3:8b" (local Ollama)
        - "openai/gpt-4o" (OpenAI)
        - "anthropic/claude-4-sonnet-20250514" (Anthropic)
        - "bedrock/anthropic.claude-v2" (AWS Bedrock)
        - "together_ai/mistralai/Mixtral-8x7B" (Together AI)
    
    LiteLLM Best Practices Applied:
        - num_retries: Automatic retry on transient failures (default: 2)
        - fallbacks: List of backup models if primary fails
        - timeout: Prevent hanging requests (default: 120s)
    """
    
    model: str = field(default_factory=lambda: os.getenv(
        "AGENTIC_LLM_MODEL", "ollama/qwen3:8b"
    ))
    temperature: float = 0.7
    max_tokens: int = 4096
    api_base: Optional[str] = None  # Override for custom endpoints
    timeout: int = 120
    num_retries: int = 2  # LiteLLM best practice: retry on transient failures
    fallbacks: Optional[list[str]] = None  # Backup models if primary fails
    
    def __post_init__(self) -> None:
        # Auto-detect Ollama host
        if self.model.startswith("ollama/") and self.api_base is None:
            self.api_base = os.getenv("OLLAMA_HOST", "http://localhost:11434")


def get_default_config() -> LLMConfig:
    """Get the default LLM configuration."""
    global _default_config
    if _default_config is None:
        _default_config = LLMConfig()
    return _default_config


def set_default_config(config: LLMConfig) -> None:
    """Set the default LLM configuration for all stages."""
    global _default_config
    _default_config = config


def validate_provider(config: Optional[LLMConfig] = None) -> dict[str, Any]:
    """Validate that the configured provider is accessible.
    
    Returns:
        Dict with 'ok' bool and 'message' or 'error' string
    """
    cfg = config or get_default_config()
    
    try:
        response = get_completion(
            "Say 'ok' and nothing else.",
            config=cfg,
            max_tokens=10
        )
        return {"ok": True, "message": f"Provider {cfg.model} is accessible", "response": response}
    except Exception as e:
        return {"ok": False, "error": str(e), "model": cfg.model}


def get_completion(
    prompt: str,
    *,
    system_prompt: Optional[str] = None,
    config: Optional[LLMConfig] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    response_format: Optional[dict[str, Any]] = None,
) -> str:
    """Get a completion from the configured LLM.
    
    Args:
        prompt: The user prompt
        system_prompt: Optional system prompt
        config: LLM configuration (uses default if not provided)
        max_tokens: Override max tokens
        temperature: Override temperature
        response_format: Optional response format (e.g., {"type": "json_object"})
    
    Returns:
        The LLM response text
    
    Raises:
        ImportError: If litellm is not installed
        Exception: If LLM call fails
    """
    try:
        import litellm  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError(
            "LiteLLM is required for LLM operations. Install with: pip install litellm"
        ) from e
    
    cfg = config or get_default_config()
    
    # Build messages
    messages: list[dict[str, str]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    # Build kwargs
    kwargs: dict[str, Any] = {
        "model": cfg.model,
        "messages": messages,
        "temperature": temperature if temperature is not None else cfg.temperature,
        "max_tokens": max_tokens if max_tokens is not None else cfg.max_tokens,
        "timeout": cfg.timeout,
        "num_retries": cfg.num_retries,  # LiteLLM built-in retry
    }
    
    # Add api_base for Ollama or custom endpoints
    if cfg.api_base:
        kwargs["api_base"] = cfg.api_base
    
    # Add fallback models if configured (LiteLLM best practice)
    if cfg.fallbacks:
        kwargs["fallbacks"] = cfg.fallbacks
    
    # Add response format if requested
    if response_format:
        kwargs["response_format"] = response_format
    
    # Suppress litellm's verbose logging
    litellm.suppress_debug_info = True  # type: ignore[attr-defined]
    
    try:
        response: Any = litellm.completion(**kwargs)  # type: ignore[attr-defined]
        # Extract content from response (type: ignore due to dynamic litellm types)
        content = str(response.choices[0].message.content or "")  # type: ignore[union-attr]
        return content
    except Exception as e:
        logger.error(f"LLM completion failed: {e}")
        raise


def get_completion_with_schema(
    prompt: str,
    schema: Type[_T],
    *,
    system_prompt: Optional[str] = None,
    config: Optional[LLMConfig] = None,
    max_retries: int = 2,
) -> _T:
    """Get a structured completion that validates against a Pydantic schema.
    
    Args:
        prompt: The user prompt
        schema: Pydantic model class to validate response against
        system_prompt: Optional system prompt
        config: LLM configuration
        max_retries: Number of retries on parse failure
    
    Returns:
        Validated Pydantic model instance
    
    Raises:
        ValueError: If response cannot be parsed after retries
    """
    cfg = config or get_default_config()
    
    # Add JSON instruction to system prompt
    schema_json: dict[str, Any] = schema.model_json_schema()
    json_instruction = f"\n\nRespond with valid JSON matching this schema:\n{json.dumps(schema_json, indent=2)}"
    
    full_system = (system_prompt or "") + json_instruction
    
    for attempt in range(max_retries + 1):
        try:
            response = get_completion(
                prompt,
                system_prompt=full_system,
                config=cfg,
                response_format={"type": "json_object"}
            )
            
            # Parse and validate
            data = json.loads(response)
            return schema.model_validate(data)
            
        except json.JSONDecodeError as e:
            if attempt == max_retries:
                raise ValueError(f"Failed to parse JSON after {max_retries + 1} attempts: {e}")
            logger.warning(f"JSON parse error (attempt {attempt + 1}): {e}")
            
        except Exception as e:
            if attempt == max_retries:
                raise ValueError(f"Schema validation failed after {max_retries + 1} attempts: {e}")
            logger.warning(f"Validation error (attempt {attempt + 1}): {e}")
    
    raise ValueError("Unexpected error in get_completion_with_schema")
