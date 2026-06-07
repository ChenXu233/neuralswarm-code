import uuid

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

from neuralswarm.database import get_db
from neuralswarm.models.agent import Agent
from neuralswarm.models.llm import LLM
from neuralswarm.models.project import Project
from neuralswarm.models.task import Task
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


import pytest


@pytest.mark.asyncio
async def test_list_tasks(client):
    resp = await client.get("/api/tasks")
    assert resp.status_code == 200
    assert "items" in resp.json()


@pytest.mark.asyncio
async def test_get_task_not_found(client):
    resp = await client.get(f"/api/tasks/{uuid.uuid4()}")
    assert resp.status_code == 404
