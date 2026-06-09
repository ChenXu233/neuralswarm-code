"""反思 Agent - L0 + L1 → L2 整理"""

import logging
from typing import Any

from neuralswarm.services.memory.l2_memory import l2_memory

logger = logging.getLogger(__name__)


class ReflectionAgent:
    """反思 Agent"""

    async def reflect(
        self,
        project_id: str,
        context: list[dict[str, Any]],
        events: list[Any]
    ) -> dict[str, Any] | None:
        """执行反思，生成长期知识"""

        # 简化实现：从上下文和事件中提取关键信息
        topics = set()

        for msg in context[-5:]:
            content = msg.get("content", "")
            if "FastAPI" in content:
                topics.add("FastAPI")
            if "SQLAlchemy" in content:
                topics.add("SQLAlchemy")
            if "Python" in content:
                topics.add("Python")

        for event in events[-10:]:
            detail = getattr(event, 'detail', str(event))
            if "创建" in detail:
                topics.add("项目创建")

        if not topics:
            return None

        knowledge = await l2_memory.store_knowledge(
            project_id=project_id,
            content=f"项目使用技术: {', '.join(topics)}",
            source="reflection_agent",
            metadata={"topics": list(topics)}
        )

        logger.info("Reflection completed for project %s: %s", project_id, topics)
        return {"content": knowledge.content, "source": knowledge.source}


# 全局反思 Agent 实例
reflection_agent = ReflectionAgent()
