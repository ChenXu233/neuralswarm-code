import tempfile

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

from neuralswarm.database import get_db
from neuralswarm.models.project import Project
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
async def test_create_project(client):
    with tempfile.TemporaryDirectory() as d:
        resp = await client.post("/api/projects", json={"name": "test-project", "path": d})
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["name"] == "test-project"
        assert "id" in data


@pytest.mark.asyncio
async def test_create_project_invalid_path(client):
    resp = await client.post("/api/projects", json={"name": "test", "path": "/nonexistent/path"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_projects(client):
    resp = await client.get("/api/projects")
    assert resp.status_code == 200
    assert "items" in resp.json()


@pytest.mark.asyncio
async def test_get_project(client):
    with tempfile.TemporaryDirectory() as d:
        create_resp = await client.post("/api/projects", json={"name": "test", "path": d})
        project_id = create_resp.json()["data"]["id"]
        resp = await client.get(f"/api/projects/{project_id}")
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == project_id


@pytest.mark.asyncio
async def test_get_project_not_found(client):
    import uuid
    resp = await client.get(f"/api/projects/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_project(client):
    with tempfile.TemporaryDirectory() as d:
        create_resp = await client.post("/api/projects", json={"name": "test", "path": d})
        project_id = create_resp.json()["data"]["id"]
        resp = await client.delete(f"/api/projects/{project_id}")
        assert resp.status_code == 200
        resp = await client.get(f"/api/projects/{project_id}")
        assert resp.status_code == 404
