from __future__ import annotations


class ContextManager:
    """上下文管理器，支持自动 compact。"""

    def __init__(self, max_tokens: int = 100000, compact_keep: int = 10):
        self.messages: list[dict] = []
        self.total_tokens: int = 0
        self.max_tokens = max_tokens
        self.compact_keep = compact_keep

    def add_message(self, role: str, content: str, tokens: int = 0, tool_calls=None):
        """添加消息。如果提供 tool_calls，序列化为 OpenAI 格式。"""
        msg: dict = {"role": role, "content": content}
        if tool_calls is not None:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": tc.arguments,
                    },
                }
                for tc in tool_calls
            ]
        self.messages.append(msg)
        self.total_tokens += tokens

    def add_tool_result(self, call_id: str, result: str):
        """添加工具执行结果消息。"""
        self.messages.append({"role": "tool", "tool_call_id": call_id, "content": result})

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
