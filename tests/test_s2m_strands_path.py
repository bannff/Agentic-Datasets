import json
from types import SimpleNamespace

from agentic_datasets.stages.s2m import s2m, S2MConfig
from agentic_datasets.schemas.messages import ConversationRecord, Message


class DummyAgent:
    def __call__(self, prompt: str, system_prompt: str = "", params=None):
        # Return a minimal JSON conversation of 4 messages
        messages = [
            {"role": "user", "content": "Q1"},
            {"role": "assistant", "content": "A1"},
            {"role": "user", "content": "Q2"},
            {"role": "assistant", "content": "A2"},
        ]
        return SimpleNamespace(text=json.dumps(messages))


def test_s2m_prefers_strands_when_available(monkeypatch):
    # Patch importlib to simulate presence of strands and OllamaModel
    def fake_import_module(name):
        if name == "strands":
            # Provide Agent class
            class Agent:
                def __init__(self, model=None, tools=None):
                    pass

                def __call__(self, *args, **kwargs):
                    return DummyAgent()(*args, **kwargs)

            return SimpleNamespace(Agent=Agent)
        if name == "strands.models.ollama":

            class OllamaModel:
                def __init__(self, host: str, model_id: str):
                    self.host = host
                    self.model_id = model_id

            return SimpleNamespace(OllamaModel=OllamaModel)
        raise ImportError(name)

    monkeypatch.setattr("agentic_datasets.stages.s2m.importlib.import_module", fake_import_module)

    rec = ConversationRecord(
        messages=[
            Message(role="user", content="What is X?"),
            Message(role="assistant", content="X is Y."),
        ],
        metadata={},
        source="test",
        id="rec-1",
    )

    out = list(s2m([rec], S2MConfig(provider="ollama", model_name="qwen3:8b")))
    assert len(out) == 1
    convo = out[0]
    assert len(convo.messages) == 4
    assert isinstance(convo.metadata, dict)
    assert convo.metadata.get("via") == "strands"
