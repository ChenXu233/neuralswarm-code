from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from uuid import UUID

from neuralswarm.models.conflict import Conflict
from neuralswarm.models.enums import ConflictAction, ConflictStatus

logger = logging.getLogger(__name__)


class ConflictManager:
    """冲突管理器 - 检测、通知、解决冲突。

    注意：每个 task_id 仅支持一个订阅者（单订阅者模型）。
    如果同一 task_id 多次调用 subscribe，会复用同一个队列；
    任何一次 unsubscribe 都会删除该队列，导致其他订阅者断开。
    这是为个人使用场景设计的简化实现。
    """

    def __init__(self) -> None:
        self.pending_conflicts: dict[UUID, Conflict] = {}
        self._resolved_conflicts: dict[UUID, Conflict] = {}
        self._listeners: dict[UUID, asyncio.Queue[Conflict]] = {}

    async def detect(self, conflict: Conflict) -> None:
        """检测到冲突 → 注册 + 通知。

        Args:
            conflict: 冲突记录。
        """
        self.pending_conflicts[conflict.id] = conflict
        logger.warning(
            "Conflict detected: id=%s file=%s agent=%s other_agent=%s",
            conflict.id,
            conflict.file_path,
            conflict.agent_id,
            conflict.other_agent_id,
        )
        await self.notify(conflict)

    async def resolve(self, conflict_id: UUID, action: ConflictAction) -> Conflict:
        """用户决策 → 执行动作。

        Args:
            conflict_id: 冲突 ID。
            action: 用户选择的动作。

        Returns:
            更新后的冲突记录。

        Raises:
            KeyError: 冲突不存在。
            ValueError: 冲突已解决。
        """
        conflict = self.pending_conflicts.get(conflict_id)
        if conflict is None:
            # 检查是否已解决
            if conflict_id in self._resolved_conflicts:
                raise ValueError(
                    f"Conflict already {self._resolved_conflicts[conflict_id].status.value}: {conflict_id}"
                )
            raise KeyError(f"Conflict not found: {conflict_id}")
        if conflict.status != ConflictStatus.PENDING:
            raise ValueError(f"Conflict already {conflict.status.value}: {conflict_id}")

        conflict.status = ConflictStatus.RESOLVED
        conflict.action = action
        conflict.resolved_at = datetime.now(timezone.utc)

        # 从 pending 中移除，但保留在 _resolved 中供后续查询
        del self.pending_conflicts[conflict_id]
        self._resolved_conflicts[conflict_id] = conflict

        logger.info(
            "Conflict resolved: id=%s action=%s",
            conflict_id,
            action.value,
        )
        return conflict

    async def notify(self, conflict: Conflict) -> None:
        """WebSocket 推送冲突通知。

        Args:
            conflict: 冲突记录。
        """
        queue = self._listeners.get(conflict.task_id)
        if queue is not None:
            await queue.put(conflict)
            logger.debug(
                "Conflict notification queued: task=%s conflict=%s",
                conflict.task_id,
                conflict.id,
            )

    def subscribe(self, task_id: UUID) -> asyncio.Queue[Conflict]:
        """订阅冲突事件。

        每个 task_id 仅支持一个订阅者。重复订阅会返回同一个队列。

        Args:
            task_id: 任务 ID。

        Returns:
            冲突事件队列。
        """
        if task_id not in self._listeners:
            self._listeners[task_id] = asyncio.Queue()
        return self._listeners[task_id]

    def unsubscribe(self, task_id: UUID) -> None:
        """取消订阅。

        会直接删除该 task_id 的队列。如果同一 task_id 有其他订阅者，
        它们也会失去队列（单订阅者模型的已知限制）。

        Args:
            task_id: 任务 ID。
        """
        self._listeners.pop(task_id, None)
