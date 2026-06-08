from __future__ import annotations

import json
import logging
from uuid import UUID

from neuralswarm.core.scheduler.central import CentralScheduler
from neuralswarm.core.scheduler.worker import WorkerAgent
from neuralswarm.core.concurrency.hash_guard import HashGuard, HashConflict
from neuralswarm.core.concurrency.conflict_manager import ConflictManager

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
        conflict_manager: ConflictManager | None = None,
        llm_gateway=None,
        agent_repo=None,
    ):
        self.agent_id = agent_id
        self.task_id = task_id
        self.central = central_scheduler
        self.hash_guard = hash_guard
        self.conflict_manager = conflict_manager
        self.llm_gateway = llm_gateway
        self.agent_repo = agent_repo
        self.plan: list[dict] = []

    async def analyze_task(self, prompt: str) -> list[dict]:
        """分析任务，生成执行计划。

        如果提供了 llm_gateway，调用 LLM 生成计划。
        否则使用硬编码的简单计划。

        Args:
            prompt: 用户的任务描述。

        Returns:
            plan - 执行步骤列表。
        """
        if self.llm_gateway:
            plan = await self._analyze_with_llm(prompt)
        else:
            plan = self._analyze_simple(prompt)

        self.plan = plan
        logger.info(
            "Agent %s generated plan with %d steps for task %s",
            self.agent_id,
            len(plan),
            self.task_id,
        )
        return plan

    async def _analyze_with_llm(self, prompt: str) -> list[dict]:
        """调用 LLM 生成执行计划。"""
        system_prompt = """你是一个任务分析器。根据用户的任务描述，生成一个 JSON 格式的执行计划。

输出格式（纯 JSON，不要 markdown）：
[
  {
    "type": "file_edit" | "file_create" | "shell",
    "description": "步骤描述",
    "path": "文件路径（file_edit/file_create 时必须）",
    "content": "文件内容（file_create 时必须）",
    "command": "shell 命令（shell 时必须）",
    "is_simple": true/false
  }
]

规则：
- is_simple=true 表示可以串行执行的简单步骤
- is_simple=false 表示需要并行执行的复杂步骤
- 每个步骤只做一个操作
- 路径使用相对路径"""

        try:
            response = await self.llm_gateway.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
            )
            plan = json.loads(response.content)
            if not isinstance(plan, list):
                raise ValueError(f"LLM 返回非列表: {type(plan)}")
            return plan
        except Exception as e:
            logger.warning("LLM 分析失败，回退到简单计划: %s", e)
            return self._analyze_simple(prompt)

    def _analyze_simple(self, prompt: str) -> list[dict]:
        """生成简单的硬编码计划。"""
        return [
            {
                "type": "shell",
                "description": f"Analyze task: {prompt}",
                "command": "echo 'analyzing task'",
                "is_simple": True,
            }
        ]

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
        冲突时通知 ConflictManager。

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
        result = await worker.execute_subtask(step)

        # 冲突时通知 ConflictManager
        if result.get("conflict") and self.conflict_manager:
            await self.conflict_manager.detect(result["conflict"])

        return result

    async def request_workers(self, subtasks: list[dict]) -> list[dict]:
        """向 Central Scheduler 申请 Worker 执行复杂任务。

        通过 central.allocate_workers 并行分配 Worker。

        Args:
            subtasks: 需要分配给 Worker 的子任务列表。

        Returns:
            每个子任务的执行结果列表。
        """
        # 通过 CentralScheduler 分配 Worker
        workers = await self.central.allocate_workers(
            task_id=self.task_id,
            parent_id=self.agent_id,
            agent_repo=self.agent_repo,
            subtasks=subtasks,
            llm_config={},
            tools=[],
        )

        results: list[dict] = []

        # 并行执行所有 Worker
        if workers:
            import asyncio

            async def run_worker(worker, subtask):
                worker_agent = WorkerAgent(
                    agent_id=worker.id,
                    worktree_path=self.hash_guard.worktree_path,
                    hash_guard=self.hash_guard,
                )
                result = await worker_agent.execute_subtask(subtask)
                # 冲突时通知 ConflictManager
                if result.get("conflict") and self.conflict_manager:
                    await self.conflict_manager.detect(result["conflict"])
                return result

            tasks = [
                run_worker(worker, subtask)
                for worker, subtask in zip(workers, subtasks)
            ]
            results = await asyncio.gather(*tasks)

        logger.info(
            "Agent %s completed %d subtasks for task %s",
            self.agent_id,
            len(results),
            self.task_id,
        )
        return results
