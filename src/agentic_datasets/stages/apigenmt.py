from __future__ import annotations

from typing import Iterable, Iterator

from ..schemas.messages import ConversationRecord


def apigenmt(records: Iterable[ConversationRecord]) -> Iterator[ConversationRecord]:
    """Stub APIGenMT stage: annotate agentic/tool-use hints.

    Placeholder adds a metadata flag; real implementation will call APIGenMT and map tool calls.
    """
    for rec in records:
        meta = dict(rec.metadata or {})
        meta.setdefault("agentic", True)
        yield ConversationRecord(messages=rec.messages, metadata=meta, source=rec.source, id=rec.id)
