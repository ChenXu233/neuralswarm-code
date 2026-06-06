import json

from neuralswarm.services.llm.base import BaseAdapter
from neuralswarm.services.llm.types import LLMChunk, LLMResponse


class OpenAIAdapter(BaseAdapter):
    """OpenAI 格式适配器。"""

    @property
    def provider(self) -> str:
        return "openai"

    def get_endpoint(self, stream: bool) -> str:
        return "/v1/chat/completions"

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
        choice = data["choices"][0]
        return LLMResponse(
            content=choice["message"]["content"],
            model=data.get("model", ""),
            usage=data.get("usage", {}),
            finish_reason=choice.get("finish_reason", "stop"),
        )

    def parse_stream_chunk(self, line: str) -> LLMChunk | None:
        if not line.startswith("data: "):
            return None
        data_str = line[6:]
        if data_str.strip() == "[DONE]":
            return None
        try:
            data = json.loads(data_str)
            choice = data["choices"][0]
            delta = choice.get("delta", {})
            content = delta.get("content", "")
            if not content:
                return None
            return LLMChunk(
                content=content,
                finish_reason=choice.get("finish_reason"),
            )
        except (json.JSONDecodeError, KeyError, IndexError):
            return None
