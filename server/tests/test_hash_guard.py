import os
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from neuralswarm.core.concurrency import HashConflict, HashGuard


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


# ── compute_hash 测试 ───────────────────────────────────────────────


def test_compute_hash_deterministic():
    """compute_hash 对相同内容应返回相同哈希。"""
    h1 = HashGuard.compute_hash("hello world")
    h2 = HashGuard.compute_hash("hello world")
    assert h1 == h2
    assert len(h1) == 64  # sha256 hex digest length


def test_compute_hash_different_content():
    """compute_hash 对不同内容应返回不同哈希。"""
    h1 = HashGuard.compute_hash("hello")
    h2 = HashGuard.compute_hash("world")
    assert h1 != h2


def test_compute_hash_empty_string():
    """compute_hash 对空字符串应返回有效哈希。"""
    h = HashGuard.compute_hash("")
    assert len(h) == 64


# ── read 测试 ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_read_returns_content(guard, worktree_path):
    """read 应返回文件内容并记录哈希。"""
    file_path = "test.txt"
    full_path = os.path.join(worktree_path, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write("hello world")

    content = await guard.read(file_path)

    assert content == "hello world"
    assert guard.get_hash(file_path) == HashGuard.compute_hash("hello world")


@pytest.mark.asyncio
async def test_read_records_hash(guard, worktree_path):
    """read 应将哈希记录到 file_hashes。"""
    file_path = "src/main.py"
    full_path = os.path.join(worktree_path, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write("print('hi')")

    assert guard.get_hash(file_path) is None

    await guard.read(file_path)

    assert guard.get_hash(file_path) is not None
    assert guard.get_hash(file_path) == HashGuard.compute_hash("print('hi')")


@pytest.mark.asyncio
async def test_read_file_not_found(guard):
    """read 对不存在的文件应抛出 FileNotFoundError。"""
    with pytest.raises(FileNotFoundError):
        await guard.read("nonexistent.txt")


# ── write 测试 (成功) ───────────────────────────────────────────────


@pytest.mark.asyncio
@patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock)
async def test_write_success(mock_git, guard, worktree_path, agent_id):
    """write 哈希匹配时应写入文件并提交，返回 True。"""
    file_path = "output.txt"
    full_path = os.path.join(worktree_path, file_path)

    # 先写入初始内容
    with open(full_path, "w", encoding="utf-8") as f:
        f.write("original")

    # 读取记录哈希
    await guard.read(file_path)

    # 写入新内容
    result = await guard.write(file_path, "updated", agent_id)

    assert result is True

    # 验证文件内容
    with open(full_path, "r", encoding="utf-8") as f:
        assert f.read() == "updated"

    # 验证 git commit 被调用
    mock_git.assert_called_once_with(file_path, agent_id)

    # 验证哈希已更新
    assert guard.get_hash(file_path) == HashGuard.compute_hash("updated")


@pytest.mark.asyncio
@patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock)
async def test_write_same_content(mock_git, guard, worktree_path, agent_id):
    """write 写入相同内容也应成功。"""
    file_path = "same.txt"
    full_path = os.path.join(worktree_path, file_path)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write("no change")

    await guard.read(file_path)

    result = await guard.write(file_path, "no change", agent_id)

    assert result is True
    mock_git.assert_called_once()


# ── write 测试 (冲突) ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_write_conflict(guard, worktree_path, agent_id):
    """write 哈希不匹配时应返回 HashConflict。"""
    file_path = "conflict.txt"
    full_path = os.path.join(worktree_path, file_path)

    # 写入初始内容
    with open(full_path, "w", encoding="utf-8") as f:
        f.write("version 1")

    # Agent A 读取
    await guard.read(file_path)

    # Agent B 修改了同一文件（模拟外部修改）
    with open(full_path, "w", encoding="utf-8") as f:
        f.write("version 2 by agent B")

    # Agent A 尝试写入
    result = await guard.write(file_path, "version 2 by agent A", agent_id)

    assert isinstance(result, HashConflict)
    assert result.file_path == file_path
    assert result.agent_id == agent_id
    assert result.expected_hash == HashGuard.compute_hash("version 1")
    assert result.actual_hash == HashGuard.compute_hash("version 2 by agent B")
    assert result.current_content == "version 2 by agent B"
    assert result.new_content == "version 2 by agent A"


@pytest.mark.asyncio
async def test_write_conflict_file_content_unchanged(guard, worktree_path, agent_id):
    """冲突时文件内容不应被修改。"""
    file_path = "preserve.txt"
    full_path = os.path.join(worktree_path, file_path)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write("original")

    await guard.read(file_path)

    # 外部修改
    with open(full_path, "w", encoding="utf-8") as f:
        f.write("modified externally")

    await guard.write(file_path, "new content", agent_id)

    # 文件应保持外部修改的内容
    with open(full_path, "r", encoding="utf-8") as f:
        assert f.read() == "modified externally"


# ── write 测试 (新文件) ─────────────────────────────────────────────


@pytest.mark.asyncio
@patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock)
async def test_write_new_file(mock_git, guard, worktree_path, agent_id):
    """write 文件不存在且无哈希记录时应创建新文件。"""
    file_path = "new_file.txt"
    full_path = os.path.join(worktree_path, file_path)

    # 没有 read 过，也没有哈希记录
    assert guard.get_hash(file_path) is None

    result = await guard.write(file_path, "brand new content", agent_id)

    assert result is True

    with open(full_path, "r", encoding="utf-8") as f:
        assert f.read() == "brand new content"

    mock_git.assert_called_once()
    assert guard.get_hash(file_path) == HashGuard.compute_hash("brand new content")


@pytest.mark.asyncio
@patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock)
async def test_write_new_file_nested_path(mock_git, guard, worktree_path, agent_id):
    """write 新文件时应自动创建中间目录。"""
    file_path = "deep/nested/dir/file.py"
    full_path = os.path.join(worktree_path, file_path)

    result = await guard.write(file_path, "print('hello')", agent_id)

    assert result is True
    assert os.path.exists(full_path)

    with open(full_path, "r", encoding="utf-8") as f:
        assert f.read() == "print('hello')"


# ── get_hash 测试 ────────────────────────────────────────────────────


def test_get_hash_returns_none_for_unknown(guard):
    """get_hash 对未知文件应返回 None。"""
    assert guard.get_hash("unknown.txt") is None


@pytest.mark.asyncio
async def test_get_hash_returns_recorded_hash(guard, worktree_path):
    """get_hash 应返回 read 时记录的哈希。"""
    file_path = "tracked.txt"
    full_path = os.path.join(worktree_path, file_path)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write("tracked content")

    await guard.read(file_path)

    expected = HashGuard.compute_hash("tracked content")
    assert guard.get_hash(file_path) == expected


# ── clear 测试 ───────────────────────────────────────────────────────


def test_clear(guard):
    """clear 应清除所有记录的哈希。"""
    guard.file_hashes["a.txt"] = "hash_a"
    guard.file_hashes["b.txt"] = "hash_b"

    assert len(guard.file_hashes) == 2

    guard.clear()

    assert len(guard.file_hashes) == 0
    assert guard.get_hash("a.txt") is None


# ── path traversal 测试 ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_read_path_traversal_rejected(guard):
    """read 应拒绝包含 .. 的路径穿越攻击。"""
    with pytest.raises(ValueError, match="Path traversal detected"):
        await guard.read("../../etc/passwd")


@pytest.mark.asyncio
async def test_read_path_traversal_subdir_rejected(guard):
    """read 应拒绝从子目录逃逸的路径。"""
    with pytest.raises(ValueError, match="Path traversal detected"):
        await guard.read("subdir/../../etc/passwd")


@pytest.mark.asyncio
@patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock)
async def test_write_path_traversal_rejected(mock_git, guard, agent_id):
    """write 应拒绝包含 .. 的路径穿越攻击。"""
    with pytest.raises(ValueError, match="Path traversal detected"):
        await guard.write("../../etc/passwd", "malicious", agent_id)


@pytest.mark.asyncio
@patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock)
async def test_write_path_traversal_subdir_rejected(mock_git, guard, agent_id):
    """write 应拒绝从子目录逃逸的路径。"""
    with pytest.raises(ValueError, match="Path traversal detected"):
        await guard.write("subdir/../../etc/passwd", "malicious", agent_id)


@pytest.mark.asyncio
@patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock)
async def test_write_path_traversal_encoded_dot_rejected(mock_git, guard, agent_id):
    """write 应拒绝尝试通过多级 .. 逃逸的路径。"""
    with pytest.raises(ValueError, match="Path traversal detected"):
        await guard.write("a/b/c/../../../../etc/passwd", "malicious", agent_id)


# ── git commit failure 测试 ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_write_git_commit_failure_still_updates_hash(guard, worktree_path, agent_id):
    """git commit 失败时，哈希记录仍应更新，避免下次误报冲突。"""
    file_path = "fail_commit.txt"
    full_path = os.path.join(worktree_path, file_path)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write("initial")

    await guard.read(file_path)

    # Mock git commit to raise
    with patch.object(
        HashGuard, "_git_add_and_commit", new_callable=AsyncMock, side_effect=RuntimeError("git failed")
    ):
        result = await guard.write(file_path, "updated content", agent_id)

    assert result is True

    # 哈希应已更新，即使 git 失败
    assert guard.get_hash(file_path) == HashGuard.compute_hash("updated content")

    # 文件内容应正确写入
    with open(full_path, "r", encoding="utf-8") as f:
        assert f.read() == "updated content"


@pytest.mark.asyncio
async def test_write_after_git_failure_no_false_conflict(guard, worktree_path, agent_id):
    """git commit 失败后，再次写入不应误报冲突。"""
    file_path = "no_false_conflict.txt"
    full_path = os.path.join(worktree_path, file_path)

    with open(full_path, "w", encoding="utf-8") as f:
        f.write("v1")

    await guard.read(file_path)

    # 第一次写入，git 失败
    with patch.object(
        HashGuard, "_git_add_and_commit", new_callable=AsyncMock, side_effect=RuntimeError("git failed")
    ):
        result1 = await guard.write(file_path, "v2", agent_id)

    assert result1 is True

    # 第二次写入，git 正常 - 不应产生冲突
    with patch.object(HashGuard, "_git_add_and_commit", new_callable=AsyncMock):
        result2 = await guard.write(file_path, "v3", agent_id)

    assert result2 is True
    assert guard.get_hash(file_path) == HashGuard.compute_hash("v3")


# ── HashConflict 数据类测试 ──────────────────────────────────────────


def test_hash_conflict_fields():
    """HashConflict 应正确存储所有字段。"""
    agent_id = uuid4()
    conflict = HashConflict(
        file_path="test.py",
        agent_id=agent_id,
        expected_hash="abc123",
        actual_hash="def456",
        current_content="current",
        new_content="new",
    )

    assert conflict.file_path == "test.py"
    assert conflict.agent_id == agent_id
    assert conflict.expected_hash == "abc123"
    assert conflict.actual_hash == "def456"
    assert conflict.current_content == "current"
    assert conflict.new_content == "new"
