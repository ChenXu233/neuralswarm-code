import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from neuralswarm.core.scheduler import AgentPool, AgentRuntime
from neuralswarm.models.enums import AgentStatus, AgentType


def _make_mock_agent_model(agent_id=None, agent_type=AgentType.WORKER):
    """创建 mock Agent 模型。"""
    agent = MagicMock()
    agent.id = agent_id or uuid4()
    agent.project_id = uuid4()
    agent.agent_type = agent_type
    agent.status = AgentStatus.IDLE
    agent.task_id = uuid4()
    agent.parent_id = None
    agent.tools = ["file_ops"]
    agent.llm_config = {"provider": "openai", "model": "gpt-4"}
    agent.worktree_path = "/tmp/worktree"
    return agent


def _make_mock_repo():
    """创建 mock AgentRepository。"""
    repo = AsyncMock()
    return repo


# ── AgentRuntime 测试 ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_agent_runtime_start():
    """start() 应更新状态为 RUNNING。"""
    model = _make_mock_agent_model()
    runtime = AgentRuntime(agent_model=model)

    repo = _make_mock_repo()
    await runtime.start(repo)

    assert runtime.status == AgentStatus.RUNNING
    assert runtime._started is True
    repo.update_status.assert_called_once_with(model.id, AgentStatus.RUNNING)


@pytest.mark.asyncio
async def test_agent_runtime_stop_completed():
    """stop() 默认将状态设为 COMPLETED。"""
    model = _make_mock_agent_model()
    runtime = AgentRuntime(agent_model=model)

    repo = _make_mock_repo()
    await runtime.stop(repo)

    assert runtime.status == AgentStatus.COMPLETED
    assert runtime._started is False
    repo.update_status.assert_called_once_with(model.id, AgentStatus.COMPLETED)


@pytest.mark.asyncio
async def test_agent_runtime_stop_failed():
    """stop() 支持设置 FAILED 状态。"""
    model = _make_mock_agent_model()
    runtime = AgentRuntime(agent_model=model)

    repo = _make_mock_repo()
    await runtime.stop(repo, final_status=AgentStatus.FAILED)

    assert runtime.status == AgentStatus.FAILED
    repo.update_status.assert_called_once_with(model.id, AgentStatus.FAILED)


def test_agent_runtime_exposes_model_fields():
    """AgentRuntime 应暴露 model 的 id、type、status。"""
    model = _make_mock_agent_model(agent_type=AgentType.SCHEDULER)
    runtime = AgentRuntime(agent_model=model)

    assert runtime.id == model.id
    assert runtime.type == AgentType.SCHEDULER
    assert runtime.status == AgentStatus.IDLE


# ── AgentPool 测试 ──────────────────────────────────────────────────


@pytest.mark.asyncio
@patch("neuralswarm.core.scheduler.agent_pool.Agent")
async def test_create_agent_registers_in_pool(MockAgent):
    """create_agent 应在 DB 创建记录并注册到 active_agents。"""
    mock_agent_instance = _make_mock_agent_model()
    MockAgent.return_value = mock_agent_instance

    pool = AgentPool(max_concurrent=3)
    repo = _make_mock_repo()

    runtime = await pool.create_agent(
        agent_repo=repo,
        agent_type=AgentType.WORKER,
        task_id=uuid4(),
        project_id=uuid4(),
        worktree_path="/tmp/wt",
        llm_config={"provider": "openai", "model": "gpt-4"},
        tools=["shell"],
        name="test-agent",
    )

    assert isinstance(runtime, AgentRuntime)
    assert runtime.id in pool.active_agents
    assert pool.active_agents[runtime.id] is runtime

    # 验证 DB 操作
    repo.create_agent.assert_called_once_with(mock_agent_instance)


@pytest.mark.asyncio
@patch("neuralswarm.core.scheduler.agent_pool.Agent")
async def test_create_agent_with_parent(MockAgent):
    """create_agent 支持 parent_id 参数。"""
    mock_agent_instance = _make_mock_agent_model()
    MockAgent.return_value = mock_agent_instance

    pool = AgentPool()
    repo = _make_mock_repo()
    parent_id = uuid4()

    await pool.create_agent(
        agent_repo=repo,
        agent_type=AgentType.WORKER,
        task_id=uuid4(),
        project_id=uuid4(),
        worktree_path="/tmp/wt",
        llm_config={},
        tools=[],
        parent_id=parent_id,
    )

    # 验证 Agent 构造时传入了 parent_id
    call_kwargs = MockAgent.call_args[1]
    assert call_kwargs["parent_id"] == parent_id


@pytest.mark.asyncio
@patch("neuralswarm.core.scheduler.agent_pool.Agent")
async def test_create_agent_default_name(MockAgent):
    """未指定 name 时应使用 agent_type 生成默认名称。"""
    mock_agent_instance = _make_mock_agent_model()
    MockAgent.return_value = mock_agent_instance

    pool = AgentPool()
    repo = _make_mock_repo()

    await pool.create_agent(
        agent_repo=repo,
        agent_type=AgentType.SCHEDULER,
        task_id=uuid4(),
        project_id=uuid4(),
        worktree_path="/tmp/wt",
        llm_config={},
        tools=[],
    )

    call_kwargs = MockAgent.call_args[1]
    assert call_kwargs["name"] == "agent-scheduler"


@pytest.mark.asyncio
@patch("neuralswarm.core.scheduler.agent_pool.Agent")
async def test_create_agent_passes_all_params(MockAgent):
    """create_agent 应将所有参数传递给 Agent 构造函数。"""
    mock_agent_instance = _make_mock_agent_model()
    MockAgent.return_value = mock_agent_instance

    pool = AgentPool()
    repo = _make_mock_repo()
    task_id = uuid4()
    project_id = uuid4()

    await pool.create_agent(
        agent_repo=repo,
        agent_type=AgentType.WORKER,
        task_id=task_id,
        project_id=project_id,
        worktree_path="/tmp/custom",
        llm_config={"provider": "anthropic"},
        tools=["shell", "file_ops"],
        name="my-agent",
    )

    call_kwargs = MockAgent.call_args[1]
    assert call_kwargs["project_id"] == project_id
    assert call_kwargs["task_id"] == task_id
    assert call_kwargs["agent_type"] == AgentType.WORKER
    assert call_kwargs["worktree_path"] == "/tmp/custom"
    assert call_kwargs["llm_config"] == {"provider": "anthropic"}
    assert call_kwargs["tools"] == ["shell", "file_ops"]
    assert call_kwargs["name"] == "my-agent"


@pytest.mark.asyncio
@patch("neuralswarm.core.scheduler.agent_pool.Agent")
async def test_destroy_agent_removes_from_pool(MockAgent):
    """destroy_agent 应从 active_agents 移除并更新 DB 状态。"""
    mock_agent_instance = _make_mock_agent_model()
    MockAgent.return_value = mock_agent_instance

    pool = AgentPool()
    repo = _make_mock_repo()

    runtime = await pool.create_agent(
        agent_repo=repo,
        agent_type=AgentType.WORKER,
        task_id=uuid4(),
        project_id=uuid4(),
        worktree_path="/tmp/wt",
        llm_config={},
        tools=[],
    )
    agent_id = runtime.id
    assert agent_id in pool.active_agents

    await pool.destroy_agent(agent_id, repo)

    assert agent_id not in pool.active_agents
    repo.update_status.assert_called_with(agent_id, AgentStatus.COMPLETED)


@pytest.mark.asyncio
@patch("neuralswarm.core.scheduler.agent_pool.Agent")
async def test_destroy_agent_failed(MockAgent):
    """destroy_agent(failed=True) 应将状态设为 FAILED。"""
    mock_agent_instance = _make_mock_agent_model()
    MockAgent.return_value = mock_agent_instance

    pool = AgentPool()
    repo = _make_mock_repo()

    runtime = await pool.create_agent(
        agent_repo=repo,
        agent_type=AgentType.WORKER,
        task_id=uuid4(),
        project_id=uuid4(),
        worktree_path="/tmp/wt",
        llm_config={},
        tools=[],
    )

    await pool.destroy_agent(runtime.id, repo, failed=True)

    assert runtime.id not in pool.active_agents
    repo.update_status.assert_called_with(runtime.id, AgentStatus.FAILED)


@pytest.mark.asyncio
async def test_destroy_agent_not_found():
    """destroy_agent 对不存在的 agent_id 应静默处理。"""
    pool = AgentPool()
    repo = _make_mock_repo()

    # 不应抛异常
    await pool.destroy_agent(uuid4(), repo)


def test_get_agent():
    """get_agent 应返回对应的 runtime。"""
    pool = AgentPool()
    model = _make_mock_agent_model()
    runtime = AgentRuntime(agent_model=model)
    pool.active_agents[model.id] = runtime

    assert pool.get_agent(model.id) is runtime
    assert pool.get_agent(uuid4()) is None


def test_list_agents():
    """list_agents 应返回所有活跃 Agent。"""
    pool = AgentPool()
    ids = set()
    for _ in range(3):
        model = _make_mock_agent_model()
        runtime = AgentRuntime(agent_model=model)
        pool.active_agents[model.id] = runtime
        ids.add(model.id)

    agents = pool.list_agents()
    assert len(agents) == 3
    assert {a.id for a in agents} == ids


@pytest.mark.asyncio
async def test_execute_with_limit():
    """execute_with_limit 应在信号量限制下执行协程。"""
    pool = AgentPool(max_concurrent=2)
    agent_id = uuid4()

    async def return_42():
        return 42

    result = await pool.execute_with_limit(agent_id, return_42())
    assert result == 42


@pytest.mark.asyncio
async def test_execute_with_limit_concurrency():
    """并发数不应超过 max_concurrent。"""
    pool = AgentPool(max_concurrent=1)
    running = 0
    max_running = 0

    async def work(_agent_id):
        nonlocal running, max_running
        running += 1
        max_running = max(max_running, running)
        await asyncio.sleep(0.05)
        running -= 1

    tasks = [
        pool.execute_with_limit(uuid4(), work(uuid4()))
        for _ in range(5)
    ]
    await asyncio.gather(*tasks)

    # max_concurrent=1, 所以同一时刻最多 1 个在运行
    assert max_running <= 1


@pytest.mark.asyncio
async def test_execute_with_limit_releases_on_exception():
    """即使协程抛异常，信号量也应释放。"""
    pool = AgentPool(max_concurrent=1)
    agent_id = uuid4()

    async def failing():
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        await pool.execute_with_limit(agent_id, failing())

    # 信号量应已释放，可以再次获取
    async def return_ok():
        return "ok"

    result = await pool.execute_with_limit(agent_id, return_ok())
    assert result == "ok"
