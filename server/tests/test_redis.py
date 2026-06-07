import pytest
import pytest_asyncio

from neuralswarm.services.redis import RedisClient


@pytest_asyncio.fixture
async def redis_client():
    client = RedisClient(url="redis://localhost:6379/15")
    await client.connect()
    yield client
    await client.pool.flushdb()
    await client.close()


@pytest.mark.asyncio
async def test_ping(redis_client):
    result = await redis_client.ping()
    assert result is True


@pytest.mark.asyncio
async def test_task_status(redis_client):
    await redis_client.set_task_status("task-001", "running")
    status = await redis_client.get_task_status("task-001")
    assert status == "running"


@pytest.mark.asyncio
async def test_publish_and_retrieve_events(redis_client):
    await redis_client.publish_event(
        "task-002", {"type": "status", "data": {"status": "running"}}
    )
    await redis_client.publish_event(
        "task-002", {"type": "message", "data": {"content": "hello"}}
    )
    events = await redis_client.get_events_since("task-002")
    assert len(events) == 2
    assert events[0]["type"] == "status"
    assert events[1]["type"] == "message"
    assert "timestamp" in events[0]
