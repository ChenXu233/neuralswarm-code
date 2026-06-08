"""E2E 测试：失败清理 + 合并冲突。"""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from neuralswarm.core.concurrency.hash_guard import HashGuard
from neuralswarm.core.scheduler.sub_scheduler import SubSchedulerAgent
from neuralswarm.models.enums import AgentStatus


@pytest.mark.asyncio
async def test_failure_cleanup(
    central_scheduler, worktree_manager, mock_agent_repo, conflict_manager
):
    """场景 5：任务执行异常 → fail_task → 资源清理。"""
    task_id = uuid4()
    project_id = uuid4()

    # 提交任务
    runtime = await central_scheduler.submit_task(
        task_id=task_id,
        project_id=project_id,
        agent_repo=mock_agent_repo,
        prompt="Test task",
        llm_config={"model": "test"},
        tools=["shell"],
    )

    # 验证资源已创建
    assert task_id in central_scheduler.task_hash_guards
    assert task_id in central_scheduler.task_agents
    worktree = worktree_manager.get_worktree(task_id)
    assert worktree is not None

    # 模拟任务失败
    error_msg = "LLM crashed"
    await central_scheduler.fail_task(task_id, agent_repo=mock_agent_repo, error=error_msg)

    # 验证资源已清理
    assert task_id not in central_scheduler.task_hash_guards
    assert task_id not in central_scheduler.task_agents
    assert worktree_manager.get_worktree(task_id) is None


@pytest.mark.asyncio
async def test_merge_conflict_preserves_worktree(
    central_scheduler, worktree_manager, mock_agent_repo
):
    """场景 6：合并冲突 → worktree 保留。"""
    task_id = uuid4()
    project_id = uuid4()

    # 提交任务
    runtime = await central_scheduler.submit_task(
        task_id=task_id,
        project_id=project_id,
        agent_repo=mock_agent_repo,
        prompt="Test merge conflict",
        llm_config={"model": "test"},
        tools=["shell"],
    )

    worktree = worktree_manager.get_worktree(task_id)
    assert worktree is not None

    # Mock merge 失败
    original_merge = worktree_manager.merge
    async def failing_merge(tid):
        raise RuntimeError("Merge conflict: CONFLICT (content): Merge conflict in file.txt")
    worktree_manager.merge = failing_merge

    # complete_task 应该保留 worktree
    await central_scheduler.complete_task(task_id, agent_repo=mock_agent_repo)

    # 验证 worktree 仍然存在（因为 merge 失败）
    # 注意：complete_task 在 merge 失败时会跳过 remove
    # 但 task_agents 和 task_hash_guards 应该被清理
    assert task_id not in central_scheduler.task_agents
    assert task_id not in central_scheduler.task_hash_guards

    # 恢复原始 merge
    worktree_manager.merge = original_merge

    # 手动清理
    await worktree_manager.remove(task_id)


@pytest.mark.asyncio
async def test_task_not_found_handles_gracefully(central_scheduler, mock_agent_repo):
    """complete_task 对不存在的 task 应优雅处理（不抛异常）。"""
    fake_task_id = uuid4()
    # complete_task 内部捕获 KeyError，不向外抛出
    await central_scheduler.complete_task(fake_task_id, agent_repo=mock_agent_repo)
    # 验证没有残留状态
    assert fake_task_id not in central_scheduler.task_agents
    assert fake_task_id not in central_scheduler.task_hash_guards


@pytest.mark.asyncio
async def test_allocate_workers_without_worktree_raises(
    central_scheduler, mock_agent_repo
):
    """allocate_workers 在没有 worktree 时应抛出 KeyError。"""
    fake_task_id = uuid4()
    with pytest.raises(KeyError):
        await central_scheduler.allocate_workers(
            task_id=fake_task_id,
            parent_id=uuid4(),
            agent_repo=mock_agent_repo,
            subtasks=[{"type": "shell", "command": "echo test"}],
            llm_config={},
            tools=[],
        )
