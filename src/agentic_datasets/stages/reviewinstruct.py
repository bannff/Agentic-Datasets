from __future__ import annotations

import importlib
import json
import os
from typing import Iterable, Iterator, Optional

from ..schemas.messages import ConversationRecord, Message
from ..agents.prompts import (
    CANDIDATE_SYSTEM_PROMPT,
    CHAIRMAN_SYSTEM_PROMPT,
    CHAIRMAN_USER_TEMPLATE,
    format_conversation_for_review,
)


class ReviewInstructConfig:
    def __init__(
        self,
        provider: str = "ollama",
        model_name: Optional[str] = None,
        max_iterations: int = 1,
        enabled: bool = True,
    ) -> None:
        self.provider = provider
        self.model_name = model_name or ("qwen3:8b" if provider == "ollama" else None)
        self.max_iterations = max(1, int(max_iterations))
        self.enabled = enabled


def reviewinstruct(
    records: Iterable[ConversationRecord], config: Optional[ReviewInstructConfig | dict] = None
) -> Iterator[ConversationRecord]:
    """ReviewInstruct: lightweight review-and-refine pass (Strands-first).

    Strategy:
    - Prefer a Strands Agent with Ollama model when available (dynamic import)
    - Ask a chairman to decide Accept vs Refine based on the current conversation
    - If Refine, ask candidate to produce a refined conversation (JSON array of messages)
    - Fallback: pass-through, set reviewed metadata
    """

    # Coerce config
    if config is None:
        cfg = ReviewInstructConfig()
    elif isinstance(config, dict):
        cfg = ReviewInstructConfig(**config)
    else:
        cfg = config

    if not cfg.enabled:
        for rec in records:
            yield rec
        return

    # Try to configure a Strands Agent with Ollama model if provider is ollama
    strands_agent = None
    if cfg.provider.lower() == "ollama":
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

    for rec in records:
        if strands_agent is None:
            # Fallback: mark reviewed, pass-through
            meta = {**(rec.metadata or {}), "stage": "reviewinstruct", "reviewed": True, "via": "fallback"}
            yield ConversationRecord(messages=rec.messages, metadata=meta, source=rec.source, id=rec.id)
            continue

        try:
            conv_text = format_conversation_for_review(rec.messages)

            # Ask chairman for decision
            chairman_user = CHAIRMAN_USER_TEMPLATE.format(
                conversation_id=rec.id or "unknown",
                quality_feedback="",
                safety_feedback="",
                diversity_feedback="",
                coherence_feedback="",
                iteration=1,
                max_iterations=cfg.max_iterations,
            )
            chairman_resp = strands_agent(chairman_user, system_prompt=CHAIRMAN_SYSTEM_PROMPT)
            chairman_text = getattr(chairman_resp, "text", None) or getattr(chairman_resp, "content", None) or str(
                chairman_resp
            )
            decision = _extract_decision(chairman_text)

            if decision == "refine" and cfg.max_iterations > 0:
                # Ask candidate to refine; include conversation for context and hints from chairman
                candidate_prompt = (
                    f"Conversation to refine:\n\n{conv_text}\n\n"
                    f"Chairman guidance:\n{chairman_text}\n\n"
                    "Return ONLY a JSON array of messages with fields role and content."
                )
                cand_resp = strands_agent(candidate_prompt, system_prompt=CANDIDATE_SYSTEM_PROMPT)
                cand_text = getattr(cand_resp, "text", None) or getattr(cand_resp, "content", None) or str(cand_resp)
                try:
                    msgs_data = json.loads(cand_text)
                    messages: list[Message] = []
                    for m in msgs_data:
                        role = m.get("role")
                        content = (m.get("content") or "").strip()
                        if not role or not content:
                            continue
                        messages.append(Message(role=role, content=content))
                    if messages:
                        yield ConversationRecord(
                            messages=messages,
                            metadata={
                                **(rec.metadata or {}),
                                "stage": "reviewinstruct",
                                "decision": "refine",
                                "via": "strands",
                                "model": cfg.model_name,
                            },
                            source=rec.source,
                            id=rec.id,
                        )
                        continue
                except Exception:
                    # Fall through to accept-as-is if parsing failed
                    pass

            # Accept path or failed refine parsing: pass-through with metadata
            meta = {
                **(rec.metadata or {}),
                "stage": "reviewinstruct",
                "decision": "accept" if decision == "accept" else "unknown",
                "via": "strands",
                "model": cfg.model_name,
            }
            yield ConversationRecord(messages=rec.messages, metadata=meta, source=rec.source, id=rec.id)
        except Exception:
            # Conservative fallback
            meta = {**(rec.metadata or {}), "stage": "reviewinstruct", "reviewed": True, "via": "fallback"}
            yield ConversationRecord(messages=rec.messages, metadata=meta, source=rec.source, id=rec.id)


def _extract_decision(text: str) -> str:
    t = text.strip().lower()
    if "decision:" in t:
        # find after 'decision:'
        try:
            part = t.split("decision:", 1)[1].strip()
            word = part.splitlines()[0].strip()
            if word.startswith("accept"):
                return "accept"
            if word.startswith("refine"):
                return "refine"
        except Exception:
            pass
    # heuristic
    if "accept" in t and "refine" not in t:
        return "accept"
    if "refine" in t:
        return "refine"
    return "unknown"
