import json
import pytest
from neuralswarm.services.llm.claude_adapter import ClaudeAdapter


@pytest.fixture
def adapter():
    return ClaudeAdapter()


def test_provider(adapter):
    assert adapter.provider == "claude"


def test_get_endpoint(adapter):
    assert adapter.get_endpoint(stream=False) == "/v1/messages"
    assert adapter.get_endpoint(stream=True) == "/v1/messages"


def test_format_request(adapter):
    messages = [{"role": "user", "content": "Hello"}]
    body = adapter.format_request(
        model_id="claude-sonnet-4-6",
        messages=messages,
        stream=False,
        temperature=0.5,
        max_tokens=100,
    )
    assert body["model"] == "claude-sonnet-4-6"
    assert body["messages"] == messages
    assert body["stream"] is False
    assert body["temperature"] == 0.5
    assert body["max_tokens"] == 100


def test_parse_response(adapter):
    data = {
        "model": "claude-sonnet-4-6",
        "content": [{"type": "text", "text": "Hi there!"}],
        "stop_reason": "end_turn",
        "usage": {"input_tokens": 10, "output_tokens": 5},
    }
    response = adapter.parse_response(data)
    assert response.content == "Hi there!"
    assert response.model == "claude-sonnet-4-6"
    assert response.finish_reason == "end_turn"
    assert response.usage["input_tokens"] == 10


def test_parse_stream_chunk(adapter):
    line = 'data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"Hello"}}'
    chunk = adapter.parse_stream_chunk(line)
    assert chunk is not None
    assert chunk.content == "Hello"
    assert chunk.finish_reason is None


def test_parse_stream_chunk_stop(adapter):
    line = 'event: message_stop\ndata: {"type":"message_stop"}'
    chunk = adapter.parse_stream_chunk(line)
    assert chunk is None
