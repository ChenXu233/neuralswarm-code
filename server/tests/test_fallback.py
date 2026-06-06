import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from neuralswarm.services.llm.gateway import LLMGateway
from neuralswarm.services.llm.types import LLMRateLimitError, LLMResponse, LLMError


@pytest.fixture
def gateway():
    return LLMGateway(base_url="http://localhost:3000", timeout=30)


@pytest.mark.asyncio
async def test_chat_raises_rate_limit_on_429(gateway):
    """单个 provider 429 时抛出 LLMRateLimitError。"""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = "Rate limited"

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.return_value.post = AsyncMock(return_value=mock_response)

        with pytest.raises(LLMRateLimitError):
            await gateway.chat(
                provider="openai",
                model_id="gpt-4",
                messages=[{"role": "user", "content": "Hello"}],
            )


@pytest.mark.asyncio
async def test_chat_with_fallback_skips_429(gateway):
    """chat_with_fallback 在第一个 provider 429 时尝试下一个。"""
    mock_429 = MagicMock()
    mock_429.status_code = 429
    mock_429.text = "Rate limited"

    mock_200 = MagicMock()
    mock_200.status_code = 200
    # 第二个 provider 是 claude，使用 Claude 格式
    mock_200.json.return_value = {
        "content": [{"type": "text", "text": "Hi!"}],
        "model": "claude-3-sonnet",
        "usage": {"total_tokens": 10},
        "stop_reason": "end_turn",
    }

    call_count = 0

    async def mock_post(url, json=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_429
        return mock_200

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.return_value.post = AsyncMock(side_effect=mock_post)

        result = await gateway.chat_with_fallback(
            model_id="gpt-4",
            messages=[{"role": "user", "content": "Hello"}],
            providers=["openai", "claude"],
        )

        assert isinstance(result, LLMResponse)
        assert result.content == "Hi!"


@pytest.mark.asyncio
async def test_chat_with_fallback_all_fail(gateway):
    """所有 provider 都 429 时，抛出最后一个 LLMRateLimitError。"""
    mock_429 = MagicMock()
    mock_429.status_code = 429
    mock_429.text = "Rate limited"

    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client.return_value)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.return_value.post = AsyncMock(return_value=mock_429)

        with pytest.raises(LLMRateLimitError):
            await gateway.chat_with_fallback(
                model_id="gpt-4",
                messages=[{"role": "user", "content": "Hello"}],
                providers=["openai", "claude"],
            )
