from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from neuralswarm.services.llm.types import LLMChunk, LLMResponse


class BaseAdapter(ABC):
    """LLM 格式适配器基类。"""

    @property
    @abstractmethod
    def provider(self) -> str:
        """Provider 名称。"""

    @abstractmethod
    def format_request(
        self,
        model_id: str,
        messages: list[dict],
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        tools: list[dict] | None = None,
    ) -> dict:
        """格式化请求体。"""

    @abstractmethod
    def get_endpoint(self, stream: bool) -> str:
        """获取 API 端点。"""

    @abstractmethod
    def parse_response(self, data: dict) -> LLMResponse:
        """解析非流式响应。"""

    @abstractmethod
    def parse_stream_chunk(self, line: str) -> LLMChunk | None:
        """解析流式 chunk。返回 None 表示跳过该行。"""
