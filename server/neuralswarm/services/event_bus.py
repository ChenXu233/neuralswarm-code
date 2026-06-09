"""事件总线 - 发布/订阅模式的事件系统"""
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


@dataclass
class Subscription:
    """订阅信息"""
    event_type: str
    handler: Callable[[dict[str, Any]], Awaitable[None]]
    id: str = field(default_factory=lambda: "")


class EventBus:
    """事件总线 - 纯本地实现，支持未来扩展到 Redis Streams"""

    def __init__(self):
        self._subscriptions: dict[str, list[Subscription]] = {}

    async def publish(self, event_type: str, data: dict[str, Any]) -> None:
        """发布事件"""
        # 通知本地订阅者，直接传递原始数据
        if event_type in self._subscriptions:
            for sub in self._subscriptions[event_type]:
                try:
                    await sub.handler(data)
                except Exception as e:
                    logger.warning("Event handler error: %s", e)

    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[dict[str, Any]], Awaitable[None]]
    ) -> Subscription:
        """订阅事件"""
        sub = Subscription(
            event_type=event_type,
            handler=handler,
            id=f"{event_type}:{id(handler)}"
        )

        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []

        self._subscriptions[event_type].append(sub)
        return sub

    async def unsubscribe(self, subscription: Subscription) -> None:
        """取消订阅"""
        if subscription.event_type in self._subscriptions:
            self._subscriptions[subscription.event_type] = [
                s for s in self._subscriptions[subscription.event_type]
                if s.id != subscription.id
            ]


# 全局事件总线实例
event_bus = EventBus()
