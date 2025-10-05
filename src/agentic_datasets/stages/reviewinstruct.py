from __future__ import annotations

from typing import Iterable, Iterator

from ..schemas.messages import ConversationRecord


def reviewinstruct(records: Iterable[ConversationRecord]) -> Iterator[ConversationRecord]:
    """Stub ReviewInstruct: applies conversational refinement.

    Placeholder marks metadata and leaves messages unchanged.
    """
    for rec in records:
        meta = dict(rec.metadata or {})
        meta.setdefault("reviewed", True)
        yield ConversationRecord(messages=rec.messages, metadata=meta, source=rec.source, id=rec.id)
