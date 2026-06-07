import pytest
from httpx import ASGITransport, AsyncClient
from neuralswarm.server import create_app


@pytest.fixture
def client():
    app = create_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_list_clients(client):
    resp = await client.get("/api/clients")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_get_client_offline(client):
    resp = await client.get("/api/clients/nonexistent")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "offline"
