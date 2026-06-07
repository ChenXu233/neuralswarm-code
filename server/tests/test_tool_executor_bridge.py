import pytest
from neuralswarm.core.tool_executor import ToolExecutor


def test_tool_executor_cloud_mode():
    executor = ToolExecutor(project_path="/tmp")
    executor.register_defaults()
    assert "file_read" in executor.list_tools()
    assert "shell" in executor.list_tools()


def test_tool_executor_bridge_mode():
    class MockBridge:
        async def read(self, uri): return "content"
        async def write(self, uri, content): return "ok"
        async def shell(self, uri, cmd, timeout=30): return "output"

    executor = ToolExecutor(
        project_path="",
        bridge=MockBridge(),
        project_type="local",
        project_uri="client://laptop/home/user/project",
    )
    executor.register_defaults()
    assert "file_read" in executor.list_tools()
    assert "shell" in executor.list_tools()
