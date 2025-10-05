from __future__ import annotations

from typing import Iterable, Iterator, Protocol

from pydantic import BaseModel

from ..schemas.messages import ConversationRecord


class StageConfig(BaseModel):
    """Base class for stage configs."""


class StageFunc(Protocol):
    def __call__(self, records: Iterable[ConversationRecord], **kwargs) -> Iterator[ConversationRecord]:
        ...
