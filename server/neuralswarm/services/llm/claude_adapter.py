import json

from neuralswarm.services.llm.base import BaseAdapter
from neuralswarm.services.llm.types import LLMChunk, LLMResponse


class ClaudeAdapter(BaseAdapter):
    """Claude 格式适配器。"""

    @property
    def provider(self) -> str:
        return "claude"

    def get_endpoint(self, stream: bool) -> str:
        return "/v1/messages"

    def format_request(
        self,
        model_id: str,
        messages: list[dict],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> dict:
        body = {
            "model": model_id,
            "messages": messages,
            "stream": stream,
            "temperature": temperature,
        }
        if max_tokens is not None:
            body["max_tokens"] = max_tokens
        return body

    def parse_response(self, data: dict) -> LLMResponse:
        content_blocks = data.get("content", [])
        text = ""
        for block in content_blocks:
            if block.get("type") == "text":
                text += block.get("text", "")
        return LLMResponse(
            content=text,
            model=data.get("model", ""),
            usage=data.get("usage", {}),
            finish_reason=data.get("stop_reason", "end_turn"),
        )

    def parse_stream_chunk(self, line: str) -> LLMChunk | None:
        if not line.startswith("data: "):
            return None
        data_str = line[6:]
        try:
            data = json.loads(data_str)
            if data.get("type") == "content_block_delta":
                delta = data.get("delta", {})
                text = delta.get("text", "")
                if not text:
                    return None
                return LLMChunk(content=text, finish_reason=None)
            return None
        except (json.JSONDecodeError, KeyError):
            return None
