"""ReviewInstruct Stage: LLM-powered multi-agent review.

Uses LLM reasoning to evaluate conversations and optionally refine them
based on quality, accuracy, and usefulness criteria.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterable, Iterator, List, Optional

from ..llm import LLMConfig, get_completion, get_default_config
from ..llm.prompts import CHAIRMAN_SYSTEM, CHAIRMAN_REVIEW, REFINER_SYSTEM, REFINER_IMPROVE
from ..schemas.messages import ConversationRecord, Message

logger = logging.getLogger(__name__)


def _format_conversation(messages: List[Message]) -> str:
    """Format messages for review."""
    lines: List[str] = []
    for msg in messages:
        role = msg.role.upper()
        content = msg.content

        if msg.tool_calls:
            tools = ", ".join(tc.name for tc in msg.tool_calls)
            lines.append(f"{role}: {content}\n  [Calls: {tools}]")
        elif msg.role == "tool":
            lines.append(f"TOOL ({msg.tool_name}): {content}")
        else:
            lines.append(f"{role}: {content}")

    return "\n\n".join(lines)


def _parse_review(text: str) -> Optional[Dict[str, Any]]:
    """Parse review JSON from LLM response."""
    text = text.strip()

    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract from code blocks
    for marker in ["```json", "```"]:
        if marker in text:
            start = text.find(marker) + len(marker)
            end = text.find("```", start)
            if end > start:
                try:
                    return json.loads(text[start:end].strip())
                except json.JSONDecodeError:
                    pass

    # Try to find JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass

    return None


def _parse_messages(text: str) -> Optional[List[Dict[str, str]]]:
    """Parse messages JSON from refiner response."""
    text = text.strip()

    # Try direct parse
    try:
        data: List[Dict[str, str]] = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # Try to extract from code blocks
    for marker in ["```json", "```"]:
        if marker in text:
            start = text.find(marker) + len(marker)
            end = text.find("```", start)
            if end > start:
                try:
                    data = json.loads(text[start:end].strip())
                    if isinstance(data, list):
                        return data
                except json.JSONDecodeError:
                    pass

    # Try to find array
    start = text.find("[")
    end = text.rfind("]")
    if start >= 0 and end > start:
        try:
            data = json.loads(text[start : end + 1])
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

    return None


def _review_conversation(
    messages: List[Message],
    config: LLMConfig,
) -> Dict[str, Any]:
    """Get quality review from LLM chairman.

    Returns:
        Dict with decision, scores, strengths, issues, guidance
    """
    conversation = _format_conversation(messages)

    prompt = CHAIRMAN_REVIEW.format(conversation=conversation)

    try:
        response = get_completion(
            prompt,
            system_prompt=CHAIRMAN_SYSTEM,
            config=config,
            temperature=0.3,  # Lower for consistent judgment
            max_tokens=1024,
        )

        review = _parse_review(response)
        if review and "decision" in review:
            return review

        # Default to accept if parsing fails
        return {"decision": "accept", "overall_score": 3, "issues": ["Parse failed"]}

    except Exception as e:
        logger.warning(f"Review failed: {e}")
        return {"decision": "accept", "overall_score": 3, "issues": [str(e)]}


def _refine_conversation(
    messages: List[Message],
    feedback: Dict[str, Any],
    config: LLMConfig,
) -> Optional[List[Message]]:
    """Refine conversation based on review feedback.

    Returns:
        List of improved Message objects or None on failure
    """
    conversation = _format_conversation(messages)

    issues = feedback.get("issues", [])
    guidance = feedback.get("refinement_guidance", "Improve clarity and completeness")

    prompt = REFINER_IMPROVE.format(
        conversation=conversation,
        feedback=json.dumps(issues),
        guidance=guidance,
    )

    try:
        response = get_completion(
            prompt,
            system_prompt=REFINER_SYSTEM,
            config=config,
            temperature=0.6,
            max_tokens=2048,
        )

        messages_data = _parse_messages(response)
        if not messages_data:
            return None

        result: List[Message] = []
        for m in messages_data:
            role = m.get("role", "").strip()
            content = m.get("content", "").strip()
            if role in ("user", "assistant", "system", "tool") and content:
                result.append(Message(role=role, content=content))

        if len(result) >= 2:
            return result
        return None

    except Exception as e:
        logger.warning(f"Refinement failed: {e}")
        return None


def reviewinstruct(
    records: Iterable[ConversationRecord],
    *,
    accept_threshold: float = 3.5,
    max_iterations: int = 2,
    use_llm: bool = True,
    llm_config: Optional[Dict[str, Any]] = None,
    config: Optional[Dict[str, Any]] = None,  # Legacy
) -> Iterator[ConversationRecord]:
    """Review and optionally refine conversations using LLM.

    Uses a chairman agent to evaluate quality, and a refiner agent
    to improve conversations that don't meet the quality threshold.

    Args:
        records: Input conversation records
        accept_threshold: Minimum score to accept (1-5 scale, default 3.5)
        max_iterations: Maximum refinement attempts
        use_llm: Whether to use LLM (False = pass through)
        llm_config: LLM configuration override
        config: Legacy config parameter

    Yields:
        Reviewed (and possibly refined) conversation records
    """
    # Handle legacy config
    if config and not llm_config:
        llm_config = config

    cfg = LLMConfig(**(llm_config or {})) if llm_config else get_default_config()

    logger.info(f"ReviewInstruct: threshold={accept_threshold}, max_iter={max_iterations}")
    if use_llm:
        logger.info(f"Using LLM: {cfg.model}")

    for rec in records:
        if not use_llm:
            disabled_meta: Dict[str, Any] = dict(rec.metadata or {})
            disabled_meta.update(
                {
                    "stage": "reviewinstruct",
                    "reviewed": False,
                    "via": "disabled",
                }
            )
            yield ConversationRecord(
                messages=rec.messages,
                metadata=disabled_meta,
                source=rec.source,
                id=rec.id,
            )
            continue

        try:
            current_messages = rec.messages
            review: Optional[Dict[str, Any]] = None
            iteration = 0

            while iteration < max_iterations:
                # Get review
                review = _review_conversation(current_messages, cfg)

                score = review.get("overall_score", 3)
                decision = review.get("decision", "accept")

                # Check if acceptable
                if decision == "accept" or score >= accept_threshold:
                    break

                # Try to refine
                refined = _refine_conversation(current_messages, review, cfg)
                if refined:
                    current_messages = refined
                    iteration += 1
                else:
                    # Refinement failed, accept as-is
                    break

            success_meta: Dict[str, Any] = dict(rec.metadata or {})
            success_meta.update(
                {
                    "stage": "reviewinstruct",
                    "reviewed": True,
                    "via": "llm",
                    "model": cfg.model,
                    "decision": review.get("decision", "accept") if review else "accept",
                    "score": review.get("overall_score", 3) if review else 3,
                    "iterations": iteration,
                }
            )

            yield ConversationRecord(
                messages=current_messages,
                metadata=success_meta,
                source=rec.source,
                id=rec.id,
            )

        except Exception as e:
            logger.warning(f"ReviewInstruct failed for {rec.id}: {e}")
            error_meta: Dict[str, Any] = dict(rec.metadata or {})
            error_meta.update(
                {
                    "stage": "reviewinstruct",
                    "reviewed": False,
                    "via": "error",
                }
            )
            yield ConversationRecord(
                messages=rec.messages,
                metadata=error_meta,
                source=rec.source,
                id=rec.id,
            )
