"""E2E 测试：Happy Path - 任务提交到完成。"""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from neuralswarm.core.concurrency.hash_guard import HashGuard
from neuralswarm.core.scheduler.sub_scheduler import SubSchedulerAgent
from neuralswarm.models.enums import AgentStatus


@pytest.mark.asyncio
async def test_simple_task_happy_path(
    central_scheduler, worktree_manager, mock_agent_repo, conflict_manager, fake_llm_simple
):
    """场景 1：简单任务 - LLM 生成计划 → 串行执行 → 完成 → worktree 合并。"""
    task_id = uuid4()
    project_id = uuid4()
    agent_id = uuid4()

    # 1. 提交任务 → 创建 worktree + sub-scheduler
    runtime = await central_scheduler.submit_task(
        task_id=task_id,
        project_id=project_id,
        agent_repo=mock_agent_repo,
        prompt="Create a hello world script",
        llm_config={"model": "test"},
        tools=["shell"],
    )
    assert runtime is not None
    assert task_id in central_scheduler.task_hash_guards

    # 2. 创建 Sub-scheduler（带 LLM）
    hash_guard = central_scheduler.task_hash_guards[task_id]
    sub_scheduler = SubSchedulerAgent(
        agent_id=agent_id,
        task_id=task_id,
        central_scheduler=central_scheduler,
        hash_guard=hash_guard,
        conflict_manager=conflict_manager,
        llm_gateway=fake_llm_simple,
        agent_repo=mock_agent_repo,
    )

    # 3. 分析任务 → 生成计划
    plan = await sub_scheduler.analyze_task("Create a hello world script")
    assert len(plan) == 1
    assert plan[0]["type"] == "shell"

    # 4. 执行计划
    result = await sub_scheduler.execute_plan(plan)
    assert result["success"] is True
    assert len(result["results"]) == 1
    assert "hello from LLM" in result["results"][0]["output"]

    # 5. 完成任务 → 合并 worktree
    await central_scheduler.complete_task(task_id, agent_repo=mock_agent_repo)
    assert task_id not in central_scheduler.task_hash_guards
    assert task_id not in central_scheduler.task_agents


@pytest.mark.asyncio
async def test_file_operations_happy_path(
    central_scheduler, worktree_manager, mock_agent_repo, conflict_manager, fake_llm_file_ops
):
    """场景 1b：文件操作任务 - 创建文件 → 编辑文件 → 完成。"""
    task_id = uuid4()
    project_id = uuid4()
    agent_id = uuid4()

    # 提交任务
    runtime = await central_scheduler.submit_task(
        task_id=task_id,
        project_id=project_id,
        agent_repo=mock_agent_repo,
        prompt="Create and edit a Python file",
        llm_config={"model": "test"},
        tools=["file_ops"],
    )

    hash_guard = central_scheduler.task_hash_guards[task_id]
    sub_scheduler = SubSchedulerAgent(
        agent_id=agent_id,
        task_id=task_id,
        central_scheduler=central_scheduler,
        hash_guard=hash_guard,
        conflict_manager=conflict_manager,
        llm_gateway=fake_llm_file_ops,
        agent_repo=mock_agent_repo,
    )

    # 分析 + 执行
    plan = await sub_scheduler.analyze_task("Create and edit a Python file")
    result = await sub_scheduler.execute_plan(plan)

    assert result["success"] is True
    assert len(result["results"]) == 2

    # 验证文件内容
    worktree = worktree_manager.get_worktree(task_id)
    file_path = os.path.join(worktree.path, "src", "hello.py")
    assert os.path.exists(file_path)
    with open(file_path, "r") as f:
        assert f.read() == "print('hello world edited')"

    # 清理
    await central_scheduler.complete_task(task_id, agent_repo=mock_agent_repo)
