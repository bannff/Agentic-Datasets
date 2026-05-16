"""S2M Stage: Single-turn to Multi-turn Conversion using LLM.

Transforms single-turn Q&A pairs into coherent, natural multi-turn
conversations using LLM reasoning for high-quality expansion.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterable, Iterator, List, Optional

from ..llm import LLMConfig, get_completion, get_default_config
from ..llm.prompts import S2M_SYSTEM, S2M_TRANSFORM
from ..schemas.messages import ConversationRecord, Message

logger = logging.getLogger(__name__)


def _parse_messages_json(text: str) -> Optional[List[Dict[str, str]]]:
    """Parse JSON array of messages from LLM response.

    Handles cases where the model wraps JSON in markdown or prose.
    """
    text = text.strip()

    # Try direct parse first
    try:
        data: List[Dict[str, str]] = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # Try to extract JSON array from markdown code block
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end > start:
            try:
                return json.loads(text[start:end].strip())
            except json.JSONDecodeError:
                pass

    # Try to extract JSON array from plain code block
    if "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end > start:
            try:
                return json.loads(text[start:end].strip())
            except json.JSONDecodeError:
                pass

    # Try to find array brackets
    start = text.find("[")
    end = text.rfind("]")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    return None


def _generate_multiturn(
    question: str,
    answer: str,
    config: LLMConfig,
) -> Optional[List[Message]]:
    """Generate multi-turn conversation using LLM.

    Args:
        question: Original user question
        answer: Original assistant answer
        config: LLM configuration

    Returns:
        List of Message objects or None on failure
    """
    prompt = S2M_TRANSFORM.format(question=question, answer=answer)

    try:
        response = get_completion(
            prompt,
            system_prompt=S2M_SYSTEM,
            config=config,
            temperature=0.7,
            max_tokens=2048,
        )

        messages_data = _parse_messages_json(response)
        if not messages_data:
            logger.warning("Failed to parse S2M response as JSON")
            return None

        messages: List[Message] = []
        for m in messages_data:
            role = m.get("role", "").strip()
            content = m.get("content", "").strip()
            if role in ("user", "assistant", "system") and content:
                messages.append(Message(role=role, content=content))

        # Ensure we have at least 4 messages (2 turns)
        if len(messages) >= 4:
            return messages

        logger.warning(f"S2M generated only {len(messages)} messages, need at least 4")
        return None

    except Exception as e:
        logger.warning(f"S2M LLM generation failed: {e}")
        return None


def _fallback_multiturn(rec: ConversationRecord) -> ConversationRecord:
    """Fallback multi-turn generation without LLM.

    Adds a simple follow-up question and answer as a placeholder.
    """
    return ConversationRecord(
        messages=[
            rec.messages[0],
            rec.messages[1],
            Message(role="user", content="Can you provide an example?"),
            Message(
                role="assistant",
                content="[Example would be provided here with LLM generation enabled]",
            ),
        ],
        metadata={
            **(rec.metadata or {}),
            "stage": "s2m",
            "original_turns": 2,
            "generated_turns": 4,
            "via": "fallback",
        },
        source=rec.source,
        id=rec.id,
    )


def s2m(
    records: Iterable[ConversationRecord],
    *,
    min_turns: int = 4,
    max_turns: int = 10,
    use_llm: bool = True,
    llm_config: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,  # Legacy param
) -> Iterator[ConversationRecord]:
    """Convert single-turn Q&A pairs to multi-turn conversations.

    Uses LLM reasoning to generate natural, coherent follow-up turns
    that expand on the original topic.

    Args:
        records: Input conversation records
        min_turns: Minimum messages in output (default 4 = 2 turns)
        max_turns: Maximum messages in output
        use_llm: Whether to use LLM (False falls back to placeholder)
        llm_config: LLM configuration override
        config: Legacy config parameter (deprecated, use llm_config)

    Yields:
        Multi-turn conversation records
    """
    # Handle legacy config parameter
    if config and not llm_config:
        llm_config = config

    cfg = LLMConfig(**(llm_config or {})) if llm_config else get_default_config()

    logger.info(f"S2M: use_llm={use_llm}, min_turns={min_turns}")
    if use_llm:
        logger.info(f"Using LLM: {cfg.model}")

    for rec in records:
        # If already multi-turn, pass through
        if len(rec.messages) > 2:
            logger.debug(f"Record {rec.id} already multi-turn ({len(rec.messages)} messages)")
            yield rec
            continue

        # Check for single-turn Q&A structure
        if (
            len(rec.messages) == 2
            and rec.messages[0].role == "user"
            and rec.messages[1].role == "assistant"
        ):
            if use_llm:
                messages = _generate_multiturn(
                    rec.messages[0].content,
                    rec.messages[1].content,
                    cfg,
                )

                if messages:
                    # Truncate if too long
                    if len(messages) > max_turns:
                        messages = messages[:max_turns]

                    yield ConversationRecord(
                        messages=messages,
                        metadata={
                            **(rec.metadata or {}),
                            "stage": "s2m",
                            "original_turns": 2,
                            "generated_turns": len(messages),
                            "via": "llm",
                            "model": cfg.model,
                        },
                        source=rec.source,
                        id=rec.id,
                    )
                    continue

            # Fallback
            yield _fallback_multiturn(rec)

        elif len(rec.messages) == 1 and rec.messages[0].role == "user":
            # Single user message - add placeholder assistant response
            yield ConversationRecord(
                messages=[
                    rec.messages[0],
                    Message(
                        role="assistant", content="[Response would be generated with LLM enabled]"
                    ),
                ],
                metadata={
                    **(rec.metadata or {}),
                    "stage": "s2m",
                    "via": "fallback",
                },
                source=rec.source,
                id=rec.id,
            )
        else:
            # Unknown structure, pass through
            yield rec
