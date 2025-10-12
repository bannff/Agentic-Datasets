from __future__ import annotations

from .registry import registry
from .transforms.chunking import chunk_dataset
from .stages.agentinstruct import agentinstruct
from .stages.s2m import s2m
from .stages.apigenmt import apigenmt
from .stages.reviewinstruct import reviewinstruct


def register_defaults() -> None:
    def _safe_register(name: str, fn) -> None:
        try:
            registry.register(name, fn)
        except ValueError:
            # Already registered; make this idempotent
            pass

    _safe_register("chunk", chunk_dataset)
    _safe_register("agentinstruct", agentinstruct)
    _safe_register("s2m", s2m)
    _safe_register("apigenmt", apigenmt)
    _safe_register("reviewinstruct", reviewinstruct)
