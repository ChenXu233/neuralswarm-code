"""L1 情景记忆 - 项目事件流"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """项目事件"""
    event_type: str
    detail: str
    project_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)


class L1Memory:
    """L1 情景记忆 - 使用内存存储（可扩展到 Redis Streams）"""

    def __init__(self):
        self._events: dict[str, list[Event]] = {}  # project_id -> events

    async def record_event(
        self,
        project_id: str,
        event_type: str,
        detail: str,
        metadata: dict[str, Any] | None = None,
    ) -> Event:
        """记录项目事件"""
        event = Event(
            event_type=event_type,
            detail=detail,
            project_id=project_id,
            metadata=metadata or {},
        )

        if project_id not in self._events:
            self._events[project_id] = []

        self._events[project_id].append(event)
        logger.debug("Recorded event for project %s: %s", project_id, event_type)
        return event

    async def get_events(
        self,
        project_id: str,
        limit: int = 100,
    ) -> list[Event]:
        """获取项目事件"""
        events = self._events.get(project_id, [])
        return events[-limit:]

    async def get_events_since(
        self,
        project_id: str,
        since: datetime,
    ) -> list[Event]:
        """获取指定时间之后的事件"""
        events = self._events.get(project_id, [])
        return [e for e in events if e.timestamp >= since]


# 全局 L1 记忆实例
l1_memory = L1Memory()
