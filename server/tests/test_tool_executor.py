import pytest
from neuralswarm.core.tool_executor import ToolExecutor


@pytest.fixture
def executor():
    return ToolExecutor()


def test_register_and_execute(executor):
    async def hello(name: str) -> str:
        return f"Hello {name}"

    executor.register("hello", hello)


@pytest.mark.asyncio
async def test_execute_unknown_tool(executor):
    result = await executor.execute("unknown", {})
    assert "Error" in result


@pytest.mark.asyncio
async def test_execute_registered_tool(executor):
    async def add(a: int, b: int) -> str:
        return str(a + b)

    executor.register("add", add)
    result = await executor.execute("add", {"a": 1, "b": 2})
    assert result == "3"


def test_list_tools(executor):
    async def tool_a():
        pass

    async def tool_b():
        pass

    executor.register("a", tool_a)
    executor.register("b", tool_b)
    assert executor.list_tools() == ["a", "b"]
