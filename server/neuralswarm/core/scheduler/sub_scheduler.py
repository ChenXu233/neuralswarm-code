from __future__ import annotations

import asyncio
import json
import logging
from uuid import UUID

from neuralswarm.core.scheduler.central import CentralScheduler
from neuralswarm.core.scheduler.worker import WorkerAgent
from neuralswarm.core.concurrency.hash_guard import HashGuard

logger = logging.getLogger(__name__)


class SubSchedulerAgent:
    """Sub-scheduler LLM - 规划 + 执行 + 协调。

    与用户对话，分析任务，制定执行计划。
    自己执行简单任务，需要并行时申请 Worker。
    """

    def __init__(
        self,
        agent_id: UUID,
        task_id: UUID,
        central_scheduler: CentralScheduler,
        hash_guard: HashGuard,
    ):
        self.agent_id = agent_id
        self.task_id = task_id
        self.central = central_scheduler
        self.hash_guard = hash_guard
        self.plan: list[dict] = []

    async def analyze_task(self, prompt: str) -> list[dict]:
        """分析任务，生成执行计划。

        Args:
            prompt: 用户的任务描述。

        Returns:
            plan - 执行步骤列表，每个步骤格式::

                {
                    "type": "file_edit" | "file_create" | "shell",
                    "description": "步骤描述",
                    "path": "src/main.py",
                    "content": "...",
                    "command": "...",
                    "is_simple": true,
                }
        """
        # 简化实现：根据 prompt 生成一个基础计划
        # LLM 集成将在后续版本中添加
        plan = [
            {
                "type": "shell",
                "description": f"Analyze task: {prompt}",
                "command": "echo 'analyzing task'",
                "is_simple": True,
            }
        ]
        self.plan = plan
        logger.info(
            "Agent %s generated plan with %d steps for task %s",
            self.agent_id,
            len(plan),
            self.task_id,
        )
        return plan

    async def execute_plan(self, plan: list[dict]) -> dict:
        """执行计划。

        1. 将步骤分为 simple（自己执行）和 complex（申请 Worker）
        2. simple 步骤串行执行
        3. complex 步骤并行分配给 Worker
        4. 返回执行结果

        Args:
            plan: 执行步骤列表。

        Returns:
            {
                "success": bool,
                "results": list[dict],
                "errors": list[str],
            }
        """
        simple_steps = [s for s in plan if s.get("is_simple", False)]
        complex_steps = [s for s in plan if not s.get("is_simple", False)]

        results: list[dict] = []
        errors: list[str] = []

        # 1. 串行执行 simple 步骤
        for step in simple_steps:
            result = await self.execute_step(step)
            results.append(result)
            if not result.get("success", False):
                errors.append(result.get("output", "Unknown error"))

        # 2. 并行执行 complex 步骤
        if complex_steps:
            worker_results = await self.request_workers(complex_steps)
            results.extend(worker_results)
            for r in worker_results:
                if not r.get("success", False):
                    errors.append(r.get("output", "Unknown error"))

        success = len(errors) == 0
        logger.info(
            "Agent %s executed plan for task %s: success=%s, %d results, %d errors",
            self.agent_id,
            self.task_id,
            success,
            len(results),
            len(errors),
        )
        return {
            "success": success,
            "results": results,
            "errors": errors,
        }

    async def execute_step(self, step: dict) -> dict:
        """自己执行一个步骤。

        使用 WorkerAgent 的 execute_subtask 方法执行具体操作。

        Args:
            step: 步骤描述字典。

        Returns:
            执行结果字典。
        """
        worker = WorkerAgent(
            agent_id=self.agent_id,
            worktree_path=self.hash_guard.worktree_path,
            hash_guard=self.hash_guard,
        )

        logger.info(
            "Agent %s self-executing step type=%s for task %s",
            self.agent_id,
            step.get("type"),
            self.task_id,
        )
        return await worker.execute_subtask(step)

    async def request_workers(self, subtasks: list[dict]) -> list[dict]:
        """向 Central Scheduler 申请 Worker 执行复杂任务。

        注意：此方法的完整实现需要 AgentRepository 和 LLM 配置，
        当前为简化版本，串行执行所有子任务。

        Args:
            subtasks: 需要分配给 Worker 的子任务列表。

        Returns:
            每个子任务的执行结果列表。
        """
        results: list[dict] = []

        # 简化实现：串行执行所有子任务
        # 完整版本将通过 central.allocate_workers 并行分配 Worker
        for subtask in subtasks:
            worker = WorkerAgent(
                agent_id=self.agent_id,
                worktree_path=self.hash_guard.worktree_path,
                hash_guard=self.hash_guard,
            )
            result = await worker.execute_subtask(subtask)
            results.append(result)

        logger.info(
            "Agent %s completed %d subtasks for task %s",
            self.agent_id,
            len(results),
            self.task_id,
        )
        return results
