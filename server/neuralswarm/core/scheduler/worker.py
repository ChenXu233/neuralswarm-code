from __future__ import annotations

import asyncio
import logging
import os
from uuid import UUID

from neuralswarm.core.concurrency.hash_guard import HashConflict, HashGuard

logger = logging.getLogger(__name__)


class WorkerAgent:
    """Worker Agent - 在 worktree 中执行具体子任务。

    使用 HashGuard 进行文件读写，确保并发安全。
    """

    def __init__(
        self,
        agent_id: UUID,
        worktree_path: str,
        hash_guard: HashGuard,
    ):
        self.agent_id = agent_id
        self.worktree_path = worktree_path
        self.hash_guard = hash_guard

    async def execute_subtask(self, subtask: dict) -> dict:
        """执行子任务。

        subtask 格式:
        {
            "type": "file_edit" | "file_create" | "shell",
            "path": "src/main.py",  # for file operations
            "content": "...",       # for file operations
            "command": "ls -la",    # for shell
        }

        Returns:
        {
            "success": bool,
            "output": str,
            "conflict": HashConflict | None,
        }
        """
        task_type = subtask.get("type")
        logger.info(
            "Agent %s executing subtask type=%s",
            self.agent_id,
            task_type,
        )

        if task_type == "file_edit":
            return await self._execute_file_edit(
                subtask["path"], subtask["content"]
            )
        elif task_type == "file_create":
            return await self._execute_file_create(
                subtask["path"], subtask["content"]
            )
        elif task_type == "shell":
            return await self._execute_shell(subtask["command"])
        else:
            msg = f"Unknown subtask type: {task_type}"
            logger.warning("Agent %s: %s", self.agent_id, msg)
            return {
                "success": False,
                "output": msg,
                "conflict": None,
            }

    async def _execute_file_edit(self, path: str, content: str) -> dict:
        """编辑文件（读取 -> 修改 -> 写入）。"""
        try:
            # 读取当前内容并记录哈希
            await self.hash_guard.read(path)

            # 写入新内容
            result = await self.hash_guard.write(path, content, self.agent_id)

            if isinstance(result, HashConflict):
                logger.warning(
                    "Agent %s hash conflict editing %s",
                    self.agent_id,
                    path,
                )
                return {
                    "success": False,
                    "output": f"Hash conflict on {path}",
                    "conflict": result,
                }

            logger.debug("Agent %s edited file %s", self.agent_id, path)
            return {
                "success": True,
                "output": f"File {path} updated successfully",
                "conflict": None,
            }
        except Exception as e:
            logger.exception("Agent %s failed to edit %s", self.agent_id, path)
            return {
                "success": False,
                "output": str(e),
                "conflict": None,
            }

    async def _execute_file_create(self, path: str, content: str) -> dict:
        """创建新文件。"""
        try:
            result = await self.hash_guard.write(path, content, self.agent_id)

            if isinstance(result, HashConflict):
                logger.warning(
                    "Agent %s hash conflict creating %s",
                    self.agent_id,
                    path,
                )
                return {
                    "success": False,
                    "output": f"Hash conflict on {path}",
                    "conflict": result,
                }

            logger.debug("Agent %s created file %s", self.agent_id, path)
            return {
                "success": True,
                "output": f"File {path} created successfully",
                "conflict": None,
            }
        except Exception as e:
            logger.exception(
                "Agent %s failed to create %s", self.agent_id, path
            )
            return {
                "success": False,
                "output": str(e),
                "conflict": None,
            }

    async def _execute_shell(self, command: str) -> dict:
        """执行 shell 命令。"""
        try:
            logger.debug(
                "Agent %s running shell: %s", self.agent_id, command
            )
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.worktree_path,
            )
            stdout, stderr = await proc.communicate()

            stdout_text = stdout.decode("utf-8", errors="replace")
            stderr_text = stderr.decode("utf-8", errors="replace")

            if proc.returncode != 0:
                output = stderr_text or stdout_text
                logger.warning(
                    "Agent %s shell command failed (rc=%d): %s",
                    self.agent_id,
                    proc.returncode,
                    output,
                )
                return {
                    "success": False,
                    "output": output,
                    "conflict": None,
                }

            logger.debug("Agent %s shell command succeeded", self.agent_id)
            return {
                "success": True,
                "output": stdout_text,
                "conflict": None,
            }
        except Exception as e:
            logger.exception(
                "Agent %s shell command error: %s", self.agent_id, command
            )
            return {
                "success": False,
                "output": str(e),
                "conflict": None,
            }
