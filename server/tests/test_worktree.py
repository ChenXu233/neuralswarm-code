import os
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from neuralswarm.core.git import WorktreeInfo, WorktreeManager


def _make_worktree_info(task_id=None):
    """创建 mock WorktreeInfo。"""
    return WorktreeInfo(
        path="/tmp/worktrees/task-12345678",
        branch="ns/task-12345678",
        task_id=task_id or uuid4(),
    )


@pytest.fixture
def manager(tmp_path):
    """创建 WorktreeManager 实例，使用临时目录。"""
    return WorktreeManager(base_path=str(tmp_path))


@pytest.fixture
def task_id():
    return uuid4()


# ── WorktreeInfo 测试 ──────────────────────────────────────────────


def test_worktree_info_init():
    """WorktreeInfo 应正确存储属性。"""
    task_id = uuid4()
    info = WorktreeInfo(path="/tmp/wt", branch="ns/task-abc", task_id=task_id)

    assert info.path == "/tmp/wt"
    assert info.branch == "ns/task-abc"
    assert info.task_id == task_id


# ── WorktreeManager 测试 ──────────────────────────────────────────


def test_manager_init(tmp_path):
    """WorktreeManager 应正确初始化路径。"""
    manager = WorktreeManager(base_path=str(tmp_path))

    assert manager.base_path == str(tmp_path)
    assert manager.worktrees_dir == os.path.join(str(tmp_path), ".neuralswarm", "worktrees")
    assert manager.active_worktrees == {}


@pytest.mark.asyncio
@patch("neuralswarm.core.git.worktree.WorktreeManager._run_git", new_callable=AsyncMock)
async def test_create(mock_run_git, manager, task_id):
    """create 应创建 worktree 目录并注册到 active_worktrees。"""
    mock_run_git.return_value = ""

    info = await manager.create(task_id)

    # 验证返回的 info
    assert isinstance(info, WorktreeInfo)
    assert info.task_id == task_id
    assert str(task_id)[:8] in info.branch
    assert "ns/task-" in info.branch
    assert "neuralswarm" in info.path
    assert "worktrees" in info.path

    # 验证注册到 active_worktrees
    assert task_id in manager.active_worktrees
    assert manager.active_worktrees[task_id] is info

    # 验证 git 命令调用
    mock_run_git.assert_called_once()
    call_args = mock_run_git.call_args[0]
    assert call_args[0] == "worktree"
    assert call_args[1] == "add"


@pytest.mark.asyncio
@patch("neuralswarm.core.git.worktree.WorktreeManager._run_git", new_callable=AsyncMock)
async def test_create_git_failure(mock_run_git, manager, task_id):
    """create 在 git 命令失败时应抛出 RuntimeError。"""
    mock_run_git.side_effect = RuntimeError("git command failed: fatal: ...")

    with pytest.raises(RuntimeError, match="git command failed"):
        await manager.create(task_id)

    # 不应注册到 active_worktrees
    assert task_id not in manager.active_worktrees


@pytest.mark.asyncio
@patch("neuralswarm.core.git.worktree.WorktreeManager._run_git", new_callable=AsyncMock)
async def test_remove(mock_run_git, manager, task_id):
    """remove 应删除 worktree 并清理 active_worktrees。"""
    # 预先注册一个 worktree
    info = _make_worktree_info(task_id)
    manager.active_worktrees[task_id] = info
    mock_run_git.return_value = ""

    await manager.remove(task_id)

    # 验证从 active_worktrees 移除
    assert task_id not in manager.active_worktrees

    # 验证 git 命令调用（worktree remove + branch -D）
    assert mock_run_git.call_count == 2
    calls = [call[0] for call in mock_run_git.call_args_list]
    assert ("worktree", "remove", info.path) in calls
    assert ("branch", "-D", info.branch) in calls


@pytest.mark.asyncio
async def test_remove_not_found(manager, task_id):
    """remove 对不存在的 task_id 应抛出 KeyError。"""
    with pytest.raises(KeyError, match=f"Worktree not found for task {task_id}"):
        await manager.remove(task_id)


@pytest.mark.asyncio
@patch("neuralswarm.core.git.worktree.WorktreeManager._run_git", new_callable=AsyncMock)
async def test_remove_git_failure(mock_run_git, manager, task_id):
    """remove 在 worktree remove 失败时应抛出 RuntimeError 并保留 active_worktrees。"""
    info = _make_worktree_info(task_id)
    manager.active_worktrees[task_id] = info
    mock_run_git.side_effect = RuntimeError("git command failed")

    with pytest.raises(RuntimeError, match="git command failed"):
        await manager.remove(task_id)

    # active_worktrees 不应被清理（worktree remove 失败）
    assert task_id in manager.active_worktrees


@pytest.mark.asyncio
@patch("neuralswarm.core.git.worktree.WorktreeManager._run_git", new_callable=AsyncMock)
async def test_remove_branch_delete_failure(mock_run_git, manager, task_id):
    """remove 在 branch -D 失败时仍应清理 active_worktrees（不产生 ghost 条目）。"""
    info = _make_worktree_info(task_id)
    manager.active_worktrees[task_id] = info

    # 第一次调用 (worktree remove) 成功，第二次 (branch -D) 失败
    mock_run_git.side_effect = ["", RuntimeError("branch delete failed")]

    # 不应抛出异常（branch 失败被 catch）
    await manager.remove(task_id)

    # active_worktrees 应被清理
    assert task_id not in manager.active_worktrees


@pytest.mark.asyncio
@patch("neuralswarm.core.git.worktree.WorktreeManager._run_git", new_callable=AsyncMock)
async def test_merge(mock_run_git, manager, task_id):
    """merge 应将 worktree 分支合并到主分支。"""
    info = _make_worktree_info(task_id)
    manager.active_worktrees[task_id] = info
    mock_run_git.return_value = ""

    await manager.merge(task_id)

    mock_run_git.assert_called_once_with(
        "merge",
        info.branch,
        "--no-ff",
        "-m",
        f"Merge task {task_id}",
        cwd=manager.base_path,
    )


@pytest.mark.asyncio
async def test_merge_not_found(manager, task_id):
    """merge 对不存在的 task_id 应抛出 KeyError。"""
    with pytest.raises(KeyError, match=f"Worktree not found for task {task_id}"):
        await manager.merge(task_id)


@pytest.mark.asyncio
@patch("neuralswarm.core.git.worktree.WorktreeManager._run_git", new_callable=AsyncMock)
async def test_merge_git_failure(mock_run_git, manager, task_id):
    """merge 在 git 命令失败时应抛出 RuntimeError。"""
    info = _make_worktree_info(task_id)
    manager.active_worktrees[task_id] = info
    mock_run_git.side_effect = RuntimeError("CONFLICT: ...")

    with pytest.raises(RuntimeError, match="CONFLICT"):
        await manager.merge(task_id)


def test_list_worktrees_empty(manager):
    """list_worktrees 无活跃 worktree 时应返回空列表。"""
    assert manager.list_worktrees() == []


def test_list_worktrees(manager):
    """list_worktrees 应返回所有活跃 worktree。"""
    task_ids = [uuid4() for _ in range(3)]
    for tid in task_ids:
        manager.active_worktrees[tid] = _make_worktree_info(tid)

    result = manager.list_worktrees()
    assert len(result) == 3
    assert {info.task_id for info in result} == set(task_ids)


def test_get_worktree(manager, task_id):
    """get_worktree 应返回对应的 WorktreeInfo 或 None。"""
    assert manager.get_worktree(task_id) is None

    info = _make_worktree_info(task_id)
    manager.active_worktrees[task_id] = info

    assert manager.get_worktree(task_id) is info


def test_get_worktree_not_found(manager):
    """get_worktree 对不存在的 task_id 应返回 None。"""
    assert manager.get_worktree(uuid4()) is None


# ── _run_git 测试 ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_run_git_success(tmp_path):
    """_run_git 成功时应返回输出。"""
    manager = WorktreeManager(base_path=str(tmp_path))

    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"output\n", b"")
        mock_proc.returncode = 0
        mock_exec.return_value = mock_proc

        result = await manager._run_git("status")

        assert result == "output"
        mock_exec.assert_called_once()


@pytest.mark.asyncio
async def test_run_git_failure(tmp_path):
    """_run_git 失败时应抛出 RuntimeError。"""
    manager = WorktreeManager(base_path=str(tmp_path))

    with patch("asyncio.create_subprocess_exec", new_callable=AsyncMock) as mock_exec:
        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"fatal: not a git repo\n")
        mock_proc.returncode = 128
        mock_exec.return_value = mock_proc

        with pytest.raises(RuntimeError, match="git command failed"):
            await manager._run_git("status")
