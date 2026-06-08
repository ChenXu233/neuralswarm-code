from __future__ import annotations

import logging
from uuid import UUID

from neuralswarm.core.scheduler.agent_pool import AgentPool, AgentRuntime
from neuralswarm.core.git.worktree import WorktreeManager
from neuralswarm.core.concurrency.hash_guard import HashGuard
from neuralswarm.core.repository import AgentRepository
from neuralswarm.models.enums import AgentType, AgentStatus

logger = logging.getLogger(__name__)


class CentralScheduler:
    """中央调度器 - 管理 Task worktree，分配 Agent。"""

    def __init__(
        self,
        agent_pool: AgentPool,
        worktree_manager: WorktreeManager,
    ):
        self.agent_pool = agent_pool
        self.worktree_manager = worktree_manager
        self.task_agents: dict[UUID, list[UUID]] = {}  # task_id -> [agent_ids]
        self.task_hash_guards: dict[UUID, HashGuard] = {}  # task_id -> HashGuard

    async def submit_task(
        self,
        task_id: UUID,
        project_id: UUID,
        agent_repo: AgentRepository,
        prompt: str,
        llm_config: dict,
        tools: list[str],
    ) -> AgentRuntime:
        """用户提交任务 → 创建 worktree + Sub-scheduler Agent。

        1. 创建 worktree
        2. 创建 Sub-scheduler Agent
        3. 注册 HashGuard
        4. 启动 Agent
        5. 返回 AgentRuntime
        """
        # 1. 创建 worktree
        worktree_info = await self.worktree_manager.create(task_id)
        logger.info("Worktree created for task %s: %s", task_id, worktree_info.path)

        # 2. 创建 Sub-scheduler Agent
        scheduler_runtime = await self.agent_pool.create_agent(
            agent_repo=agent_repo,
            agent_type=AgentType.SCHEDULER,
            task_id=task_id,
            project_id=project_id,
            worktree_path=worktree_info.path,
            llm_config=llm_config,
            tools=tools,
            name=f"scheduler-{task_id}",
        )

        # 3. 注册到 task_agents
        self.task_agents.setdefault(task_id, []).append(scheduler_runtime.id)

        # 4. 创建并注册 HashGuard
        hash_guard = HashGuard(worktree_path=worktree_info.path)
        self.task_hash_guards[task_id] = hash_guard

        # 5. 启动 Agent
        await scheduler_runtime.start(agent_repo)

        logger.info("Task %s submitted, scheduler agent %s created", task_id, scheduler_runtime.id)
        return scheduler_runtime

    async def allocate_workers(
        self,
        task_id: UUID,
        parent_id: UUID,
        agent_repo: AgentRepository,
        subtasks: list[dict],
        llm_config: dict,
        tools: list[str],
    ) -> list[AgentRuntime]:
        """Sub-scheduler 申请 Worker Agents。

        1. 获取 worktree 路径
        2. 为每个 subtask 创建 Worker Agent
        3. 注册到 task_agents
        4. 启动所有 Worker Agent
        5. 返回 AgentRuntime 列表
        """
        # 1. 获取 worktree 路径
        worktree_info = self.worktree_manager.get_worktree(task_id)
        if worktree_info is None:
            raise KeyError(f"No worktree found for task {task_id}")

        # 2. 为每个 subtask 创建 Worker Agent
        worker_runtimes: list[AgentRuntime] = []
        for subtask in subtasks:
            worker_runtime = await self.agent_pool.create_agent(
                agent_repo=agent_repo,
                agent_type=AgentType.WORKER,
                task_id=task_id,
                project_id=subtask.get("project_id"),
                worktree_path=worktree_info.path,
                llm_config=llm_config,
                tools=tools,
                name=subtask.get("name", f"worker-{task_id}"),
                parent_id=parent_id,
            )
            worker_runtimes.append(worker_runtime)

            # 3. 注册到 task_agents
            self.task_agents.setdefault(task_id, []).append(worker_runtime.id)

        # 4. 启动所有 Worker Agent
        for runtime in worker_runtimes:
            await runtime.start(agent_repo)

        logger.info(
            "Allocated %d workers for task %s", len(worker_runtimes), task_id
        )
        return worker_runtimes

    async def complete_task(self, task_id: UUID, agent_repo: AgentRepository) -> None:
        """Task 完成 → 合并 worktree + 清理。

        1. 合并 worktree 到主分支
        2. 销毁所有 Agent
        3. 清理 HashGuard
        4. 删除 worktree
        """
        # 1. 合并 worktree
        merge_failed = False
        try:
            await self.worktree_manager.merge(task_id)
            logger.info("Worktree merged for task %s", task_id)
        except KeyError as e:
            logger.warning("Failed to merge worktree for task %s: %s", task_id, e)
        except RuntimeError as e:
            logger.warning(
                "Merge conflict for task %s, preserving worktree: %s", task_id, e
            )
            merge_failed = True

        # 2. 销毁所有 Agent
        agent_ids = self.task_agents.get(task_id, [])
        for agent_id in agent_ids:
            await self.agent_pool.destroy_agent(agent_id, agent_repo)

        # 3. 清理 HashGuard
        hash_guard = self.task_hash_guards.pop(task_id, None)
        if hash_guard is not None:
            hash_guard.clear()

        # 4. 删除 worktree (仅在合并成功或 worktree 不存在时)
        if not merge_failed:
            try:
                await self.worktree_manager.remove(task_id)
            except (KeyError, RuntimeError) as e:
                logger.warning("Failed to remove worktree for task %s: %s", task_id, e)
        else:
            logger.info(
                "Skipping worktree removal for task %s due to merge conflict", task_id
            )

        # 5. 清理 task_agents 记录
        self.task_agents.pop(task_id, None)

        logger.info("Task %s completed, resources cleaned up", task_id)

    async def fail_task(self, task_id: UUID, agent_repo: AgentRepository, error: str) -> None:
        """Task 失败 → 清理资源。

        1. 销毁所有 Agent (标记为 FAILED)
        2. 清理 HashGuard
        3. 删除 worktree
        """
        logger.warning("Task %s failed: %s", task_id, error)

        # 1. 销毁所有 Agent
        agent_ids = self.task_agents.get(task_id, [])
        for agent_id in agent_ids:
            await self.agent_pool.destroy_agent(agent_id, agent_repo, failed=True)

        # 2. 清理 HashGuard
        hash_guard = self.task_hash_guards.pop(task_id, None)
        if hash_guard is not None:
            hash_guard.clear()

        # 3. 删除 worktree
        try:
            await self.worktree_manager.remove(task_id)
        except (KeyError, RuntimeError) as e:
            logger.warning("Failed to remove worktree for task %s: %s", task_id, e)

        # 4. 清理 task_agents 记录
        self.task_agents.pop(task_id, None)

        logger.info("Task %s failed, resources cleaned up", task_id)

    def get_task_agents(self, task_id: UUID) -> list[UUID]:
        """获取 Task 的所有 Agent ID。"""
        return self.task_agents.get(task_id, [])

    def get_hash_guard(self, task_id: UUID) -> HashGuard | None:
        """获取 Task 的 HashGuard。"""
        return self.task_hash_guards.get(task_id)
