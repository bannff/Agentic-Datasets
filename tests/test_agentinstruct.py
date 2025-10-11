from __future__ import annotations

from typing import List

from agentic_datasets.schemas.messages import ConversationRecord, Message
from agentic_datasets.stages.agentinstruct import agentinstruct


def _make_single_turn(seed: str = "Explain SQL injection") -> ConversationRecord:
    return ConversationRecord(
        id="rec-1",
        source="unit-test",
        messages=[
            Message(role="user", content=seed),
            Message(role="assistant", content="It is a class of injection attacks ..."),
        ],
    )


def test_agentinstruct_fan_out_basic():
    rec = _make_single_turn()
    out: List[ConversationRecord] = list(agentinstruct([rec], k_variants=3))
    assert len(out) == 3
    # All outputs should start with a user message variant
    for i, r in enumerate(out, start=1):
        assert r.messages[0].role == "user"
        assert r.metadata and r.metadata.get("stage") == "agentinstruct"
        assert r.metadata.get("variant_id") == f"v{i}"


def test_agentinstruct_dedupe_and_keep_top_n():
    rec = _make_single_turn("What is XSS and how to prevent it?")
    # Request many variants but keep only top 2 diverse
    out: List[ConversationRecord] = list(
        agentinstruct([rec], k_variants=6, keep_top_n=2, dedupe=True)
    )
    assert len(out) == 2
    # Ensure metadata has diversity proxy
    for r in out:
        assert r.metadata is not None
        assert isinstance(r.metadata.get("dedupe_score"), float)
        assert r.metadata.get("origin_id") == "rec-1"
