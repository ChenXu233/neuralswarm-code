import tempfile

import pytest
from neuralswarm.core.tool_executor import ToolExecutor
from neuralswarm.core.tool_metadata import ToolMetadata, ToolParameter


@pytest.fixture
def project_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def executor(project_dir):
    return ToolExecutor(project_path=project_dir)


def test_register_and_execute(executor: ToolExecutor):
    async def hello(name: str) -> str:
        return f"Hello {name}"

    executor.register("hello", hello)


@pytest.mark.asyncio
async def test_execute_unknown_tool(executor: ToolExecutor):
    result = await executor.execute("unknown", {})
    assert "Error" in result


@pytest.mark.asyncio
async def test_execute_registered_tool(executor: ToolExecutor):
    async def add(a: int, b: int) -> str:
        return str(a + b)

    executor.register("add", add)
    result = await executor.execute("add", {"a": 1, "b": 2})
    assert result == "3"


def test_list_tools(executor: ToolExecutor):
    async def tool_a():
        pass

    async def tool_b():
        pass

    executor.register("a", tool_a)
    executor.register("b", tool_b)
    assert executor.list_tools() == ["a", "b"]


@pytest.mark.asyncio
async def test_register_defaults(executor: ToolExecutor):
    executor.register_defaults()
    assert "file_read" in executor.list_tools()
    assert "file_write" in executor.list_tools()
    assert "shell" in executor.list_tools()


def test_metadata_from_register(executor: ToolExecutor):
    async def my_tool(x: str) -> str:
        return x

    meta = ToolMetadata(
        name="my_tool",
        description="A tool",
        parameters=[ToolParameter(name="x", type="string", description="input")],
    )
    executor.register("my_tool", my_tool, metadata=meta)
    assert executor.get_metadata("my_tool") is meta


def test_to_openai_tools(executor: ToolExecutor):
    executor.register_defaults()
    tools = executor.to_openai_tools()
    assert len(tools) == 3
    names = {t["function"]["name"] for t in tools}
    assert names == {"file_read", "file_write", "shell"}
    # Check structure
    for t in tools:
        assert t["type"] == "function"
        assert "parameters" in t["function"]


def test_to_anthropic_tools(executor: ToolExecutor):
    executor.register_defaults()
    tools = executor.to_anthropic_tools()
    assert len(tools) == 3
    names = {t["name"] for t in tools}
    assert names == {"file_read", "file_write", "shell"}
    for t in tools:
        assert "input_schema" in t
