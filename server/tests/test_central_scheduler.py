import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from neuralswarm.core.scheduler.agent_pool import AgentPool, AgentRuntime
from neuralswarm.core.scheduler.central import CentralScheduler
from neuralswarm.core.git.worktree import WorktreeManager, WorktreeInfo
from neuralswarm.core.concurrency.hash_guard import HashGuard
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


def _make_worktree_info(task_id=None):
    """创建 WorktreeInfo 实例。"""
    return WorktreeInfo(
        path="/tmp/worktrees/task-12345678",
        branch="ns/task-12345678",
        task_id=task_id or uuid4(),
    )


def _make_central_scheduler():
    """创建 CentralScheduler 实例，使用 mock 组件。"""
    agent_pool = AgentPool(max_concurrent=5)
    worktree_manager = MagicMock(spec=WorktreeManager)
    return CentralScheduler(
        agent_pool=agent_pool,
        worktree_manager=worktree_manager,
    )


# ── submit_task 测试 ──────────────────────────────────────────────


@pytest.mark.asyncio
@patch("neuralswarm.core.scheduler.agent_pool.Agent")
async def test_submit_task_creates_worktree_and_scheduler(MockAgent):
    """submit_task 应创建 worktree 和 scheduler agent。"""
    task_id = uuid4()
    project_id = uuid4()
    worktree_info = _make_worktree_info(task_id)

    mock_agent_instance = _make_mock_agent_model(agent_type=AgentType.SCHEDULER)
    MockAgent.return_value = mock_agent_instance

    scheduler = _make_central_scheduler()
    scheduler.worktree_manager.create = AsyncMock(return_value=worktree_info)
    scheduler.worktree_manager.get_worktree = MagicMock(return_value=worktree_info)

    repo = _make_mock_repo()
    # 让 repo.create_agent 返回传入的 agent 对象
    repo.create_agent = AsyncMock(side_effect=lambda agent: agent)

    runtime = await scheduler.submit_task(
        task_id=task_id,
        project_id=project_id,
        agent_repo=repo,
        prompt="Test prompt",
        llm_config={"provider": "openai", "model": "gpt-4"},
        tools=["file_ops"],
    )

    # 验证 worktree 创建
    scheduler.worktree_manager.create.assert_called_once_with(task_id)

    # 验证 Agent 创建
    assert isinstance(runtime, AgentRuntime)
    assert runtime.type == AgentType.SCHEDULER

    # 验证注册到 task_agents
    assert task_id in scheduler.task_agents
    assert runtime.id in scheduler.task_agents[task_id]

    # 验证 HashGuard 创建
    assert task_id in scheduler.task_hash_guards
    assert isinstance(scheduler.task_hash_guards[task_id], HashGuard)

    # 验证 Agent 启动
    assert runtime.status == AgentStatus.RUNNING


@pytest.mark.asyncio
@patch("neuralswarm.core.scheduler.agent_pool.Agent")
async def test_submit_task_default_agent_name(MockAgent):
    """submit_task 应为 scheduler agent 生成默认名称。"""
    task_id = uuid4()
    project_id = uuid4()
    worktree_info = _make_worktree_info(task_id)

    mock_agent_instance = _make_mock_agent_model(agent_type=AgentType.SCHEDULER)
    MockAgent.return_value = mock_agent_instance

    scheduler = _make_central_scheduler()
    scheduler.worktree_manager.create = AsyncMock(return_value=worktree_info)

    repo = _make_mock_repo()

    await scheduler.submit_task(
        task_id=task_id,
        project_id=project_id,
        agent_repo=repo,
        prompt="Test",
        llm_config={},
        tools=[],
    )

    # 验证 Agent 名称包含 task_id
    call_kwargs = MockAgent.call_args[1]
    assert f"scheduler-{task_id}" == call_kwargs["name"]


# ── allocate_workers 测试 ──────────────────────────────────────────


@pytest.mark.asyncio
@patch("neuralswarm.core.scheduler.agent_pool.Agent")
async def test_allocate_workers_creates_worker_agents(MockAgent):
    """allocate_workers 应为每个 subtask 创建 worker agent。"""
    task_id = uuid4()
    parent_id = uuid4()
    worktree_info = _make_worktree_info(task_id)

    subtasks = [
        {"name": "subtask-1", "project_id": uuid4()},
        {"name": "subtask-2", "project_id": uuid4()},
        {"name": "subtask-3", "project_id": uuid4()},
    ]

    mock_agents = [_make_mock_agent_model(agent_type=AgentType.WORKER) for _ in range(3)]
    MockAgent.side_effect = mock_agents

    scheduler = _make_central_scheduler()
    scheduler.worktree_manager.get_worktree = MagicMock(return_value=worktree_info)

    # 预先设置 task_agents
    scheduler.task_agents[task_id] = [parent_id]

    repo = _make_mock_repo()
    # 让 repo.create_agent 返回传入的 agent 对象
    repo.create_agent = AsyncMock(side_effect=lambda agent: agent)

    runtimes = await scheduler.allocate_workers(
        task_id=task_id,
        parent_id=parent_id,
        agent_repo=repo,
        subtasks=subtasks,
        llm_config={"provider": "openai", "model": "gpt-4"},
        tools=["file_ops"],
    )

    # 验证创建了 3 个 worker
    assert len(runtimes) == 3
    assert all(isinstance(r, AgentRuntime) for r in runtimes)
    assert all(r.type == AgentType.WORKER for r in runtimes)

    # 验证注册到 task_agents
    assert len(scheduler.task_agents[task_id]) == 4  # 1 parent + 3 workers

    # 验证所有 worker 已启动
    assert all(r.status == AgentStatus.RUNNING for r in runtimes)

    # 验证 parent_id 被传递
    for call in MockAgent.call_args_list:
        assert call[1]["parent_id"] == parent_id


@pytest.mark.asyncio
async def test_allocate_workers_no_worktree_raises():
    """allocate_workers 在 worktree 不存在时应抛出 KeyError。"""
    task_id = uuid4()

    scheduler = _make_central_scheduler()
    scheduler.worktree_manager.get_worktree = MagicMock(return_value=None)

    repo = _make_mock_repo()

    with pytest.raises(KeyError, match="No worktree found"):
        await scheduler.allocate_workers(
            task_id=task_id,
            parent_id=uuid4(),
            agent_repo=repo,
            subtasks=[{"name": "test", "project_id": uuid4()}],
            llm_config={},
            tools=[],
        )


# ── complete_task 测试 ────────────────────────────────────────────


@pytest.mark.asyncio
@patch("neuralswarm.core.scheduler.agent_pool.Agent")
async def test_complete_task_merges_and_cleans_up(MockAgent):
    """complete_task 应合并 worktree、销毁 agent、清理资源。"""
    task_id = uuid4()
    worktree_info = _make_worktree_info(task_id)

    mock_agent_instance = _make_mock_agent_model(agent_type=AgentType.SCHEDULER)
    MockAgent.return_value = mock_agent_instance

    scheduler = _make_central_scheduler()
    scheduler.worktree_manager.create = AsyncMock(return_value=worktree_info)
    scheduler.worktree_manager.merge = AsyncMock()
    scheduler.worktree_manager.remove = AsyncMock()

    repo = _make_mock_repo()

    # 先提交任务
    runtime = await scheduler.submit_task(
        task_id=task_id,
        project_id=uuid4(),
        agent_repo=repo,
        prompt="Test",
        llm_config={},
        tools=[],
    )
    agent_id = runtime.id

    # 完成任务
    await scheduler.complete_task(task_id, repo)

    # 验证 worktree 合并
    scheduler.worktree_manager.merge.assert_called_once_with(task_id)

    # 验证 Agent 已销毁
    assert agent_id not in scheduler.agent_pool.active_agents

    # 验证 HashGuard 已清理
    assert task_id not in scheduler.task_hash_guards

    # 验证 worktree 已删除
    scheduler.worktree_manager.remove.assert_called_once_with(task_id)

    # 验证 task_agents 已清理
    assert task_id not in scheduler.task_agents


@pytest.mark.asyncio
async def test_complete_task_preserves_worktree_on_merge_conflict():
    """complete_task 在合并冲突(RuntimeError)时应保留 worktree 不删除。"""
    task_id = uuid4()

    scheduler = _make_central_scheduler()
    scheduler.worktree_manager.merge = AsyncMock(side_effect=RuntimeError("merge conflict"))
    scheduler.worktree_manager.remove = AsyncMock()

    repo = _make_mock_repo()

    # 不应抛异常
    await scheduler.complete_task(task_id, repo)

    # worktree 不应被删除（保留未合并的提交）
    scheduler.worktree_manager.remove.assert_not_called()


@pytest.mark.asyncio
async def test_complete_task_removes_worktree_on_key_error():
    """complete_task 在 worktree 不存在(KeyError)时仍应尝试删除。"""
    task_id = uuid4()

    scheduler = _make_central_scheduler()
    scheduler.worktree_manager.merge = AsyncMock(side_effect=KeyError("not found"))
    scheduler.worktree_manager.remove = AsyncMock()

    repo = _make_mock_repo()

    # 不应抛异常
    await scheduler.complete_task(task_id, repo)

    # worktree 仍应被尝试删除
    scheduler.worktree_manager.remove.assert_called_once_with(task_id)


# ── fail_task 测试 ────────────────────────────────────────────────


@pytest.mark.asyncio
@patch("neuralswarm.core.scheduler.agent_pool.Agent")
async def test_fail_task_cleans_up_without_merging(MockAgent):
    """fail_task 应清理资源但不合并 worktree。"""
    task_id = uuid4()
    worktree_info = _make_worktree_info(task_id)

    mock_agent_instance = _make_mock_agent_model(agent_type=AgentType.WORKER)
    MockAgent.return_value = mock_agent_instance

    scheduler = _make_central_scheduler()
    scheduler.worktree_manager.create = AsyncMock(return_value=worktree_info)
    scheduler.worktree_manager.merge = AsyncMock()
    scheduler.worktree_manager.remove = AsyncMock()

    repo = _make_mock_repo()

    # 先提交任务
    runtime = await scheduler.submit_task(
        task_id=task_id,
        project_id=uuid4(),
        agent_repo=repo,
        prompt="Test",
        llm_config={},
        tools=[],
    )
    agent_id = runtime.id

    # 失败任务
    await scheduler.fail_task(task_id, repo, error="Test error")

    # 验证 worktree 未合并
    scheduler.worktree_manager.merge.assert_not_called()

    # 验证 Agent 已销毁（标记为 FAILED）
    assert agent_id not in scheduler.agent_pool.active_agents

    # 验证 HashGuard 已清理
    assert task_id not in scheduler.task_hash_guards

    # 验证 worktree 已删除
    scheduler.worktree_manager.remove.assert_called_once_with(task_id)

    # 验证 task_agents 已清理
    assert task_id not in scheduler.task_agents


@pytest.mark.asyncio
async def test_fail_task_handles_remove_failure():
    """fail_task 在删除 worktree 失败时应静默处理。"""
    task_id = uuid4()

    scheduler = _make_central_scheduler()
    scheduler.worktree_manager.remove = AsyncMock(side_effect=RuntimeError("remove failed"))

    repo = _make_mock_repo()

    # 不应抛异常
    await scheduler.fail_task(task_id, repo, error="Test error")


# ── get_task_agents 测试 ──────────────────────────────────────────


def test_get_task_agents_returns_agent_ids():
    """get_task_agents 应返回 task 的所有 agent ID。"""
    scheduler = _make_central_scheduler()
    task_id = uuid4()
    agent_ids = [uuid4(), uuid4(), uuid4()]

    scheduler.task_agents[task_id] = agent_ids

    result = scheduler.get_task_agents(task_id)
    assert result == agent_ids


def test_get_task_agents_returns_empty_list_for_unknown_task():
    """get_task_agents 对未知 task 应返回空列表。"""
    scheduler = _make_central_scheduler()

    result = scheduler.get_task_agents(uuid4())
    assert result == []


# ── get_hash_guard 测试 ───────────────────────────────────────────


def test_get_hash_guard_returns_guard():
    """get_hash_guard 应返回 task 的 HashGuard。"""
    scheduler = _make_central_scheduler()
    task_id = uuid4()
    guard = HashGuard(worktree_path="/tmp/test")

    scheduler.task_hash_guards[task_id] = guard

    result = scheduler.get_hash_guard(task_id)
    assert result is guard


def test_get_hash_guard_returns_none_for_unknown_task():
    """get_hash_guard 对未知 task 应返回 None。"""
    scheduler = _make_central_scheduler()

    result = scheduler.get_hash_guard(uuid4())
    assert result is None
