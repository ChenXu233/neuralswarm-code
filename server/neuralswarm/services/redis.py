import json
from datetime import datetime, timezone

import redis.asyncio as redis

from neuralswarm.config import settings


class RedisClient:
    def __init__(self, url: str | None = None):
        self._url = url or settings.REDIS_URL
        self._pool: redis.Redis | None = None

    async def connect(self):
        # 使用 RESP2 协议以兼容旧版 Redis (3.x)
        self._pool = redis.from_url(self._url, decode_responses=True, protocol=2)

    async def close(self):
        if self._pool:
            await self._pool.aclose()

    @property
    def pool(self) -> redis.Redis:
        if self._pool is None:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._pool

    async def ping(self) -> bool:
        try:
            return await self.pool.ping()
        except Exception:
            return False

    async def publish_event(self, task_id: str, event: dict):
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        event_json = json.dumps(event)
        await self.pool.xadd(f"task:{task_id}:events", {"data": event_json})
        await self.pool.publish(f"task:{task_id}", event_json)

    async def get_events_since(self, task_id: str, last_id: str = "0") -> list[dict]:
        entries = await self.pool.xrange(f"task:{task_id}:events", min=last_id, max="+")
        events = []
        for entry_id, data in entries:
            event = json.loads(data["data"])
            event["event_id"] = entry_id
            events.append(event)
        return events

    async def subscribe(self, task_id: str):
        pubsub = self.pool.pubsub()
        await pubsub.subscribe(f"task:{task_id}")
        return pubsub

    async def set_task_status(self, task_id: str, status: str):
        await self.pool.set(f"task:{task_id}:status", status, ex=86400)

    async def get_task_status(self, task_id: str) -> str | None:
        return await self.pool.get(f"task:{task_id}:status")


redis_client = RedisClient()
