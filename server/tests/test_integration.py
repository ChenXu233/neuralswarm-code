"""M2 integration test: full flow from project creation to task submission."""
import tempfile

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

from neuralswarm.database import get_db
from neuralswarm.models import Agent, LLM, Project, Task, TaskStatus
from neuralswarm.server import create_app


# Allow JSONB to work with SQLite for testing
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Project.__table__.create, checkfirst=True)
        await conn.run_sync(Agent.__table__.create, checkfirst=True)
        await conn.run_sync(LLM.__table__.create, checkfirst=True)
        await conn.run_sync(Task.__table__.create, checkfirst=True)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_project_and_list(client):
    """Create a project and verify it appears in the list."""
    with tempfile.TemporaryDirectory() as d:
        # Create project
        resp = await client.post("/api/projects", json={"name": "test-project", "path": d})
        assert resp.status_code == 200
        project_id = resp.json()["data"]["id"]
        assert project_id

        # List projects
        resp = await client.get("/api/projects")
        assert resp.status_code == 200
        projects = resp.json()["items"]
        assert any(p["id"] == project_id for p in projects)

        # Get project
        resp = await client.get(f"/api/projects/{project_id}")
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "test-project"


@pytest.mark.asyncio
async def test_api_endpoints_exist(client):
    """Verify all expected API endpoints are registered."""
    # Health
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    # Projects list
    resp = await client.get("/api/projects")
    assert resp.status_code == 200
    assert "items" in resp.json()


@pytest.mark.asyncio
async def test_project_crud_full_flow(client):
    """Full CRUD flow: create, get, list, delete."""
    with tempfile.TemporaryDirectory() as d:
        # Create
        resp = await client.post("/api/projects", json={"name": "crud-test", "path": d})
        assert resp.status_code == 200
        project_id = resp.json()["data"]["id"]

        # Get
        resp = await client.get(f"/api/projects/{project_id}")
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "crud-test"

        # List - should contain our project
        resp = await client.get("/api/projects")
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1

        # Delete
        resp = await client.delete(f"/api/projects/{project_id}")
        assert resp.status_code == 200

        # Verify deleted
        resp = await client.get(f"/api/projects/{project_id}")
        assert resp.status_code == 404
