from __future__ import annotations

from typing import Iterable, Iterator

from ..schemas.messages import ConversationRecord, Message


def s2m(records: Iterable[ConversationRecord]) -> Iterator[ConversationRecord]:
    """Stub S2M stage: converts single-turn records to multi-turn shape if needed.

    For now, this is a pass-through; integration will call the real S2M tool and map outputs.
    """
    for rec in records:
        # If already multi-turn, yield as-is
        if len(rec.messages) > 1:
            yield rec
            continue
        # If single message, synthesize a minimal two-turn structure (placeholder)
        msg = rec.messages[0]
        if msg.role == "user":
            yield ConversationRecord(messages=[msg, Message(role="assistant", content="...")], metadata=rec.metadata, source=rec.source, id=rec.id)
        else:
            yield rec
