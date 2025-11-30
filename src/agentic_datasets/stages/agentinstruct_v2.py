"""AgentInstruct Stage: LLM-powered instruction transformation.

Implements the Microsoft AgentInstruct methodology using real LLM reasoning
to transform seed instructions into diverse, high-quality variants.

Transformation Types:
1. Question Answering - Q&A format transformations
2. Open Domain Writing - Creative/exploratory expansions
3. Coding/Debugging - Technical implementation focus
4. Classification - Categorization and comparison tasks
5. Summarization - Concise key-point extraction
6. Extraction - Specific information pulling
7. Reasoning - Multi-step logical analysis

Each variant is generated using LLM reasoning, not simple string templates.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Dict, Iterable, Iterator, List, Optional

from ..llm import LLMConfig, get_completion, get_default_config
from ..llm.prompts import AGENTINSTRUCT_SYSTEM, TRANSFORM_PROMPTS, COMPLEXITY_PROMPTS
from ..schemas.messages import ConversationRecord, Message

logger = logging.getLogger(__name__)

# Default transformation types to use
DEFAULT_TRANSFORMS = ["qa", "writing", "coding", "reasoning"]


def _normalize_text(s: str) -> str:
    """Normalize text for deduplication."""
    return " ".join(s.lower().strip().split())


def _hash_text(s: str) -> str:
    """Hash normalized text for deduplication."""
    return hashlib.sha256(_normalize_text(s).encode("utf-8")).hexdigest()[:16]


def _jaccard_diversity(a: str, b: str) -> float:
    """Calculate Jaccard diversity between two texts (0..1)."""
    at = set(_normalize_text(a).split())
    bt = set(_normalize_text(b).split())
    if not at and not bt:
        return 0.0
    inter = len(at & bt)
    union = len(at | bt) or 1
    return 1.0 - (inter / union)


def _transform_with_llm(
    seed: str,
    transform_type: str,
    config: LLMConfig,
) -> Optional[str]:
    """Transform a seed instruction using LLM reasoning.
    
    Args:
        seed: The original instruction text
        transform_type: One of the 7 transformation types
        config: LLM configuration
    
    Returns:
        Transformed instruction or None on failure
    """
    prompt_template = TRANSFORM_PROMPTS.get(transform_type)
    if not prompt_template:
        logger.warning(f"Unknown transform type: {transform_type}")
        return None
    
    prompt = prompt_template.format(seed=seed)
    
    try:
        response = get_completion(
            prompt,
            system_prompt=AGENTINSTRUCT_SYSTEM,
            config=config,
            temperature=0.8,  # Higher for diversity
            max_tokens=512,
        )
        return response.strip()
    except Exception as e:
        logger.warning(f"LLM transform failed for {transform_type}: {e}")
        return None


def _adjust_complexity(
    instruction: str,
    level: str,
    config: LLMConfig,
) -> Optional[str]:
    """Adjust instruction complexity using LLM.
    
    Args:
        instruction: The instruction to adjust
        level: beginner, intermediate, or advanced
        config: LLM configuration
    
    Returns:
        Adjusted instruction or None on failure
    """
    prompt_template = COMPLEXITY_PROMPTS.get(level)
    if not prompt_template:
        return None
    
    prompt = prompt_template.format(instruction=instruction)
    
    try:
        from ..llm.prompts.agentinstruct import COMPLEXITY_SYSTEM
        response = get_completion(
            prompt,
            system_prompt=COMPLEXITY_SYSTEM,
            config=config,
            temperature=0.6,
            max_tokens=512,
        )
        return response.strip()
    except Exception as e:
        logger.warning(f"Complexity adjustment failed: {e}")
        return None


def _fallback_transform(seed: str, transform_type: str) -> str:
    """Fallback transformation when LLM is unavailable.
    
    Uses simple suffix-based transformations as a last resort.
    """
    suffixes = {
        "qa": " Explain this in a Q&A format with clear answers.",
        "writing": " Provide a comprehensive explanation with examples.",
        "coding": " Include code examples and implementation details.",
        "classification": " Compare and categorize the different approaches.",
        "summarization": " Summarize the key points concisely.",
        "extraction": " Extract the essential facts and data points.",
        "reasoning": " Walk through the logic step by step.",
    }
    return seed.strip() + suffixes.get(transform_type, "")


def agentinstruct(
    records: Iterable[ConversationRecord],
    *,
    k_variants: int = 3,
    transforms: Optional[List[str]] = None,
    complexity_levels: Optional[List[str]] = None,
    dedupe: bool = True,
    use_llm: bool = True,
    llm_config: Optional[Dict[str, Any]] = None,
) -> Iterator[ConversationRecord]:
    """Expand each record into k diverse instruction variants using LLM reasoning.
    
    This implements the AgentInstruct methodology with real LLM-powered
    transformations instead of simple string templates.
    
    Args:
        records: Input stream of ConversationRecord
        k_variants: Number of variants to generate per input
        transforms: List of transformation types to use
            Options: qa, writing, coding, classification, summarization, extraction, reasoning
        complexity_levels: Optional list of complexity adjustments
            Options: beginner, intermediate, advanced
        dedupe: Remove duplicate/similar variants
        use_llm: Whether to use LLM (False falls back to templates)
        llm_config: Optional LLM configuration override
    
    Yields:
        ConversationRecord items, one per variant (fan-out)
    """
    # Setup configuration
    config = LLMConfig(**(llm_config or {})) if llm_config else get_default_config()
    transform_types = transforms or DEFAULT_TRANSFORMS
    k = max(1, int(k_variants))
    
    # Log configuration
    logger.info(f"AgentInstruct: k={k}, transforms={transform_types}, use_llm={use_llm}")
    if use_llm:
        logger.info(f"Using LLM: {config.model}")
    
    for rec in records:
        # Find first user message as seed
        user_idx = next(
            (i for i, m in enumerate(rec.messages) if m.role == "user"),
            None
        )
        if user_idx is None:
            yield rec
            continue
        
        seed = rec.messages[user_idx].content
        origin_id = rec.id
        
        # Generate variants using selected transforms
        candidates: List[tuple[str, str]] = []  # (variant_text, transform_type)
        
        for transform_type in transform_types:
            if len(candidates) >= k:
                break
            
            if use_llm:
                variant = _transform_with_llm(seed, transform_type, config)
                if variant and variant != seed:
                    candidates.append((variant, transform_type))
            else:
                variant = _fallback_transform(seed, transform_type)
                candidates.append((variant, transform_type))
        
        # Apply complexity adjustments if requested
        if complexity_levels and use_llm:
            adjusted: List[tuple[str, str]] = []
            for variant, ttype in candidates:
                for level in complexity_levels:
                    if len(adjusted) >= k:
                        break
                    adj = _adjust_complexity(variant, level, config)
                    if adj:
                        adjusted.append((adj, f"{ttype}_{level}"))
            if adjusted:
                candidates = adjusted[:k]
        
        # Deduplicate by content hash
        if dedupe:
            unique: Dict[str, tuple[str, str]] = {}
            for variant, ttype in candidates:
                h = _hash_text(variant)
                if h not in unique:
                    unique[h] = (variant, ttype)
            candidates = list(unique.values())
        
        # Take top k
        candidates = candidates[:k]
        
        # Yield variant records
        for i, (variant, transform_type) in enumerate(candidates, start=1):
            # Rewrite first user message; keep rest unchanged
            new_messages: List[Message] = []
            for idx, msg in enumerate(rec.messages):
                if idx == user_idx and msg.role == "user":
                    new_messages.append(Message(role="user", content=variant))
                else:
                    new_messages.append(msg)
            
            meta: Dict[str, Any] = dict(rec.metadata or {})
            meta.update({
                "stage": "agentinstruct",
                "origin_id": origin_id,
                "variant_id": f"v{i}",
                "transform_type": transform_type,
                "variant_prompt": variant,
                "diversity_score": _jaccard_diversity(variant, seed),
                "llm_generated": use_llm,
                "model": config.model if use_llm else None,
            })
            
            yield ConversationRecord(
                messages=new_messages,
                id=(rec.id or "rec") + f"::v{i}",
                source=rec.source,
                metadata=meta,
            )
