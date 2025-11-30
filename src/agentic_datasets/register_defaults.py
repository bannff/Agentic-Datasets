from __future__ import annotations

from .registry import registry
from .transforms.chunking import chunk_dataset

# Import the new LLM-powered v2 stages
from .stages.agentinstruct_v2 import agentinstruct
from .stages.s2m_v2 import s2m
from .stages.apigenmt_v2 import apigenmt
from .stages.reviewinstruct_v2 import reviewinstruct

# Keep legacy imports available
from .stages import agentinstruct as agentinstruct_legacy
from .stages import s2m as s2m_legacy
from .stages import apigenmt as apigenmt_legacy
from .stages import reviewinstruct as reviewinstruct_legacy


def register_defaults() -> None:
    """Register default transforms.
    
    Uses the new LLM-powered v2 stages by default.
    Legacy keyword-based stages are available with _legacy suffix.
    """
    def _safe_register(name: str, fn) -> None:
        try:
            registry.register(name, fn)
        except ValueError:
            # Already registered; make this idempotent
            pass

    _safe_register("chunk", chunk_dataset)
    
    # Register v2 LLM-powered stages as defaults
    _safe_register("agentinstruct", agentinstruct)
    _safe_register("s2m", s2m)
    _safe_register("apigenmt", apigenmt)
    _safe_register("reviewinstruct", reviewinstruct)
    
    # Register legacy stages with _legacy suffix
    _safe_register("agentinstruct_legacy", agentinstruct_legacy.agentinstruct)
    _safe_register("s2m_legacy", s2m_legacy.s2m)
    _safe_register("apigenmt_legacy", apigenmt_legacy.apigenmt)
    _safe_register("reviewinstruct_legacy", reviewinstruct_legacy.reviewinstruct)
