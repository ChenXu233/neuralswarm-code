from __future__ import annotations

import asyncio
import logging
import os
from uuid import UUID

logger = logging.getLogger(__name__)


class WorktreeInfo:
    """Worktree 信息。"""

    def __init__(self, path: str, branch: str, task_id: UUID):
        self.path = path
        self.branch = branch
        self.task_id = task_id


class WorktreeManager:
    """Git Worktree 管理器。

    每个 Task 获得独立的 Git worktree 用于隔离执行。
    多个 Agent 在同一 worktree 中工作，通过文件哈希检查防止冲突。
    """

    def __init__(self, base_path: str):
        """初始化 WorktreeManager。

        Args:
            base_path: 项目的 git 仓库根目录。
        """
        self.base_path = base_path
        self.worktrees_dir = os.path.join(base_path, ".neuralswarm", "worktrees")
        self.active_worktrees: dict[UUID, WorktreeInfo] = {}  # task_id -> info

    async def create(self, task_id: UUID) -> WorktreeInfo:
        """为 Task 创建 worktree。

        1. 确保 .neuralswarm/worktrees/ 目录存在
        2. 创建分支名: ns/task-{task_id_short}
        3. git worktree add <path> -b <branch>
        4. 注册到 active_worktrees

        Args:
            task_id: 任务 ID。

        Returns:
            WorktreeInfo 实例。

        Raises:
            RuntimeError: git 命令执行失败。
        """
        # 确保 worktrees 目录存在
        os.makedirs(self.worktrees_dir, exist_ok=True)

        # 生成分支名（使用 task_id 前 8 位）
        task_id_short = str(task_id)[:8]
        branch = f"ns/task-{task_id_short}"
        worktree_path = os.path.join(self.worktrees_dir, f"task-{task_id_short}")

        logger.info("Creating worktree for task %s (branch=%s)", task_id, branch)

        await self._run_git("worktree", "add", worktree_path, "-b", branch)

        info = WorktreeInfo(path=worktree_path, branch=branch, task_id=task_id)
        self.active_worktrees[task_id] = info

        logger.info("Worktree created: %s", worktree_path)
        return info

    async def remove(self, task_id: UUID) -> None:
        """删除 worktree。

        1. 从 active_worktrees 获取 info
        2. git worktree remove <path>
        3. git branch -D <branch>
        4. 从 active_worktrees 移除

        Args:
            task_id: 任务 ID。

        Raises:
            KeyError: worktree 不存在。
            RuntimeError: git 命令执行失败。
        """
        info = self.active_worktrees.get(task_id)
        if info is None:
            raise KeyError(f"Worktree not found for task {task_id}")

        logger.info("Removing worktree for task %s: %s", task_id, info.path)

        await self._run_git("worktree", "remove", info.path)

        # Use -D (force) and wrap in try/except: if branch deletion fails
        # after the worktree is already removed, we still clean up the
        # active_worktrees dict to avoid "ghost" entries.
        try:
            await self._run_git("branch", "-D", info.branch)
        except RuntimeError:
            logger.warning("Failed to delete branch %s, skipping", info.branch)

        del self.active_worktrees[task_id]
        logger.info("Worktree removed for task %s", task_id)

    async def merge(self, task_id: UUID) -> None:
        """将 worktree 分支合并到主分支。

        1. cd base_path
        2. git merge <branch> --no-ff -m "Merge task {task_id}"

        Args:
            task_id: 任务 ID。

        Raises:
            KeyError: worktree 不存在。
            RuntimeError: git 命令执行失败。
        """
        info = self.active_worktrees.get(task_id)
        if info is None:
            raise KeyError(f"Worktree not found for task {task_id}")

        logger.info("Merging branch %s for task %s", info.branch, task_id)

        await self._run_git(
            "merge",
            info.branch,
            "--no-ff",
            "-m",
            f"Merge task {task_id}",
            cwd=self.base_path,
        )

        logger.info("Branch %s merged for task %s", info.branch, task_id)

    def list_worktrees(self) -> list[WorktreeInfo]:
        """列出所有活跃 worktree。

        Returns:
            WorktreeInfo 列表。
        """
        return list(self.active_worktrees.values())

    def get_worktree(self, task_id: UUID) -> WorktreeInfo | None:
        """获取指定 Task 的 worktree。

        Args:
            task_id: 任务 ID。

        Returns:
            WorktreeInfo 或 None。
        """
        return self.active_worktrees.get(task_id)

    async def _run_git(self, *args: str, cwd: str | None = None) -> str:
        """执行 git 命令的辅助方法。

        Args:
            *args: git 子命令及参数。
            cwd: 工作目录，默认使用 base_path。

        Returns:
            命令输出（去除首尾空白）。

        Raises:
            RuntimeError: git 命令返回非零退出码。
        """
        cmd = ["git"] + list(args)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd or self.base_path,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"git command failed: {stderr.decode()}")
        return stdout.decode().strip()
