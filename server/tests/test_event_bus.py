"""事件总线测试"""
import pytest
import asyncio
from neuralswarm.services.event_bus import EventBus


@pytest.fixture
def event_bus():
    return EventBus()


@pytest.mark.asyncio
async def test_publish_and_subscribe(event_bus):
    """测试发布和订阅事件"""
    received = []

    async def handler(event):
        received.append(event)

    await event_bus.subscribe("test:event", handler)
    await event_bus.publish("test:event", {"data": "test"})

    await asyncio.sleep(0.1)  # 等待事件传播

    assert len(received) == 1
    assert received[0]["data"] == "test"


@pytest.mark.asyncio
async def test_multiple_subscribers(event_bus):
    """测试多个订阅者"""
    received1 = []
    received2 = []

    async def handler1(event):
        received1.append(event)

    async def handler2(event):
        received2.append(event)

    await event_bus.subscribe("test:event", handler1)
    await event_bus.subscribe("test:event", handler2)
    await event_bus.publish("test:event", {"data": "test"})

    await asyncio.sleep(0.1)

    assert len(received1) == 1
    assert len(received2) == 1


@pytest.mark.asyncio
async def test_unsubscribe(event_bus):
    """测试取消订阅"""
    received = []

    async def handler(event):
        received.append(event)

    subscription = await event_bus.subscribe("test:event", handler)
    await event_bus.unsubscribe(subscription)
    await event_bus.publish("test:event", {"data": "test"})

    await asyncio.sleep(0.1)

    assert len(received) == 0
