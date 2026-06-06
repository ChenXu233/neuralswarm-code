import json
import pytest
from neuralswarm.services.llm.openai_adapter import OpenAIAdapter


@pytest.fixture
def adapter():
    return OpenAIAdapter()


def test_provider(adapter):
    assert adapter.provider == "openai"


def test_get_endpoint(adapter):
    assert adapter.get_endpoint(stream=False) == "/v1/chat/completions"
    assert adapter.get_endpoint(stream=True) == "/v1/chat/completions"


def test_format_request(adapter):
    messages = [{"role": "user", "content": "Hello"}]
    body = adapter.format_request(
        model_id="gpt-4",
        messages=messages,
        stream=False,
        temperature=0.5,
        max_tokens=100,
    )
    assert body["model"] == "gpt-4"
    assert body["messages"] == messages
    assert body["stream"] is False
    assert body["temperature"] == 0.5
    assert body["max_tokens"] == 100


def test_format_request_stream(adapter):
    messages = [{"role": "user", "content": "Hello"}]
    body = adapter.format_request(model_id="gpt-4", messages=messages, stream=True)
    assert body["stream"] is True


def test_parse_response(adapter):
    data = {
        "model": "gpt-4",
        "choices": [{"message": {"content": "Hi there!"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }
    response = adapter.parse_response(data)
    assert response.content == "Hi there!"
    assert response.model == "gpt-4"
    assert response.finish_reason == "stop"
    assert response.usage["total_tokens"] == 15


def test_parse_stream_chunk(adapter):
    line = 'data: {"choices": [{"delta": {"content": "Hello"}, "finish_reason": null}]}'
    chunk = adapter.parse_stream_chunk(line)
    assert chunk is not None
    assert chunk.content == "Hello"
    assert chunk.finish_reason is None


def test_parse_stream_chunk_done(adapter):
    line = "data: [DONE]"
    chunk = adapter.parse_stream_chunk(line)
    assert chunk is None
