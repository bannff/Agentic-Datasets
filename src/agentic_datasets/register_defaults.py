from __future__ import annotations

from .registry import registry
from .transforms.chunking import chunk_dataset
from .stages.agentinstruct import agentinstruct
from .stages.s2m import s2m
from .stages.apigenmt import apigenmt
from .stages.reviewinstruct import reviewinstruct


def register_defaults() -> None:
    registry.register("chunk", chunk_dataset)
    registry.register("agentinstruct", agentinstruct)
    registry.register("s2m", s2m)
    registry.register("apigenmt", apigenmt)
    registry.register("reviewinstruct", reviewinstruct)
