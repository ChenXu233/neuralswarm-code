import os
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from neuralswarm.core.concurrency import HashConflict, HashGuard
from neuralswarm.core.scheduler.worker import WorkerAgent


@pytest.fixture
def worktree_path(tmp_path):
    """返回临时 worktree 路径。"""
    return str(tmp_path)


@pytest.fixture
def guard(worktree_path):
    """创建 HashGuard 实例。"""
    return HashGuard(worktree_path=worktree_path)


@pytest.fixture
def agent_id():
    return uuid4()


@pytest.fixture
def worker(agent_id, worktree_path, guard):
    """创建 WorkerAgent 实例。"""
    return WorkerAgent(
        agent_id=agent_id,
        worktree_path=worktree_path,
        hash_guard=guard,
    )


# ── execute_subtask: file_edit (成功) ─────────────────────────────────


@pytest.mark.asyncio
@patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock)
async def test_file_edit_success(mock_git, worker, worktree_path):
    """file_edit 应读取文件、写入新内容并返回成功。"""
    file_path = "edit.txt"
    full_path = os.path.join(worktree_path, file_path)

    # 创建初始文件
    with open(full_path, "w", encoding="utf-8") as f:
        f.write("original content")

    result = await worker.execute_subtask({
        "type": "file_edit",
        "path": file_path,
        "content": "updated content",
    })

    assert result["success"] is True
    assert result["conflict"] is None
    assert "updated successfully" in result["output"]

    # 验证文件内容
    with open(full_path, "r", encoding="utf-8") as f:
        assert f.read() == "updated content"


# ── execute_subtask: file_edit (冲突) ─────────────────────────────────


@pytest.mark.asyncio
async def test_file_edit_conflict(worker, worktree_path):
    """file_edit 哈希冲突时应返回冲突信息。"""
    file_path = "conflict.txt"
    full_path = os.path.join(worktree_path, file_path)

    # 创建初始文件
    with open(full_path, "w", encoding="utf-8") as f:
        f.write("version 1")

    # 模拟外部修改：在 worker 读取后、写入前修改文件
    # 通过在 hash_guard.read 和 hash_guard.write 之间插入修改来实现
    original_write = worker.hash_guard.write

    async def intercept_write(path, content, aid):
        # 此时 read 已经记录了 "version 1" 的哈希
        # 在写入前外部修改文件
        with open(full_path, "w", encoding="utf-8") as f:
            f.write("modified by someone else")
        return await original_write(path, content, aid)

    worker.hash_guard.write = intercept_write

    result = await worker.execute_subtask({
        "type": "file_edit",
        "path": file_path,
        "content": "version 2 by worker",
    })

    assert result["success"] is False
    assert result["conflict"] is not None
    assert isinstance(result["conflict"], HashConflict)
    assert result["conflict"].file_path == file_path
    assert result["conflict"].expected_hash == HashGuard.compute_hash("version 1")
    assert result["conflict"].actual_hash == HashGuard.compute_hash("modified by someone else")

    # 恢复原始 write 方法
    worker.hash_guard.write = original_write


# ── execute_subtask: file_create ──────────────────────────────────────


@pytest.mark.asyncio
@patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock)
async def test_file_create_success(mock_git, worker, worktree_path):
    """file_create 应创建新文件并返回成功。"""
    file_path = "new_file.txt"
    full_path = os.path.join(worktree_path, file_path)

    result = await worker.execute_subtask({
        "type": "file_create",
        "path": file_path,
        "content": "brand new content",
    })

    assert result["success"] is True
    assert result["conflict"] is None
    assert "created successfully" in result["output"]

    with open(full_path, "r", encoding="utf-8") as f:
        assert f.read() == "brand new content"


@pytest.mark.asyncio
@patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock)
async def test_file_create_nested_path(mock_git, worker, worktree_path):
    """file_create 嵌套路径应自动创建中间目录。"""
    file_path = "deep/nested/dir/file.py"
    full_path = os.path.join(worktree_path, file_path)

    result = await worker.execute_subtask({
        "type": "file_create",
        "path": file_path,
        "content": "print('hello')",
    })

    assert result["success"] is True
    assert os.path.exists(full_path)

    with open(full_path, "r", encoding="utf-8") as f:
        assert f.read() == "print('hello')"


# ── execute_subtask: shell ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_shell_success(worker, worktree_path):
    """shell 命令成功时应返回输出。"""
    result = await worker.execute_subtask({
        "type": "shell",
        "command": "echo hello",
    })

    assert result["success"] is True
    assert "hello" in result["output"]
    assert result["conflict"] is None


@pytest.mark.asyncio
async def test_shell_failure(worker):
    """shell 命令失败时应返回错误信息。"""
    result = await worker.execute_subtask({
        "type": "shell",
        "command": "exit 1",
    })

    assert result["success"] is False
    assert result["conflict"] is None


# ── execute_subtask: unknown type ─────────────────────────────────────


@pytest.mark.asyncio
async def test_unknown_subtask_type(worker):
    """未知 subtask 类型应返回失败。"""
    result = await worker.execute_subtask({
        "type": "unknown_type",
    })

    assert result["success"] is False
    assert "Unknown subtask type" in result["output"]
    assert result["conflict"] is None


# ── execute_subtask: file_edit 异常处理 ────────────────────────────────


@pytest.mark.asyncio
async def test_file_edit_read_error(worker):
    """file_edit 读取不存在的文件应返回失败。"""
    result = await worker.execute_subtask({
        "type": "file_edit",
        "path": "nonexistent.txt",
        "content": "content",
    })

    assert result["success"] is False
    assert result["conflict"] is None


@pytest.mark.asyncio
async def test_file_edit_path_traversal(worker):
    """file_edit 路径穿越应返回失败。"""
    result = await worker.execute_subtask({
        "type": "file_edit",
        "path": "../../etc/passwd",
        "content": "malicious",
    })

    assert result["success"] is False
    assert result["conflict"] is None


# ── execute_subtask: file_create 路径穿越 ─────────────────────────────


@pytest.mark.asyncio
async def test_file_create_path_traversal(worker):
    """file_create 路径穿越应返回失败。"""
    result = await worker.execute_subtask({
        "type": "file_create",
        "path": "../../etc/passwd",
        "content": "malicious",
    })

    assert result["success"] is False
    assert result["conflict"] is None
