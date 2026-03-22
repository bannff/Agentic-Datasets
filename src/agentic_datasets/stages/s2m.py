"""S2M Stage: Single-turn to Multi-turn Conversion.

This stage transforms single-turn Q&A pairs into coherent, natural multi-turn conversations
using Strands agents with specialized prompts.

Implementation Status:
- ✅ Infrastructure: Agent config, prompts, error handling
- ⚠️ Agent Integration: Requires strands-agents installation
- 🔴 LLM Calls: Requires model provider authentication

To enable full functionality:
1. Install: pip install strands-agents strands-agents-tools
2. Install provider: pip install boto3 (Bedrock) OR anthropic OR openai
3. Configure credentials (see agents.base.get_provider_setup_instructions)
4. Uncomment the async implementation below
"""

from __future__ import annotations

import logging
import os
import importlib
from typing import Iterable, Iterator, Optional

from ..schemas.messages import ConversationRecord, Message
from ..agents.prompts import S2M_SYSTEM_PROMPT, S2M_USER_TEMPLATE

logger = logging.getLogger(__name__)


class S2MConfig:
    """Configuration for S2M stage."""

    def __init__(
        self,
        provider: str = "ollama",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        min_turns: int = 3,
        max_turns: int = 5,
        enabled: bool = True,
    ):
        """Initialize S2M configuration.

        Args:
            provider: Model provider (ollama, bedrock, anthropic, openai)
            model_name: Specific model (uses provider default if None)
            temperature: Generation temperature (0.0-1.0)
            min_turns: Minimum conversation turns to generate
            max_turns: Maximum conversation turns to generate
            enabled: Whether S2M transformation is enabled
        """
        self.provider = provider
        self.model_name = model_name or ("qwen3:8b" if provider == "ollama" else None)
        self.temperature = temperature
        self.min_turns = min_turns
        self.max_turns = max_turns
        self.enabled = enabled


def s2m(
    records: Iterable[ConversationRecord],
    config: Optional[S2MConfig | dict] = None,
) -> Iterator[ConversationRecord]:
    """Convert single-turn Q&A pairs to multi-turn conversations.

    This stage:
    1. Detects single-turn conversations (user Q + assistant A)
    2. Uses Strands agent to generate natural follow-up turns
    3. Maintains context and domain focus across turns
    4. Validates generated conversations

    Current Status: PLACEHOLDER
    - Infrastructure ready (config, prompts, validation)
    - Requires strands-agents installation for full functionality
    - Falls back to pass-through if agent not available

    Args:
        records: Input conversation records
        config: S2M configuration (uses defaults if None)

    Yields:
        Multi-turn conversation records
    """
    # Allow YAML params to pass a raw dict; coerce into S2MConfig
    if config is None:
        cfg = S2MConfig()
    elif isinstance(config, dict):
        cfg = S2MConfig(**config)
    else:
        cfg = config

    if not cfg.enabled:
        logger.info("S2M stage disabled, passing through")
        yield from records
        return

    # Try Strands agent path first if available and provider is ollama; otherwise, use direct Ollama fallback
    use_ollama = cfg.provider.lower() == "ollama"
    ollama_client = None
    strands_agent = None
    if use_ollama:
        # Attempt to build a Strands Agent with Ollama model (dynamic import to avoid optional-deps lint errors)
        try:
            strands_module = importlib.import_module("strands")
            ollama_module = importlib.import_module("strands.models.ollama")

            Agent = getattr(strands_module, "Agent")
            OllamaModel = getattr(ollama_module, "OllamaModel")

            host = os.getenv("OLLAMA_HOST") or "http://localhost:11434"
            model = OllamaModel(host=host, model_id=cfg.model_name or "qwen3:8b")
            strands_agent = Agent(model=model)
        except Exception:
            strands_agent = None
    if use_ollama:
        try:
            from ollama import Client  # type: ignore

            host = os.getenv("OLLAMA_HOST")
            ollama_client = Client(host=host) if host else Client()
        except Exception as e:
            logger.warning(f"Ollama client unavailable: {e}. Falling back.")
            ollama_client = None

    for rec in records:
        # If already multi-turn, yield as-is
        if len(rec.messages) > 2:
            logger.debug(f"Record {rec.id} already multi-turn ({len(rec.messages)} messages)")
            yield rec
            continue

        # Check if single-turn Q&A structure
        if (
            len(rec.messages) == 2
            and rec.messages[0].role == "user"
            and rec.messages[1].role == "assistant"
        ):
            # Prefer Strands agent if available
            if strands_agent is not None:
                try:
                    user_q = rec.messages[0].content
                    assistant_a = rec.messages[1].content
                    prompt = S2M_USER_TEMPLATE.format(question=user_q, answer=assistant_a)
                    # Compose with system prompt
                    result = strands_agent(
                        prompt,
                        system_prompt=S2M_SYSTEM_PROMPT,
                        params={"temperature": max(0.0, min(1.0, cfg.temperature))},
                    )
                    # Expect JSON array of messages in result.text or result.content
                    text = (
                        getattr(result, "text", None)
                        or getattr(result, "content", None)
                        or str(result)
                    )
                    import json as _json

                    msgs_data = _json.loads(text)
                    messages: list[Message] = []
                    for m in msgs_data:
                        role = m.get("role")
                        content = m.get("content", "").strip()
                        if not role or not content:
                            continue
                        messages.append(Message(role=role, content=content))

                    # Ensure at least original + 2 new turns; otherwise fallback
                    if len(messages) >= 4:
                        yield ConversationRecord(
                            messages=messages,
                            metadata={
                                **(rec.metadata or {}),
                                "stage": "s2m",
                                "original_turns": 2,
                                "generated_turns": len(messages),
                                "provider": "ollama",
                                "model": cfg.model_name,
                                "via": "strands",
                            },
                            source=rec.source,
                            id=rec.id,
                        )
                        continue
                except Exception as e:
                    logger.warning(f"Strands S2M failed: {e}. Falling back for {rec.id}")

            if ollama_client is not None and cfg.model_name:
                # Attempt a minimal 2 extra turns generation via Ollama chat
                try:
                    user_q = rec.messages[0].content
                    assistant_a = rec.messages[1].content
                    prompt = (
                        "You are an expert conversational tutor. Given an initial user question and "
                        "assistant answer, propose ONE natural follow-up user question that deepens understanding.\n\n"
                        f"Q: {user_q}\nA: {assistant_a}\n\nReturn only the follow-up question."
                    )
                    q_resp = ollama_client.generate(
                        model=cfg.model_name,
                        prompt=prompt,
                        options={"temperature": max(0.0, min(1.0, cfg.temperature))},
                    )
                    followup_q = (q_resp.get("response") or "Could you give an example?").strip()

                    a_resp = ollama_client.generate(
                        model=cfg.model_name,
                        prompt=f"User asked: {followup_q}\nProvide a concise, accurate answer.",
                        options={"temperature": max(0.0, min(1.0, cfg.temperature))},
                    )
                    followup_a = (a_resp.get("response") or "[Answer]").strip()

                    out = ConversationRecord(
                        messages=[
                            rec.messages[0],
                            rec.messages[1],
                            Message(role="user", content=followup_q),
                            Message(role="assistant", content=followup_a),
                        ],
                        metadata={
                            **(rec.metadata or {}),
                            "stage": "s2m",
                            "original_turns": 2,
                            "generated_turns": 4,
                            "provider": "ollama",
                            "model": cfg.model_name,
                        },
                        source=rec.source,
                        id=rec.id,
                    )
                    yield out
                    continue
                except Exception as e:
                    logger.warning(f"Ollama generation failed: {e}. Falling back for {rec.id}")
                    yield _fallback_multiturn(rec)
            else:
                # Fallback: minimal placeholder
                logger.debug(f"No agent available, using fallback for {rec.id}")
                yield _fallback_multiturn(rec)

        elif len(rec.messages) == 1:
            # Single message - add minimal assistant response
            msg = rec.messages[0]
            if msg.role == "user":
                yield ConversationRecord(
                    messages=[
                        msg,
                        Message(
                            role="assistant",
                            content="[Multi-turn conversation would be generated here with Strands agent]",
                        ),
                    ],
                    metadata={**(rec.metadata or {}), "stage": "s2m", "generated": "fallback"},
                    source=rec.source,
                    id=rec.id,
                )
            else:
                yield rec
        else:
            # Unknown structure, pass through
            yield rec


def _fallback_multiturn(rec: ConversationRecord) -> ConversationRecord:
    """Fallback multi-turn generation without agent.

    Adds a simple follow-up question and answer as a placeholder.
    """
    # Simple follow-up (original messages are preserved in rec)
    followup_q = "Can you provide an example?"
    followup_a = "[Example would be provided here with actual agent implementation]"

    return ConversationRecord(
        messages=[
            rec.messages[0],  # Original user question
            rec.messages[1],  # Original assistant answer
            Message(role="user", content=followup_q),
            Message(role="assistant", content=followup_a),
        ],
        metadata={
            **(rec.metadata or {}),
            "stage": "s2m",
            "original_turns": 2,
            "generated_turns": 4,
            "generated": "fallback",
        },
        source=rec.source,
        id=rec.id,
    )


# TODO: Implement when strands-agents is installed
# async def _generate_multiturn(
#     rec: ConversationRecord,
#     agent: Any,  # Strands Agent type
#     config: S2MConfig,
# ) -> ConversationRecord:
#     """Generate multi-turn conversation using Strands agent.
#
#     Args:
#         rec: Input conversation record (single-turn Q&A)
#         agent: Configured Strands agent
#         config: S2M configuration
#
#     Returns:
#         Multi-turn conversation record
#     """
#     question = rec.messages[0].content
#     answer = rec.messages[1].content
#
#     # Format prompt
#     prompt = S2M_USER_TEMPLATE.format(
#         question=question,
#         answer=answer
#     )
#
#     # Generate with agent
#     try:
#         result = await agent.run(prompt)
#
#         # Parse JSON response
#         messages_data = json.loads(result.content)
#
#         # Validate message structure
#         messages = []
#         for msg_data in messages_data:
#             if "role" not in msg_data or "content" not in msg_data:
#                 logger.warning(f"Invalid message structure in response: {msg_data}")
#                 continue
#
#             messages.append(Message(
#                 role=msg_data["role"],
#                 content=msg_data["content"]
#             ))
#
#         # Validate turn count
#         if len(messages) < config.min_turns:
#             logger.warning(
#                 f"Generated conversation has {len(messages)} turns, "
#                 f"less than minimum {config.min_turns}"
#             )
#
#         if len(messages) > config.max_turns * 2:  # *2 for user+assistant pairs
#             logger.warning(
#                 f"Generated conversation has {len(messages)} turns, "
#                 f"more than maximum {config.max_turns * 2}"
#             )
#             messages = messages[:config.max_turns * 2]
#
#         return ConversationRecord(
#             messages=messages,
#             metadata={
#                 **rec.metadata,
#                 "stage": "s2m",
#                 "original_turns": len(rec.messages),
#                 "generated_turns": len(messages),
#                 "provider": config.provider,
#                 "model": config.model_name or "default",
#                 "temperature": config.temperature,
#             },
#             source=rec.source,
#             id=rec.id,
#         )
#
#     except json.JSONDecodeError as e:
#         logger.error(f"Failed to parse agent response as JSON: {e}")
#         logger.debug(f"Response content: {result.content}")
#         return _fallback_multiturn(rec)
#
#     except Exception as e:
#         logger.error(f"Error generating multi-turn conversation: {e}")
#         return _fallback_multiturn(rec)
