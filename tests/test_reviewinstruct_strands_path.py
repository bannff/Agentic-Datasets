"""ReviewInstruct Strands path tests."""
# mypy: ignore-errors

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from agentic_datasets.stages.reviewinstruct import reviewinstruct, ReviewInstructConfig
from agentic_datasets.schemas.messages import ConversationRecord, Message


class DummyAgent:
    def __init__(self, replies: list[str]):
        self._replies = replies
        self._i = 0

    def __call__(self, prompt: str, system_prompt: str | None = None, params: dict | None = None):
        # Return next reply cycling
        if self._i >= len(self._replies):
            self._i = 0
        txt = self._replies[self._i]
        self._i += 1
        return SimpleNamespace(text=txt)


def test_reviewinstruct_strands_accept(monkeypatch: pytest.MonkeyPatch):
    # Mock strands and model imports
    def fake_import_module(name: str):
        if name == "strands":
            return SimpleNamespace(Agent=lambda model: DummyAgent(["Decision: Accept\nSummary: ok"]))
        if name == "strands.models.ollama":
            return SimpleNamespace(OllamaModel=lambda host, model_id: SimpleNamespace())
        raise ImportError(name)

    monkeypatch.setattr("agentic_datasets.stages.reviewinstruct.importlib.import_module", fake_import_module)

    rec = ConversationRecord(
        messages=[
            Message(role="user", content="What is CSRF?"),
            Message(role="assistant", content="CSRF is..."),
        ],
        id="rec1",
        source="test",
    )

    out = list(reviewinstruct([rec], ReviewInstructConfig(max_iterations=1)))
    assert len(out) == 1
    assert out[0].metadata and out[0].metadata.get("stage") == "reviewinstruct"
    assert out[0].metadata.get("via") == "strands"
    assert out[0].metadata.get("decision") in {"accept", "unknown"}


def test_reviewinstruct_strands_refine(monkeypatch: pytest.MonkeyPatch):
    refined = json.dumps([
        {"role": "user", "content": "What is CSRF?"},
        {"role": "assistant", "content": "CSRF is a cross-site request forgery, ..."},
    ])

    def fake_import_module(name: str):
        if name == "strands":
            # First call is chairman => Refine; second is candidate => refined JSON
            return SimpleNamespace(Agent=lambda model: DummyAgent(["Decision: Refine\nPriority fixes: ...", refined]))
        if name == "strands.models.ollama":
            return SimpleNamespace(OllamaModel=lambda host, model_id: SimpleNamespace())
        raise ImportError(name)

    monkeypatch.setattr("agentic_datasets.stages.reviewinstruct.importlib.import_module", fake_import_module)

    rec = ConversationRecord(
        messages=[
            Message(role="user", content="Explain input validation"),
            Message(role="assistant", content="Input validation helps ..."),
        ],
        id="rec2",
        source="test",
    )

    out = list(reviewinstruct([rec], ReviewInstructConfig(max_iterations=1)))
    assert len(out) == 1
    assert out[0].metadata and out[0].metadata.get("stage") == "reviewinstruct"
    assert out[0].metadata.get("via") == "strands"
    assert out[0].metadata.get("decision") == "refine"
    assert len(out[0].messages) == 2
    assert out[0].messages[0].role == "user"
    assert out[0].messages[1].role == "assistant"
