"""L0 瞬时记忆 - Agent 上下文持久化"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class L0Memory:
    """L0 瞬时记忆 - 使用内存存储（可扩展到 Redis）"""

    def __init__(self):
        self._storage: dict[str, list[dict[str, Any]]] = {}

    async def save_context(
        self,
        agent_id: str,
        context: list[dict[str, Any]]
    ) -> None:
        """保存 Agent 上下文"""
        self._storage[agent_id] = context
        logger.debug("Saved context for agent %s (%d messages)", agent_id, len(context))

    async def load_context(
        self,
        agent_id: str
    ) -> list[dict[str, Any]] | None:
        """加载 Agent 上下文"""
        return self._storage.get(agent_id)

    async def compact_context(
        self,
        agent_id: str,
        keep_last: int = 10
    ) -> list[dict[str, Any]]:
        """压缩上下文，保留最后 N 条消息"""
        context = await self.load_context(agent_id)
        if not context:
            return []

        if len(context) <= keep_last:
            return context

        # 保留最后 N 条消息
        compacted = context[-keep_last:]
        await self.save_context(agent_id, compacted)
        logger.info("Compacted context for agent %s: %d -> %d messages",
                    agent_id, len(context), len(compacted))
        return compacted

    async def clear_context(self, agent_id: str) -> None:
        """清除 Agent 上下文"""
        if agent_id in self._storage:
            del self._storage[agent_id]
            logger.debug("Cleared context for agent %s", agent_id)


# 全局 L0 记忆实例
l0_memory = L0Memory()
