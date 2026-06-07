import pytest
from neuralswarm.server import create_app


def test_websocket_route_registered():
    app = create_app()
    routes = [r.path for r in app.routes]
    assert "/ws/tasks/{task_id}" in routes
