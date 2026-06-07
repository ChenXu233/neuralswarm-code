import json

import pytest

from neuralswarm.services.llm.claude_adapter import ClaudeAdapter
from neuralswarm.services.llm.openai_adapter import OpenAIAdapter
from neuralswarm.services.llm.types import LLMResponse, ToolCall


def test_openai_parse_tool_calls():
    adapter = OpenAIAdapter()
    data = {
        "choices": [{
            "message": {
                "content": "",
                "tool_calls": [{
                    "id": "call_001",
                    "function": {
                        "name": "shell",
                        "arguments": json.dumps({"command": "ls -la"}),
                    },
                }],
            },
            "finish_reason": "tool_calls",
        }],
        "model": "gpt-4",
        "usage": {"total_tokens": 100},
    }
    resp = adapter.parse_response(data)
    assert resp.tool_calls is not None
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].name == "shell"
    assert resp.tool_calls[0].arguments == {"command": "ls -la"}


def test_openai_parse_no_tool_calls():
    adapter = OpenAIAdapter()
    data = {
        "choices": [{"message": {"content": "hello"}, "finish_reason": "stop"}],
        "model": "gpt-4",
        "usage": {"total_tokens": 50},
    }
    resp = adapter.parse_response(data)
    assert resp.tool_calls is None
    assert resp.content == "hello"


def test_claude_parse_tool_use():
    adapter = ClaudeAdapter()
    data = {
        "content": [
            {"type": "text", "text": "I'll run the command."},
            {"type": "tool_use", "id": "toolu_001", "name": "shell", "input": {"command": "ls"}},
        ],
        "model": "claude-sonnet-4-6",
        "usage": {"input_tokens": 50, "output_tokens": 30},
        "stop_reason": "tool_use",
    }
    resp = adapter.parse_response(data)
    assert resp.tool_calls is not None
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].name == "shell"
    assert resp.content == "I'll run the command."


def test_openai_format_request_with_tools():
    adapter = OpenAIAdapter()
    tools = [{"type": "function", "function": {"name": "shell", "parameters": {}}}]
    body = adapter.format_request(
        model_id="gpt-4", messages=[{"role": "user", "content": "hi"}], tools=tools,
    )
    assert "tools" in body
    assert body["tools"] == tools


def test_openai_format_request_without_tools():
    adapter = OpenAIAdapter()
    body = adapter.format_request(
        model_id="gpt-4", messages=[{"role": "user", "content": "hi"}],
    )
    assert "tools" not in body
