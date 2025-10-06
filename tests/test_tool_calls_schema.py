from agentic_datasets.schemas.messages import Message, ConversationRecord, ToolCall


def test_assistant_tool_call_and_tool_reply():
    assistant = Message(
        role="assistant",
        content="I'll fetch the status.",
        tool_calls=[
            ToolCall(
                id="call-1", name="http_request", arguments={"url": "https://api"}
            )
        ],
    )
    tool = Message(
        role="tool",
        content="OK",
        tool_name="http_request",
        tool_call_id="call-1",
        tool_output={"status": "ok"},
    )
    rec = ConversationRecord(
        messages=[Message(role="user", content="status?"), assistant, tool]
    )
    assert rec.messages[1].tool_calls and rec.messages[2].tool_output


def test_tool_message_requires_name():
    try:
        Message(role="tool", content="missing", tool_output={})
        assert False, "expected validation error"
    except Exception:
        assert True