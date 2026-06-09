import pytest
from datetime import datetime, timedelta

from neuralswarm.services.memory.l1_memory import L1Memory, Event


@pytest.fixture
def l1_memory():
    return L1Memory()


async def test_record_event(l1_memory):
    """测试记录事件"""
    event = await l1_memory.record_event(
        project_id="proj-1",
        event_type="task_completed",
        detail="任务完成: 实现登录功能"
    )

    assert isinstance(event, Event)
    assert event.event_type == "task_completed"
    assert event.detail == "任务完成: 实现登录功能"
    assert event.project_id == "proj-1"
    assert event.timestamp is not None
    assert isinstance(event.timestamp, datetime)
    assert event.metadata == {}


async def test_record_event_with_metadata(l1_memory):
    """测试带元数据的事件记录"""
    metadata = {"agent_id": "agent-1", "task_id": "task-42"}

    event = await l1_memory.record_event(
        project_id="proj-1",
        event_type="task_failed",
        detail="任务失败: 网络超时",
        metadata=metadata
    )

    assert event.metadata == metadata


async def test_get_events(l1_memory):
    """测试获取项目事件"""
    await l1_memory.record_event("proj-1", "event_a", "详情A")
    await l1_memory.record_event("proj-1", "event_b", "详情B")
    await l1_memory.record_event("proj-1", "event_c", "详情C")

    events = await l1_memory.get_events("proj-1")

    assert len(events) == 3
    assert events[0].event_type == "event_a"
    assert events[1].event_type == "event_b"
    assert events[2].event_type == "event_c"


async def test_get_events_returns_empty_for_unknown_project(l1_memory):
    """测试获取不存在项目的事件返回空列表"""
    events = await l1_memory.get_events("nonexistent")

    assert events == []


async def test_get_events_with_limit(l1_memory):
    """测试事件获取数量限制"""
    for i in range(10):
        await l1_memory.record_event("proj-1", f"event_{i}", f"详情{i}")

    events = await l1_memory.get_events("proj-1", limit=3)

    assert len(events) == 3
    # limit 取最后 N 条
    assert events[0].event_type == "event_7"
    assert events[2].event_type == "event_9"


async def test_get_events_project_isolation(l1_memory):
    """测试不同项目的事件互相隔离"""
    await l1_memory.record_event("proj-1", "event_a", "项目1的事件")
    await l1_memory.record_event("proj-2", "event_b", "项目2的事件")

    events_1 = await l1_memory.get_events("proj-1")
    events_2 = await l1_memory.get_events("proj-2")

    assert len(events_1) == 1
    assert len(events_2) == 1
    assert events_1[0].project_id == "proj-1"
    assert events_2[0].project_id == "proj-2"


async def test_get_events_since(l1_memory):
    """测试获取指定时间之后的事件"""
    base_time = datetime(2026, 1, 1, 12, 0, 0)

    # 使用 record_event 记录事件，然后手动修改时间戳来模拟
    e1 = await l1_memory.record_event("proj-1", "old_event", "旧事件")
    e1.timestamp = base_time

    e2 = await l1_memory.record_event("proj-1", "new_event", "新事件")
    e2.timestamp = base_time + timedelta(hours=1)

    since = base_time + timedelta(minutes=30)
    events = await l1_memory.get_events_since("proj-1", since=since)

    assert len(events) == 1
    assert events[0].event_type == "new_event"


async def test_event_default_timestamp():
    """测试 Event 数据类的默认时间戳"""
    event = Event(
        event_type="test",
        detail="测试",
        project_id="proj-1"
    )

    assert event.timestamp is not None
    assert isinstance(event.timestamp, datetime)
