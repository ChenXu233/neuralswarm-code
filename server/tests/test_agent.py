import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from neuralswarm.core.agent import Agent
from neuralswarm.core.tool_executor import ToolExecutor
from neuralswarm.core.context_manager import ContextManager
from neuralswarm.services.llm.types import LLMResponse, ToolCall
from neuralswarm.models.enums import AgentStatus


@pytest.fixture
def mock_llm_gateway():
    gateway = AsyncMock()
    gateway.chat.return_value = LLMResponse(
        content="Task completed",
        model="test-model",
        usage={"total_tokens": 100},
        finish_reason="stop",
    )
    return gateway


@pytest.fixture
def mock_agent_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def tool_executor():
    return ToolExecutor()


@pytest.fixture
def context_manager():
    return ContextManager()


@pytest.fixture
def agent(mock_llm_gateway, mock_agent_repo, tool_executor, context_manager):
    return Agent(
        agent_id=uuid4(),
        project_id=uuid4(),
        tools=[],
        llm_gateway=mock_llm_gateway,
        agent_repo=mock_agent_repo,
        tool_executor=tool_executor,
        context_manager=context_manager,
    )


@pytest.mark.asyncio
async def test_agent_execute_simple(agent, mock_llm_gateway, mock_agent_repo):
    result = await agent.execute(
        task="Hello",
        llm_id=uuid4(),
        provider="openai",
        model_id="gpt-4",
    )
    assert result == "Task completed"
    mock_agent_repo.update_status.assert_any_call(agent.agent_id, AgentStatus.RUNNING)
    mock_agent_repo.update_status.assert_any_call(agent.agent_id, AgentStatus.IDLE)


@pytest.mark.asyncio
async def test_agent_execute_updates_context(agent, context_manager):
    await agent.execute(
        task="Hello",
        llm_id=uuid4(),
        provider="openai",
        model_id="gpt-4",
    )
    messages = context_manager.get_messages()
    assert len(messages) == 2  # user + assistant
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Task completed"


@pytest.mark.asyncio
async def test_agent_execute_with_tool_calls(agent, mock_llm_gateway, mock_agent_repo, tool_executor):
    # First call returns tool call, second returns final response
    mock_llm_gateway.chat.side_effect = [
        LLMResponse(content="", model="test", usage={"total_tokens": 50}, tool_calls=[
            ToolCall(id="call_001", name="add", arguments={"a": 1, "b": 2}),
        ]),
        LLMResponse(content="Result is 3", model="test", usage={"total_tokens": 80}),
    ]

    async def add(a: int, b: int) -> str:
        return str(a + b)
    tool_executor.register("add", add)

    result = await agent.execute(
        task="Calculate 1+2",
        llm_id=uuid4(),
        provider="openai",
        model_id="gpt-4",
    )
    assert result == "Result is 3"
