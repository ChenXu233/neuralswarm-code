"""E2E 测试：冲突检测 + 用户决策。"""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from neuralswarm.core.concurrency.hash_guard import HashGuard, HashConflict
from neuralswarm.core.concurrency.conflict_manager import ConflictManager
from neuralswarm.core.scheduler.worker import WorkerAgent


@pytest.mark.asyncio
async def test_hash_conflict_detection(temp_git_repo):
    """场景 3：两个独立 HashGuard 读同一文件 → Guard-1 写入成功 → Guard-2 写入冲突。"""
    worktree_path = str(temp_git_repo)

    # 创建初始文件
    file_path = os.path.join(worktree_path, "shared.txt")
    with open(file_path, "w") as f:
        f.write("original content")

    # 两个独立的 HashGuard（模拟两个独立的 Agent）
    guard1 = HashGuard(worktree_path=worktree_path)
    guard2 = HashGuard(worktree_path=worktree_path)

    # 两个 Guard 都读取文件（各自记录哈希）
    content1 = await guard1.read("shared.txt")
    content2 = await guard2.read("shared.txt")
    assert content1 == "original content"
    assert content2 == "original content"

    # Guard-1 写入成功
    agent1_id = uuid4()
    with patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock):
        result1 = await guard1.write("shared.txt", "modified by agent-1", agent1_id)
    assert result1 is True

    # Guard-2 写入冲突（它的 recorded_hash 仍然是 original content 的哈希）
    agent2_id = uuid4()
    result2 = await guard2.write("shared.txt", "modified by agent-2", agent2_id)
    assert isinstance(result2, HashConflict)
    assert result2.file_path == "shared.txt"
    assert result2.expected_hash != result2.actual_hash
    assert result2.new_content == "modified by agent-2"

    # 验证文件内容未被覆盖
    with open(file_path, "r") as f:
        assert f.read() == "modified by agent-1"


@pytest.mark.asyncio
async def test_conflict_notification_and_resolution():
    """场景 4：冲突发生 → ConflictManager 通知 → 用户决策 → 执行动作。"""
    manager = ConflictManager()
    task_id = uuid4()

    # 订阅冲突事件
    queue = manager.subscribe(task_id)

    # 创建 Conflict 模型（模拟 DB 记录）
    from neuralswarm.models.conflict import Conflict as ConflictModel, ConflictStatus, ConflictAction

    conflict_model = ConflictModel(
        id=uuid4(),
        task_id=task_id,
        file_path="src/main.py",
        agent_id=uuid4(),
        other_agent_id=uuid4(),
        old_hash="abc123",
        current_hash="def456",
        current_content="current version",
        new_content="new version",
        status=ConflictStatus.PENDING,
    )

    # 注册到 manager
    await manager.detect(conflict_model)

    # 验证队列收到通知（Conflict 对象）
    assert not queue.empty()
    event = await queue.get()
    assert event.id == conflict_model.id
    assert event.file_path == "src/main.py"

    # 用户决策：re_read
    resolved = await manager.resolve(conflict_model.id, ConflictAction.RE_READ)
    assert resolved.status == ConflictStatus.RESOLVED
    assert resolved.action == ConflictAction.RE_READ

    # 验证 pending 中已移除
    assert conflict_model.id not in manager.pending_conflicts


@pytest.mark.asyncio
async def test_conflict_worker_integration(temp_git_repo):
    """场景 3b：WorkerAgent 使用 HashGuard 进行文件编辑。"""
    worktree_path = str(temp_git_repo)

    # 创建初始文件
    file_path = os.path.join(worktree_path, "conflict_test.txt")
    with open(file_path, "w") as f:
        f.write("original")

    guard = HashGuard(worktree_path=worktree_path)

    # Worker 读取 + 编辑文件
    worker = WorkerAgent(
        agent_id=uuid4(),
        worktree_path=worktree_path,
        hash_guard=guard,
    )
    result = await worker.execute_subtask({
        "type": "file_edit",
        "path": "conflict_test.txt",
        "content": "modified by worker",
    })
    assert result["success"] is True
    assert result["conflict"] is None

    # 验证文件内容已更新
    with open(file_path, "r") as f:
        assert f.read() == "modified by worker"
