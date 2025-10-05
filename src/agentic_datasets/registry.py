from __future__ import annotations

from typing import Callable
from collections.abc import Iterator

from .schemas.messages import ConversationRecord


Transform = Callable[..., Iterator[ConversationRecord]]


class Registry:
    def __init__(self) -> None:
        self._transforms: dict[str, Transform] = {}

    def register(self, name: str, fn: Transform) -> None:
        if name in self._transforms:
            raise ValueError(f"Transform '{name}' already registered")
        self._transforms[name] = fn

    def get(self, name: str) -> Transform:
        if name not in self._transforms:
            raise KeyError(f"Unknown transform: {name}")
        return self._transforms[name]

    def list(self) -> dict[str, Transform]:
        return dict(self._transforms)


registry = Registry()
