import pytest
from neuralswarm.services.bridge.protocol import ExecuteCommand, CommandResult
from neuralswarm.services.bridge.router import BridgeRouter
from neuralswarm.services.bridge.client_manager import ClientManager


def test_execute_command_to_json():
    cmd = ExecuteCommand(command="file_read", params={"path": "/tmp/test"})
    json_data = cmd.to_json()
    assert json_data["type"] == "execute"
    assert json_data["command"] == "file_read"
    assert json_data["params"]["path"] == "/tmp/test"
    assert "request_id" in json_data


def test_command_result_from_json():
    data = {
        "type": "result",
        "request_id": "req-001",
        "status": "success",
        "data": {"content": "hello"},
    }
    result = CommandResult.from_json(data)
    assert result.request_id == "req-001"
    assert result.status == "success"
    assert result.data["content"] == "hello"


def test_bridge_router_parse_uri():
    cm = ClientManager()
    router = BridgeRouter(cm)

    node_type, path = router._parse_uri("server:///home/user/file.py")
    assert node_type == "local"
    assert path == "/home/user/file.py"

    node_type, path = router._parse_uri("client://laptop/home/user/file.py")
    assert node_type == "laptop"
    assert path == "/home/user/file.py"


def test_client_manager_not_connected():
    cm = ClientManager()
    assert not cm.is_connected("nonexistent")
    assert cm.list_clients() == []
