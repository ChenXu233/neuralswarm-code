import pytest
from httpx import ASGITransport, AsyncClient
from neuralswarm.server import create_app


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")
