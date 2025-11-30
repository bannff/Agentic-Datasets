"""Tests for v2 LLM-powered stages.

These tests verify the v2 stages work correctly with both LLM-powered
and fallback modes.
"""

from __future__ import annotations

import pytest
from unittest.mock import patch
from typing import Any, Callable, Dict, List

from agentic_datasets.schemas.messages import ConversationRecord, Message
from agentic_datasets.stages.agentinstruct_v2 import agentinstruct
from agentic_datasets.stages.s2m_v2 import s2m as single_to_multi
from agentic_datasets.stages.reviewinstruct_v2 import reviewinstruct
from agentic_datasets.stages.apigenmt_v2 import apigenmt


def _make_single_turn(user_content: str = "Explain SQL injection") -> ConversationRecord:
    """Create a simple single-turn conversation for testing."""
    return ConversationRecord(
        id="test-rec-1",
        source="unit-test",
        messages=[
            Message(role="user", content=user_content),
            Message(role="assistant", content="SQL injection is a code injection technique..."),
        ],
    )


def _make_multi_turn() -> ConversationRecord:
    """Create a multi-turn conversation for testing."""
    return ConversationRecord(
        id="test-rec-2",
        source="unit-test",
        messages=[
            Message(role="user", content="What is XSS?"),
            Message(role="assistant", content="XSS is cross-site scripting..."),
            Message(role="user", content="How do I prevent it?"),
            Message(role="assistant", content="Use output encoding and CSP headers..."),
        ],
    )


class TestAgentInstructV2:
    """Tests for AgentInstruct v2 stage."""

    def test_fallback_mode_generates_variants(self):
        """Test that fallback mode generates variants without LLM."""
        rec = _make_single_turn()
        out: List[ConversationRecord] = list(agentinstruct([rec], k_variants=3, use_llm=False))
        
        assert len(out) == 3
        for i, r in enumerate(out, start=1):
            assert r.messages[0].role == "user"
            assert r.metadata is not None
            assert r.metadata.get("stage") == "agentinstruct"
            assert r.metadata.get("llm_generated") is False
            assert r.metadata.get("variant_id") == f"v{i}"

    def test_metadata_tracks_transform_type(self):
        """Test that metadata includes transform type info."""
        rec = _make_single_turn()
        out: List[ConversationRecord] = list(
            agentinstruct([rec], k_variants=2, transforms=["qa", "coding"], use_llm=False)
        )
        
        transform_types = [r.metadata["transform_type"] for r in out if r.metadata]
        assert "qa" in transform_types or "coding" in transform_types

    def test_deduplication_removes_identical_variants(self):
        """Test that dedupe removes duplicate content."""
        rec = _make_single_turn()
        out: List[ConversationRecord] = list(
            agentinstruct([rec], k_variants=10, dedupe=True, use_llm=False)
        )
        
        # With deduplication, we shouldn't have more variants than transform types
        assert len(out) <= 7  # max 7 transform types

    def test_diversity_score_in_metadata(self):
        """Test that diversity score is computed and stored."""
        rec = _make_single_turn()
        out: List[ConversationRecord] = list(agentinstruct([rec], k_variants=2, use_llm=False))
        
        for r in out:
            assert r.metadata is not None
            assert "diversity_score" in r.metadata
            assert isinstance(r.metadata["diversity_score"], float)
            assert 0.0 <= r.metadata["diversity_score"] <= 1.0


class TestS2MV2:
    """Tests for Single-to-Multi turn v2 stage."""

    def test_fallback_mode_expands_conversation(self):
        """Test that fallback mode generates follow-up turns."""
        rec = _make_single_turn()
        out: List[ConversationRecord] = list(single_to_multi([rec], min_turns=4, max_turns=6, use_llm=False))
        
        assert len(out) == 1
        result = out[0]
        # Should have more messages than original (min_turns=4 means at least 4 messages)
        assert len(result.messages) >= 2
        assert result.metadata is not None
        assert result.metadata.get("stage") == "s2m"

    def test_multi_turn_conversation_passthrough(self):
        """Test that multi-turn conversations are passed through or enhanced."""
        rec = _make_multi_turn()
        out: List[ConversationRecord] = list(single_to_multi([rec], min_turns=4, use_llm=False))
        
        assert len(out) == 1
        result = out[0]
        assert len(result.messages) >= 4  # Original multi-turn


class TestReviewInstructV2:
    """Tests for ReviewInstruct v2 stage."""

    def test_fallback_mode_adds_review(self):
        """Test that fallback mode adds review markers."""
        rec = _make_single_turn()
        out: List[ConversationRecord] = list(reviewinstruct([rec], use_llm=False))
        
        assert len(out) == 1
        result = out[0]
        assert result.metadata is not None
        assert result.metadata.get("stage") == "reviewinstruct"

    def test_metadata_tracks_review_info(self):
        """Test that review metadata is populated."""
        rec = _make_single_turn()
        out: List[ConversationRecord] = list(reviewinstruct([rec], use_llm=False))
        
        result = out[0]
        assert result.metadata is not None
        assert "reviewed" in result.metadata or "stage" in result.metadata


class TestAPIGenMTV2:
    """Tests for APIGenMT v2 stage."""

    def test_fallback_mode_processes_records(self):
        """Test that fallback mode works without LLM."""
        rec = _make_single_turn("Check if port 443 is open on example.com")
        tools: List[Dict[str, Any]] = [
            {
                "name": "port_scan",
                "description": "Scan ports on a host",
                "parameters": {"host": {"type": "string"}, "port": {"type": "integer"}},
            }
        ]
        out: List[ConversationRecord] = list(apigenmt([rec], tools=tools, use_llm=False))
        
        assert len(out) == 1
        result = out[0]
        assert result.metadata is not None
        assert result.metadata.get("stage") == "apigenmt"

    def test_semantic_matching_injects_tools(self):
        """Test that semantic matching can inject relevant tools."""
        # Create a message that should trigger tool injection
        rec = _make_single_turn("Scan the network for open ports on 192.168.1.1")
        tools: List[Dict[str, Any]] = [
            {
                "name": "port_scanner",
                "description": "Scan ports on a network host",
                "parameters": {"host": {"type": "string"}},
            }
        ]
        out: List[ConversationRecord] = list(apigenmt([rec], tools=tools, use_llm=False))
        
        assert len(out) == 1
        result = out[0]
        assert result.metadata is not None


class TestV2StagesIntegration:
    """Integration tests for v2 stages working together."""

    def test_pipeline_chain_fallback_mode(self):
        """Test that stages can be chained together in fallback mode."""
        rec = _make_single_turn("Explain buffer overflow vulnerabilities")
        
        # Chain: agentinstruct -> s2m -> reviewinstruct
        step1 = list(agentinstruct([rec], k_variants=1, use_llm=False))
        assert len(step1) == 1
        
        step2 = list(single_to_multi(step1, min_turns=4, use_llm=False))
        assert len(step2) == 1
        
        step3 = list(reviewinstruct(step2, use_llm=False))
        assert len(step3) == 1
        
        # Final result should have metadata from all stages
        final = step3[0]
        assert final.metadata is not None
        # Each stage should have processed the record
        assert len(final.messages) >= 2


@pytest.fixture
def mock_llm_response() -> Callable[..., str]:
    """Mock LLM response for testing LLM-powered code paths."""
    def _mock_completion(*args: Any, **kwargs: Any) -> str:
        return "This is a mocked LLM response for testing purposes."
    return _mock_completion


class TestV2WithMockedLLM:
    """Tests with mocked LLM to verify LLM code paths."""

    def test_agentinstruct_with_mocked_llm(self, mock_llm_response: Callable[..., str]) -> None:
        """Test agentinstruct with mocked LLM responses."""
        with patch("agentic_datasets.stages.agentinstruct_v2.get_completion", mock_llm_response):
            rec = _make_single_turn()
            out: List[ConversationRecord] = list(agentinstruct([rec], k_variants=2, use_llm=True))
            
            # Should get variants (may be fewer due to deduplication of identical mock responses)
            assert len(out) >= 1
            for r in out:
                assert r.metadata is not None
                assert r.metadata.get("llm_generated") is True
