from collections.abc import AsyncIterator

import httpx

from neuralswarm.services.llm.base import BaseAdapter
from neuralswarm.services.llm.claude_adapter import ClaudeAdapter
from neuralswarm.services.llm.openai_adapter import OpenAIAdapter
from neuralswarm.services.llm.types import (
    LLMChunk,
    LLMError,
    LLMRateLimitError,
    LLMResponse,
    LLMTimeoutError,
)


class LLMGateway:
    """LLM 网关适配器主类。"""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._adapters: dict[str, BaseAdapter] = {
            "openai": OpenAIAdapter(),
            "claude": ClaudeAdapter(),
        }

    def _get_adapter(self, provider: str) -> BaseAdapter:
        """根据 provider 获取适配器。"""
        adapter = self._adapters.get(provider)
        if adapter is None:
            raise ValueError(
                f"Unknown provider: {provider}. Available: {list(self._adapters.keys())}"
            )
        return adapter

    async def chat(
        self,
        provider: str,
        model_id: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """非流式聊天。"""
        adapter = self._get_adapter(provider)
        endpoint = adapter.get_endpoint(stream=False)
        body = adapter.format_request(
            model_id=model_id,
            messages=messages,
            stream=False,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    json=body,
                )
            except httpx.TimeoutException:
                raise LLMTimeoutError()
            except httpx.NetworkError as e:
                raise LLMError(f"Network error: {e}", retryable=True)

        if response.status_code == 429:
            raise LLMRateLimitError()
        if response.status_code != 200:
            raise LLMError(
                f"HTTP {response.status_code}: {response.text}",
                status_code=response.status_code,
            )

        return adapter.parse_response(response.json())

    async def chat_with_fallback(
        self,
        model_id: str,
        messages: list[dict],
        providers: list[str],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """带降级的非流式聊天。依次尝试 providers 列表中的 provider。"""
        last_error = None
        for provider in providers:
            try:
                return await self.chat(
                    provider=provider,
                    model_id=model_id,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except LLMRateLimitError:
                last_error = LLMRateLimitError(f"Provider {provider} rate limited")
                continue
            except (LLMError, LLMTimeoutError) as e:
                if e.retryable:
                    last_error = e
                    continue
                raise
        raise last_error or LLMError("All providers failed")

    async def chat_stream(
        self,
        provider: str,
        model_id: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> AsyncIterator[LLMChunk]:
        """流式聊天。"""
        adapter = self._get_adapter(provider)
        endpoint = adapter.get_endpoint(stream=True)
        body = adapter.format_request(
            model_id=model_id,
            messages=messages,
            stream=True,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}{endpoint}",
                    json=body,
                ) as response:
                    if response.status_code == 429:
                        raise LLMRateLimitError()
                    if response.status_code != 200:
                        raise LLMError(
                            f"HTTP {response.status_code}",
                            status_code=response.status_code,
                        )
                    async for line in response.aiter_lines():
                        chunk = adapter.parse_stream_chunk(line)
                        if chunk is not None:
                            yield chunk
            except httpx.TimeoutException:
                raise LLMTimeoutError()
            except httpx.NetworkError as e:
                raise LLMError(f"Network error: {e}", retryable=True)
