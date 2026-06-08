import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

from neuralswarm.database import get_db
from neuralswarm.models.agent import Agent
from neuralswarm.models.enums import AgentStatus, AgentType
from neuralswarm.models.project import Project
from neuralswarm.server import create_app


# Allow JSONB to work with SQLite for testing
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


_engine = None
_session_factory = None


@pytest_asyncio.fixture
async def client():
    global _engine, _session_factory
    _engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with _engine.begin() as conn:
        await conn.run_sync(Project.__table__.create, checkfirst=True)
        await conn.run_sync(Agent.__table__.create, checkfirst=True)

    _session_factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with _session_factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    await _engine.dispose()
    _engine = None
    _session_factory = None


async def _create_test_data():
    """Helper to create test data using the session factory."""
    async with _session_factory() as session:
        project = Project(id=uuid.uuid4(), name="Test Project", path="/test/project")
        session.add(project)
        await session.commit()

        agents = [
            Agent(
                id=uuid.uuid4(),
                project_id=project.id,
                name="Scheduler Agent",
                agent_type=AgentType.SCHEDULER,
                status=AgentStatus.IDLE,
            ),
            Agent(
                id=uuid.uuid4(),
                project_id=project.id,
                name="Worker Agent 1",
                agent_type=AgentType.WORKER,
                status=AgentStatus.RUNNING,
            ),
            Agent(
                id=uuid.uuid4(),
                project_id=project.id,
                name="Worker Agent 2",
                agent_type=AgentType.WORKER,
                status=AgentStatus.COMPLETED,
            ),
        ]
        session.add_all(agents)
        await session.commit()
        return project, agents


@pytest.mark.asyncio
async def test_list_agents_empty(client):
    resp = await client.get("/api/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_get_agent_not_found(client):
    resp = await client.get(f"/api/agents/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Agent not found"


@pytest.mark.asyncio
async def test_list_agents_with_pagination(client):
    project, agents = await _create_test_data()

    resp = await client.get("/api/agents", params={"limit": 2, "offset": 0})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["total"] == 3

    resp = await client.get("/api/agents", params={"limit": 2, "offset": 2})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_list_agents_filter_by_status(client):
    project, agents = await _create_test_data()

    resp = await client.get("/api/agents", params={"status": "running"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "running"


@pytest.mark.asyncio
async def test_list_agents_filter_by_agent_type(client):
    project, agents = await _create_test_data()

    resp = await client.get("/api/agents", params={"agent_type": "worker"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    for item in data["items"]:
        assert item["agent_type"] == "worker"


@pytest.mark.asyncio
async def test_list_agents_filter_by_project_id(client):
    project, agents = await _create_test_data()

    resp = await client.get("/api/agents", params={"project_id": str(project.id)})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 3
    for item in data["items"]:
        assert item["project_id"] == str(project.id)


@pytest.mark.asyncio
async def test_get_agent_found(client):
    project, agents = await _create_test_data()
    agent = agents[0]

    resp = await client.get(f"/api/agents/{agent.id}")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["id"] == str(agent.id)
    assert data["name"] == agent.name
    assert data["agent_type"] == agent.agent_type.value
    assert data["status"] == agent.status.value
