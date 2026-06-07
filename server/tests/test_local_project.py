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
async def test_create_cloud_project(client):
    with tempfile.TemporaryDirectory() as d:
        resp = await client.post("/api/projects", json={
            "name": "cloud-proj",
            "path": d,
            "project_type": "cloud",
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["project_type"] == "cloud"
        assert data["client_id"] is None


@pytest.mark.asyncio
async def test_create_local_project(client):
    resp = await client.post("/api/projects", json={
        "name": "local-proj",
        "path": "/home/user/project",
        "project_type": "local",
        "client_id": "client-001",
    })
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["project_type"] == "local"
    assert data["client_id"] == "client-001"
    assert data["path"] == "client://client-001/home/user/project"


@pytest.mark.asyncio
async def test_create_local_project_without_client_id(client):
    resp = await client.post("/api/projects", json={
        "name": "local-proj",
        "path": "/home/user/project",
        "project_type": "local",
    })
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_project_default_type(client):
    with tempfile.TemporaryDirectory() as d:
        resp = await client.post("/api/projects", json={
            "name": "default-proj",
            "path": d,
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["project_type"] == "cloud"
