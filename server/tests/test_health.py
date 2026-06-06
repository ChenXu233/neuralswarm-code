import pytest


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """测试 /health 端点返回 200"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
