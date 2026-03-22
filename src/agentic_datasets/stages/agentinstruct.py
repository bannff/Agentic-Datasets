"""AgentInstruct Stage: expand single-turn seeds into k diverse instruction variants.

This stage is intentionally provider-agnostic for now. It performs a lightweight,
rule-based fan-out that rewrites the first user message into several variants
with different emphases (examples, steps, pitfalls, summary, beginner-friendly, etc.).

Later, this can be upgraded to an LLM-backed variant generator (via Strands), but
the interface and metadata remain stable to keep downstream stages unchanged.

Outputs multiple ConversationRecord items for each input record (fan-out), each with:
- messages[0] rewritten (role=user)
- optional retention of original assistant reply if present
- metadata augmented with origin_id, variant_id, variant_prompt, dedupe_score
"""

from __future__ import annotations

from typing import Iterable, Iterator, List, Optional, Dict, Any
import hashlib

from ..schemas.messages import ConversationRecord, Message


def _normalize_text(s: str) -> str:
    return " ".join(s.lower().strip().split())


def _hash_text(s: str) -> str:
    return hashlib.sha256(_normalize_text(s).encode("utf-8")).hexdigest()[:16]


def _jaccard_diversity(a: str, b: str) -> float:
    """Simple token-set Jaccard distance as a diversity proxy (0..1)."""
    at = set(_normalize_text(a).split())
    bt = set(_normalize_text(b).split())
    if not at and not bt:
        return 0.0
    inter = len(at & bt)
    union = len(at | bt) or 1
    return 1.0 - (inter / union)


def _variant_templates(seed: str) -> List[str]:
    """Deterministic set of prompt variants applied to the seed instruction."""
    base = seed.strip()
    return [
        f"{base} Please include a small, practical example.",
        f"{base} Provide step-by-step guidance and common pitfalls.",
        f"{base} Summarize the key points concisely in bullet points.",
        f"{base} Explain it for a beginner with simple language.",
        f"{base} Focus on realistic scenarios and mitigations.",
        f"{base} Compare alternative approaches and when to use each.",
        f"{base} Include best practices and anti-patterns.",
    ]


def agentinstruct(
    records: Iterable[ConversationRecord],
    *,
    k_variants: int = 3,
    dedupe: bool = True,
    keep_top_n: Optional[int] = None,
) -> Iterator[ConversationRecord]:
    """Expand each record into k diverse instruction variants.

    Args:
        records: Input stream of ConversationRecord
        k_variants: Number of variants to attempt per input
        dedupe: Remove duplicate/similar variants (simple hash-based)
        keep_top_n: If set, keep only the top-N most diverse variants vs original

    Yields:
        ConversationRecord items, one per variant (fan-out)
    """

    k = max(1, int(k_variants))

    for rec in records:
        # Find first user message to serve as the seed
        user_idx = next((i for i, m in enumerate(rec.messages) if m.role == "user"), None)
        if user_idx is None:
            # No user message; pass through as-is
            yield rec
            continue

        seed = rec.messages[user_idx].content
        candidates = _variant_templates(seed)
        # Take the first k candidates deterministically
        candidates = candidates[:k]

        # Optionally dedupe by normalized hash
        unique: Dict[str, str] = {}
        for c in candidates:
            h = _hash_text(c)
            if not dedupe or h not in unique:
                unique[h] = c

        # Optionally select top-N by diversity against original seed
        selected: List[str]
        if keep_top_n is not None:
            scored = [(c, _jaccard_diversity(c, seed)) for c in unique.values()]
            scored.sort(key=lambda t: t[1], reverse=True)
            selected = [c for c, _ in scored[: max(1, int(keep_top_n))]]
        else:
            selected = list(unique.values())

        origin_id = rec.id

        for i, variant in enumerate(selected, start=1):
            # Rewrite first user message; keep the rest unchanged
            new_messages: List[Message] = []
            for idx, msg in enumerate(rec.messages):
                if idx == user_idx and msg.role == "user":
                    new_messages.append(Message(role="user", content=variant))
                else:
                    new_messages.append(msg)

            meta: Dict[str, Any] = dict(rec.metadata or {})
            meta.update(
                {
                    "stage": "agentinstruct",
                    "origin_id": origin_id,
                    "variant_id": f"v{i}",
                    "variant_prompt": variant,
                    "dedupe_score": _jaccard_diversity(variant, seed),
                }
            )

            yield ConversationRecord(
                messages=new_messages,
                id=(rec.id or "rec") + f"::v{i}",
                source=rec.source,
                metadata=meta,
            )
