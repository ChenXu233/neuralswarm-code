from __future__ import annotations


class ContextManager:
    """上下文管理器，支持自动 compact。"""

    def __init__(self, max_tokens: int = 100000, compact_keep: int = 10):
        self.messages: list[dict] = []
        self.total_tokens: int = 0
        self.max_tokens = max_tokens
        self.compact_keep = compact_keep

    def add_message(self, role: str, content: str, tokens: int = 0):
        """添加消息。"""
        self.messages.append({"role": role, "content": content})
        self.total_tokens += tokens

    def get_messages(self) -> list[dict]:
        """获取所有消息。"""
        return self.messages

    def update_tokens(self, usage: dict):
        """根据 API 返回的 usage 更新 token 消耗。"""
        self.total_tokens += usage.get("total_tokens", 0)

    def needs_compact(self) -> bool:
        """是否需要 compact。"""
        return self.total_tokens > self.max_tokens

    def compact(self, summary: str):
        """执行 compact：保留最近 N 条消息，旧的替换为摘要。"""
        if len(self.messages) <= self.compact_keep:
            return
        recent = self.messages[-self.compact_keep:]
        self.messages = [{"role": "system", "content": f"Previous context summary: {summary}"}] + recent
        self.total_tokens = 0

    def auto_compact_check(self) -> bool:
        """检查是否需要 compact。"""
        return self.needs_compact()
