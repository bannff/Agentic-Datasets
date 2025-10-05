from __future__ import annotations

from pathlib import Path

from agentic_datasets.schemas.messages import Message, ConversationRecord
from agentic_datasets.transforms.chunking import chunk_conversation


def test_chunk_conversation_basic(tmp_path: Path) -> None:
    # Build a conversation with a long user message to force splitting
    long_text = "Hello " * 300  # repeated to exceed ~512 tokens with cl100k_base
    rec = ConversationRecord(
        id="conv-1",
        source="unit-test",
        messages=[
            Message(role="user", content=long_text),
            Message(role="assistant", content="Thanks for your question."),
        ],
    )

    chunks = chunk_conversation(rec, model_name="gpt-4o-mini", max_tokens=200, overlap=20)
    assert len(chunks) >= 2
    # Ensure each chunk has at least one message and content present
    for c in chunks:
        assert c.messages and c.messages[0].content
