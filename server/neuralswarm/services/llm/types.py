from dataclasses import dataclass, field


@dataclass
class ToolCall:
    """LLM 返回的工具调用。"""
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    """LLM 非流式响应。"""
    content: str
    model: str
    usage: dict = field(default_factory=dict)
    finish_reason: str = "stop"
    tool_calls: list[ToolCall] | None = None


@dataclass
class LLMChunk:
    """LLM 流式响应 chunk。"""
    content: str
    finish_reason: str | None = None


class LLMError(Exception):
    """LLM 调用错误。"""
    def __init__(self, message: str, status_code: int | None = None, retryable: bool = False):
        super().__init__(message)
        self.status_code = status_code
        self.retryable = retryable


class LLMRateLimitError(LLMError):
    """429 限流错误。"""
    def __init__(self, message: str = "Rate limited"):
        super().__init__(message, status_code=429, retryable=True)


class LLMTimeoutError(LLMError):
    """超时错误。"""
    def __init__(self, message: str = "Request timed out"):
        super().__init__(message, retryable=True)
