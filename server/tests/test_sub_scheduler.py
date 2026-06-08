import os
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from neuralswarm.core.concurrency import HashGuard
from neuralswarm.core.scheduler.central import CentralScheduler
from neuralswarm.core.scheduler.sub_scheduler import SubSchedulerAgent


@pytest.fixture
def agent_id():
    return uuid4()


@pytest.fixture
def task_id():
    return uuid4()


@pytest.fixture
def worktree_path(tmp_path):
    return str(tmp_path)


@pytest.fixture
def hash_guard(worktree_path):
    return HashGuard(worktree_path=worktree_path)


@pytest.fixture
def central_scheduler():
    agent_pool = MagicMock()
    worktree_manager = MagicMock()
    return CentralScheduler(
        agent_pool=agent_pool,
        worktree_manager=worktree_manager,
    )


@pytest.fixture
def sub_scheduler(agent_id, task_id, central_scheduler, hash_guard):
    return SubSchedulerAgent(
        agent_id=agent_id,
        task_id=task_id,
        central_scheduler=central_scheduler,
        hash_guard=hash_guard,
    )


# ── analyze_task 测试 ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_analyze_task_returns_plan(sub_scheduler):
    """analyze_task 应返回包含步骤的计划列表。"""
    plan = await sub_scheduler.analyze_task("Create a hello world script")

    assert isinstance(plan, list)
    assert len(plan) > 0

    # 验证每个步骤都有必要字段
    for step in plan:
        assert "type" in step
        assert "description" in step
        assert "is_simple" in step


@pytest.mark.asyncio
async def test_analyze_task_stores_plan(sub_scheduler):
    """analyze_task 应将计划存储在 self.plan 中。"""
    plan = await sub_scheduler.analyze_task("Test task")
    assert sub_scheduler.plan == plan


@pytest.mark.asyncio
async def test_analyze_task_prompt_in_description(sub_scheduler):
    """analyze_task 生成的步骤描述应包含用户 prompt。"""
    prompt = "Build a REST API"
    plan = await sub_scheduler.analyze_task(prompt)

    assert any(prompt in step["description"] for step in plan)


# ── execute_step 测试 ─────────────────────────────────────────────────


@pytest.mark.asyncio
@patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock)
async def test_execute_step_file_create(mock_git, sub_scheduler, worktree_path):
    """execute_step 应通过 WorkerAgent 执行 file_create。"""
    step = {
        "type": "file_create",
        "path": "test.txt",
        "content": "hello world",
        "is_simple": True,
    }

    result = await sub_scheduler.execute_step(step)

    assert result["success"] is True
    assert result["conflict"] is None

    # 验证文件已创建
    full_path = os.path.join(worktree_path, "test.txt")
    with open(full_path, "r", encoding="utf-8") as f:
        assert f.read() == "hello world"


@pytest.mark.asyncio
async def test_execute_step_shell(sub_scheduler):
    """execute_step 应通过 WorkerAgent 执行 shell 命令。"""
    step = {
        "type": "shell",
        "command": "echo test_output",
        "is_simple": True,
    }

    result = await sub_scheduler.execute_step(step)

    assert result["success"] is True
    assert "test_output" in result["output"]


@pytest.mark.asyncio
@patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock)
async def test_execute_step_file_edit(mock_git, sub_scheduler, worktree_path):
    """execute_step 应通过 WorkerAgent 执行 file_edit。"""
    # 先创建初始文件
    file_path = "edit_test.txt"
    full_path = os.path.join(worktree_path, file_path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write("original")

    step = {
        "type": "file_edit",
        "path": file_path,
        "content": "modified",
        "is_simple": True,
    }

    result = await sub_scheduler.execute_step(step)

    assert result["success"] is True
    with open(full_path, "r", encoding="utf-8") as f:
        assert f.read() == "modified"


# ── execute_plan 测试 ─────────────────────────────────────────────────


@pytest.mark.asyncio
@patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock)
async def test_execute_plan_simple_steps(mock_git, sub_scheduler):
    """execute_plan 应执行所有 is_simple 步骤。"""
    plan = [
        {
            "type": "shell",
            "command": "echo step1",
            "is_simple": True,
        },
        {
            "type": "shell",
            "command": "echo step2",
            "is_simple": True,
        },
    ]

    result = await sub_scheduler.execute_plan(plan)

    assert result["success"] is True
    assert len(result["results"]) == 2
    assert len(result["errors"]) == 0
    assert "step1" in result["results"][0]["output"]
    assert "step2" in result["results"][1]["output"]


@pytest.mark.asyncio
async def test_execute_plan_with_failed_step(sub_scheduler):
    """execute_plan 在某步骤失败时应记录错误但仍返回结果。"""
    plan = [
        {
            "type": "shell",
            "command": "echo success",
            "is_simple": True,
        },
        {
            "type": "shell",
            "command": "exit 1",
            "is_simple": True,
        },
    ]

    result = await sub_scheduler.execute_plan(plan)

    assert result["success"] is False
    assert len(result["results"]) == 2
    assert len(result["errors"]) == 1
    assert result["results"][0]["success"] is True
    assert result["results"][1]["success"] is False


@pytest.mark.asyncio
async def test_execute_plan_complex_steps_use_workers(sub_scheduler):
    """execute_plan 应将非 simple 步骤分配给 request_workers。"""
    plan = [
        {
            "type": "shell",
            "command": "echo worker_task",
            "is_simple": False,
        },
    ]

    result = await sub_scheduler.execute_plan(plan)

    assert result["success"] is True
    assert len(result["results"]) == 1
    assert "worker_task" in result["results"][0]["output"]


@pytest.mark.asyncio
async def test_execute_plan_mixed_steps(sub_scheduler):
    """execute_plan 应正确处理 simple 和 complex 混合步骤。"""
    plan = [
        {
            "type": "shell",
            "command": "echo simple",
            "is_simple": True,
        },
        {
            "type": "shell",
            "command": "echo complex",
            "is_simple": False,
        },
    ]

    result = await sub_scheduler.execute_plan(plan)

    assert result["success"] is True
    assert len(result["results"]) == 2


@pytest.mark.asyncio
async def test_execute_plan_empty(sub_scheduler):
    """execute_plan 空计划应返回成功。"""
    result = await sub_scheduler.execute_plan([])

    assert result["success"] is True
    assert len(result["results"]) == 0
    assert len(result["errors"]) == 0


# ── request_workers 测试 ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_request_workers_executes_subtasks(sub_scheduler):
    """request_workers 应执行所有子任务并返回结果。"""
    subtasks = [
        {
            "type": "shell",
            "command": "echo worker1",
        },
        {
            "type": "shell",
            "command": "echo worker2",
        },
    ]

    results = await sub_scheduler.request_workers(subtasks)

    assert len(results) == 2
    assert all(r["success"] for r in results)
    assert "worker1" in results[0]["output"]
    assert "worker2" in results[1]["output"]


@pytest.mark.asyncio
async def test_request_workers_handles_failure(sub_scheduler):
    """request_workers 在子任务失败时应继续执行其余任务。"""
    subtasks = [
        {
            "type": "shell",
            "command": "echo ok",
        },
        {
            "type": "shell",
            "command": "exit 1",
        },
    ]

    results = await sub_scheduler.request_workers(subtasks)

    assert len(results) == 2
    assert results[0]["success"] is True
    assert results[1]["success"] is False


@pytest.mark.asyncio
async def test_request_workers_empty_list(sub_scheduler):
    """request_workers 空列表应返回空结果。"""
    results = await sub_scheduler.request_workers([])
    assert results == []
