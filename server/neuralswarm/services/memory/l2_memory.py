"""L2 语义记忆 - 长期知识存储"""

import logging
from typing import Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Knowledge:
    """长期知识"""
    content: str
    source: str
    project_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


class L2Memory:
    """L2 语义记忆 - 使用内存存储（可扩展到 Qdrant）"""

    def __init__(self):
        self._knowledge: dict[str, list[Knowledge]] = {}  # project_id -> knowledge

    async def store_knowledge(
        self,
        project_id: str,
        content: str,
        source: str,
        metadata: dict[str, Any] | None = None
    ) -> Knowledge:
        """存储知识"""
        knowledge = Knowledge(
            content=content,
            source=source,
            project_id=project_id,
            metadata=metadata or {}
        )

        if project_id not in self._knowledge:
            self._knowledge[project_id] = []

        self._knowledge[project_id].append(knowledge)
        logger.debug("Stored knowledge for project %s from %s", project_id, source)
        return knowledge

    async def search_knowledge(
        self,
        project_id: str,
        query: str,
        limit: int = 10
    ) -> list[Knowledge]:
        """搜索知识（简单关键词匹配，可扩展到向量搜索）"""
        knowledge_list = self._knowledge.get(project_id, [])

        # 简单关键词匹配
        results = [
            k for k in knowledge_list
            if query.lower() in k.content.lower()
        ]

        return results[:limit]

    async def get_all_knowledge(
        self,
        project_id: str
    ) -> list[Knowledge]:
        """获取项目所有知识"""
        return self._knowledge.get(project_id, [])


# 全局 L2 记忆实例
l2_memory = L2Memory()
