from __future__ import annotations

import asyncio
import hashlib
import logging
import os
from dataclasses import dataclass
from uuid import UUID

import aiofiles

logger = logging.getLogger(__name__)


@dataclass
class HashConflict:
    """文件哈希冲突。"""

    file_path: str
    agent_id: UUID
    expected_hash: str  # Agent 读取时的哈希
    actual_hash: str  # 当前文件的哈希
    current_content: str  # 当前文件内容
    new_content: str  # Agent 想写入的内容


class HashGuard:
    """文件哈希并发控制器。

    通过跟踪文件哈希来检测并发修改冲突。
    每个 Agent 读文件时记录哈希，写入前校验哈希是否变化。
    """

    def __init__(self, worktree_path: str):
        self.worktree_path = worktree_path
        self.file_hashes: dict[str, str] = {}  # file_path -> sha256 hash

    async def read(self, file_path: str) -> str:
        """读取文件并记录哈希。

        1. 读取文件内容
        2. 计算 sha256 哈希
        3. 记录到 file_hashes
        4. 返回文件内容

        Args:
            file_path: 文件的相对路径。

        Returns:
            文件内容。

        Raises:
            FileNotFoundError: 文件不存在。
        """
        full_path = os.path.join(self.worktree_path, file_path)

        async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
            content = await f.read()

        file_hash = self.compute_hash(content)
        self.file_hashes[file_path] = file_hash

        logger.debug("Read file %s, hash=%s", file_path, file_hash[:12])
        return content

    async def write(
        self, file_path: str, content: str, agent_id: UUID
    ) -> bool | HashConflict:
        """写入文件，校验哈希。

        1. 读取当前文件内容
        2. 计算当前哈希
        3. 与记录的哈希比较
        4. 如果哈希不同 -> 返回 HashConflict
        5. 如果哈希相同 -> 写入文件 + git commit
        6. 更新 file_hashes

        Args:
            file_path: 文件的相对路径。
            content: 要写入的内容。
            agent_id: 执行写入的 Agent ID。

        Returns:
            True 表示写入成功，HashConflict 表示冲突。
        """
        full_path = os.path.join(self.worktree_path, file_path)
        recorded_hash = self.file_hashes.get(file_path)

        # 读取当前文件内容
        current_content = ""
        if os.path.exists(full_path):
            async with aiofiles.open(full_path, "r", encoding="utf-8") as f:
                current_content = await f.read()

        current_hash = self.compute_hash(current_content)

        # 如果有记录的哈希，检查是否冲突
        if recorded_hash is not None and current_hash != recorded_hash:
            logger.warning(
                "Hash conflict on %s: expected=%s actual=%s (agent=%s)",
                file_path,
                recorded_hash[:12],
                current_hash[:12],
                agent_id,
            )
            return HashConflict(
                file_path=file_path,
                agent_id=agent_id,
                expected_hash=recorded_hash,
                actual_hash=current_hash,
                current_content=current_content,
                new_content=content,
            )

        # 哈希匹配（或新文件），写入文件
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        async with aiofiles.open(full_path, "w", encoding="utf-8") as f:
            await f.write(content)

        # Git commit
        await self._git_add_and_commit(file_path, agent_id)

        # 更新哈希记录
        new_hash = self.compute_hash(content)
        self.file_hashes[file_path] = new_hash

        logger.debug(
            "Wrote file %s, new_hash=%s (agent=%s)",
            file_path,
            new_hash[:12],
            agent_id,
        )
        return True

    def get_hash(self, file_path: str) -> str | None:
        """获取文件的记录哈希。"""
        return self.file_hashes.get(file_path)

    def clear(self) -> None:
        """清除所有记录的哈希。"""
        self.file_hashes.clear()

    @staticmethod
    def compute_hash(content: str) -> str:
        """计算内容的 sha256 哈希。"""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def _git_add_and_commit(self, file_path: str, agent_id: UUID) -> None:
        """将文件变更提交到 git。

        Args:
            file_path: 文件的相对路径。
            agent_id: 执行写入的 Agent ID。
        """
        await self._run_git("add", file_path)
        await self._run_git(
            "commit",
            "-m",
            f"[HashGuard] Update {file_path} (agent={agent_id})",
        )

    async def _run_git(self, *args: str) -> str:
        """执行 git 命令。

        Args:
            *args: git 子命令及参数。

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
            cwd=self.worktree_path,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"git command failed: {stderr.decode()}")
        return stdout.decode().strip()
