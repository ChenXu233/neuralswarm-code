"""冲突管理器测试。"""

import asyncio
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

from neuralswarm.database import get_db
from neuralswarm.models.agent import Agent
from neuralswarm.models.conflict import Conflict
from neuralswarm.models.enums import (
    AgentStatus,
    AgentType,
    ConflictAction,
    ConflictStatus,
    TaskStatus,
)
from neuralswarm.models.llm import LLM
from neuralswarm.models.project import Project
from neuralswarm.models.task import Task
from neuralswarm.server import create_app


# Allow JSONB to work with SQLite for testing
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Project.__table__.create, checkfirst=True)
        await conn.run_sync(Agent.__table__.create, checkfirst=True)
        await conn.run_sync(LLM.__table__.create, checkfirst=True)
        await conn.run_sync(Task.__table__.create, checkfirst=True)
        await conn.run_sync(Conflict.__table__.create, checkfirst=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def seed_data(db_session):
    """创建测试基础数据。"""
    project = Project(name="test-project", path="/tmp/test", config={})
    db_session.add(project)
    await db_session.flush()

    agent1 = Agent(
        project_id=project.id,
        name="agent-1",
        agent_type=AgentType.WORKER,
        status=AgentStatus.IDLE,
        tools=[],
        context={},
        llm_config={},
    )
    agent2 = Agent(
        project_id=project.id,
        name="agent-2",
        agent_type=AgentType.WORKER,
        status=AgentStatus.IDLE,
        tools=[],
        context={},
        llm_config={},
    )
    db_session.add_all([agent1, agent2])
    await db_session.flush()

    task = Task(
        project_id=project.id,
        agent_id=agent1.id,
        llm_id=uuid.uuid4(),
        input="test",
        status=TaskStatus.RUNNING,
    )
    db_session.add(task)
    await db_session.flush()

    await db_session.commit()
    return {"project": project, "agent1": agent1, "agent2": agent2, "task": task}


@pytest_asyncio.fixture
async def client(db_engine):
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


# ── Conflict model tests ──


@pytest.mark.asyncio
async def test_conflict_model_create(db_session, seed_data):
    """测试 Conflict 模型创建。"""
    data = seed_data
    conflict = Conflict(
        task_id=data["task"].id,
        file_path="src/main.py",
        agent_id=data["agent1"].id,
        other_agent_id=data["agent2"].id,
        old_hash="abc123",
        current_hash="def456",
        current_content="current",
        new_content="new",
        status=ConflictStatus.PENDING,
    )
    db_session.add(conflict)
    await db_session.commit()
    await db_session.refresh(conflict)

    assert conflict.id is not None
    assert conflict.status == ConflictStatus.PENDING
    assert conflict.action is None
    assert conflict.resolved_at is None
    assert conflict.created_at is not None


@pytest.mark.asyncio
async def test_conflict_model_defaults(db_session, seed_data):
    """测试 Conflict 模型默认值。"""
    data = seed_data
    conflict = Conflict(
        task_id=data["task"].id,
        file_path="test.py",
        agent_id=data["agent1"].id,
        other_agent_id=data["agent2"].id,
        old_hash="h1",
        current_hash="h2",
        current_content="c",
        new_content="n",
    )
    db_session.add(conflict)
    await db_session.commit()
    await db_session.refresh(conflict)

    assert conflict.status == ConflictStatus.PENDING
    assert conflict.action is None


# ── ConflictManager tests ──


@pytest.mark.asyncio
async def test_conflict_manager_detect():
    """测试 ConflictManager.detect 注册 + 通知。"""
    from neuralswarm.core.concurrency.conflict_manager import ConflictManager

    manager = ConflictManager()

    task_id = uuid.uuid4()
    queue = manager.subscribe(task_id)

    conflict = Conflict(
        id=uuid.uuid4(),
        task_id=task_id,
        file_path="src/app.py",
        agent_id=uuid.uuid4(),
        other_agent_id=uuid.uuid4(),
        old_hash="aaa",
        current_hash="bbb",
        current_content="old content",
        new_content="new content",
        status=ConflictStatus.PENDING,
    )

    await manager.detect(conflict)

    assert conflict.id in manager.pending_conflicts
    # 队列应收到通知
    received = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert received.id == conflict.id

    manager.unsubscribe(task_id)


@pytest.mark.asyncio
async def test_conflict_manager_resolve():
    """测试 ConflictManager.resolve 决策。"""
    from neuralswarm.core.concurrency.conflict_manager import ConflictManager

    manager = ConflictManager()

    conflict = Conflict(
        id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        file_path="src/app.py",
        agent_id=uuid.uuid4(),
        other_agent_id=uuid.uuid4(),
        old_hash="aaa",
        current_hash="bbb",
        current_content="old",
        new_content="new",
        status=ConflictStatus.PENDING,
    )

    await manager.detect(conflict)
    assert conflict.id in manager.pending_conflicts

    resolved = await manager.resolve(conflict.id, ConflictAction.OVERWRITE)
    assert resolved.status == ConflictStatus.RESOLVED
    assert resolved.action == ConflictAction.OVERWRITE
    assert resolved.resolved_at is not None
    assert conflict.id not in manager.pending_conflicts


@pytest.mark.asyncio
async def test_conflict_manager_resolve_not_found():
    """测试 ConflictManager.resolve 冲突不存在。"""
    from neuralswarm.core.concurrency.conflict_manager import ConflictManager

    manager = ConflictManager()

    with pytest.raises(KeyError):
        await manager.resolve(uuid.uuid4(), ConflictAction.RE_READ)


@pytest.mark.asyncio
async def test_conflict_manager_resolve_already_resolved():
    """测试 ConflictManager.resolve 冲突已解决。"""
    from neuralswarm.core.concurrency.conflict_manager import ConflictManager

    manager = ConflictManager()

    conflict = Conflict(
        id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        file_path="src/app.py",
        agent_id=uuid.uuid4(),
        other_agent_id=uuid.uuid4(),
        old_hash="aaa",
        current_hash="bbb",
        current_content="old",
        new_content="new",
        status=ConflictStatus.PENDING,
    )

    await manager.detect(conflict)
    await manager.resolve(conflict.id, ConflictAction.RE_READ)

    # 再次 resolve 应该抛出异常
    with pytest.raises(ValueError, match="already resolved"):
        await manager.resolve(conflict.id, ConflictAction.OVERWRITE)


@pytest.mark.asyncio
async def test_conflict_manager_subscribe_unsubscribe():
    """测试 ConflictManager subscribe/unsubscribe。"""
    from neuralswarm.core.concurrency.conflict_manager import ConflictManager

    manager = ConflictManager()

    task_id = uuid.uuid4()
    queue = manager.subscribe(task_id)
    assert isinstance(queue, asyncio.Queue)
    assert task_id in manager._listeners

    # 重复订阅应返回同一个队列
    queue2 = manager.subscribe(task_id)
    assert queue is queue2

    manager.unsubscribe(task_id)
    assert task_id not in manager._listeners

    # 取消不存在的订阅不应抛异常
    manager.unsubscribe(task_id)


@pytest.mark.asyncio
async def test_conflict_manager_notify_no_listener():
    """测试 ConflictManager.notify 无订阅者时静默。"""
    from neuralswarm.core.concurrency.conflict_manager import ConflictManager

    manager = ConflictManager()

    conflict = Conflict(
        id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        file_path="src/app.py",
        agent_id=uuid.uuid4(),
        other_agent_id=uuid.uuid4(),
        old_hash="aaa",
        current_hash="bbb",
        current_content="old",
        new_content="new",
        status=ConflictStatus.PENDING,
    )

    # 不应抛异常
    await manager.notify(conflict)


# ── API tests ──


@pytest.mark.asyncio
async def test_get_conflict(client, db_engine, seed_data):
    """测试 GET /api/conflicts/{conflict_id}。"""
    data = seed_data

    # 先插入冲突记录
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        conflict = Conflict(
            task_id=data["task"].id,
            file_path="src/app.py",
            agent_id=data["agent1"].id,
            other_agent_id=data["agent2"].id,
            old_hash="aaa",
            current_hash="bbb",
            current_content="old content",
            new_content="new content",
            status=ConflictStatus.PENDING,
        )
        session.add(conflict)
        await session.commit()
        await session.refresh(conflict)
        conflict_id = conflict.id

    resp = await client.get(f"/api/conflicts/{conflict_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["id"] == str(conflict_id)
    assert body["data"]["status"] == "pending"


@pytest.mark.asyncio
async def test_get_conflict_not_found(client):
    """测试 GET /api/conflicts/{conflict_id} 404。"""
    resp = await client.get(f"/api/conflicts/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_decide_conflict(client, db_engine, seed_data):
    """测试 POST /api/conflicts/{conflict_id}/decide。"""
    data = seed_data

    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        conflict = Conflict(
            task_id=data["task"].id,
            file_path="src/app.py",
            agent_id=data["agent1"].id,
            other_agent_id=data["agent2"].id,
            old_hash="aaa",
            current_hash="bbb",
            current_content="old content",
            new_content="new content",
            status=ConflictStatus.PENDING,
        )
        session.add(conflict)
        await session.commit()
        await session.refresh(conflict)
        conflict_id = conflict.id

    resp = await client.post(
        f"/api/conflicts/{conflict_id}/decide",
        json={"action": "overwrite"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["status"] == "resolved"
    assert body["data"]["action"] == "overwrite"
    assert body["data"]["resolved_at"] is not None


@pytest.mark.asyncio
async def test_decide_conflict_already_resolved(client, db_engine, seed_data):
    """测试 POST /api/conflicts/{conflict_id}/decide 已解决。"""
    data = seed_data
    from datetime import datetime, timezone

    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        conflict = Conflict(
            task_id=data["task"].id,
            file_path="src/app.py",
            agent_id=data["agent1"].id,
            other_agent_id=data["agent2"].id,
            old_hash="aaa",
            current_hash="bbb",
            current_content="old content",
            new_content="new content",
            status=ConflictStatus.RESOLVED,
            action=ConflictAction.RE_READ,
            resolved_at=datetime.now(timezone.utc),
        )
        session.add(conflict)
        await session.commit()
        await session.refresh(conflict)
        conflict_id = conflict.id

    resp = await client.post(
        f"/api/conflicts/{conflict_id}/decide",
        json={"action": "overwrite"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_decide_conflict_not_found(client):
    """测试 POST /api/conflicts/{conflict_id}/decide 404。"""
    resp = await client.post(
        f"/api/conflicts/{uuid.uuid4()}/decide",
        json={"action": "overwrite"},
    )
    assert resp.status_code == 404


# ── WebSocket tests ──


@pytest.mark.asyncio
async def test_conflict_ws_notification():
    """测试 WebSocket 冲突通知。"""
    from neuralswarm.core.concurrency.conflict_manager import ConflictManager
    from neuralswarm.api.ws_conflicts import conflict_events

    manager = ConflictManager()

    task_id = uuid.uuid4()
    queue = manager.subscribe(task_id)

    conflict = Conflict(
        id=uuid.uuid4(),
        task_id=task_id,
        file_path="src/app.py",
        agent_id=uuid.uuid4(),
        other_agent_id=uuid.uuid4(),
        old_hash="aaa",
        current_hash="bbb",
        current_content="old",
        new_content="new",
        status=ConflictStatus.PENDING,
    )

    await manager.detect(conflict)

    received = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert received.id == conflict.id
    assert received.task_id == task_id

    manager.unsubscribe(task_id)


@pytest.mark.asyncio
async def test_conflict_ws_subscribe_isolation():
    """测试不同 task_id 的订阅隔离。"""
    from neuralswarm.core.concurrency.conflict_manager import ConflictManager

    manager = ConflictManager()

    task1 = uuid.uuid4()
    task2 = uuid.uuid4()

    queue1 = manager.subscribe(task1)
    queue2 = manager.subscribe(task2)

    conflict1 = Conflict(
        id=uuid.uuid4(),
        task_id=task1,
        file_path="a.py",
        agent_id=uuid.uuid4(),
        other_agent_id=uuid.uuid4(),
        old_hash="h1",
        current_hash="h2",
        current_content="c1",
        new_content="n1",
        status=ConflictStatus.PENDING,
    )

    conflict2 = Conflict(
        id=uuid.uuid4(),
        task_id=task2,
        file_path="b.py",
        agent_id=uuid.uuid4(),
        other_agent_id=uuid.uuid4(),
        old_hash="h3",
        current_hash="h4",
        current_content="c2",
        new_content="n2",
        status=ConflictStatus.PENDING,
    )

    await manager.detect(conflict1)
    await manager.detect(conflict2)

    # task1 的队列只应收到 conflict1
    received1 = await asyncio.wait_for(queue1.get(), timeout=1.0)
    assert received1.id == conflict1.id

    # task2 的队列只应收到 conflict2
    received2 = await asyncio.wait_for(queue2.get(), timeout=1.0)
    assert received2.id == conflict2.id

    manager.unsubscribe(task1)
    manager.unsubscribe(task2)
