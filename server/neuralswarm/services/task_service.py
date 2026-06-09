import asyncio
import logging
import os
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neuralswarm.core.agent import Agent
from neuralswarm.core.context_manager import ContextManager
from neuralswarm.core.repository import AgentRepository
from neuralswarm.core.tool_executor import ToolExecutor
from neuralswarm.models.agent import Agent as AgentModel
from neuralswarm.models.enums import AgentStatus, TaskStatus
from neuralswarm.models.llm import LLM
from neuralswarm.models.project import Project
from neuralswarm.models.task import Task
from neuralswarm.services.llm.gateway import LLMGateway
from neuralswarm.services.redis import redis_client

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, db: AsyncSession, llm_gateway: LLMGateway):
        self.db = db
        self.llm_gateway = llm_gateway

    async def _get_mcp_client(self, project_id: str):
        """获取项目的 MCP 客户端"""
        from neuralswarm.services.mcp.router import mcp_router
        from neuralswarm.services.mcp.client import McpClient

        client_id = mcp_router.get_client_for_project(project_id)
        if not client_id:
            return None

        # 简化实现：返回新的客户端连接
        client = McpClient(f"ws://localhost:8765")
        if await client.connect():
            return client
        return None

    async def submit_task(self, project_id: UUID, prompt: str) -> Task:
        """Submit a task and start agent execution in background."""
        project = await self.db.get(Project, project_id)
        if not project or project.deleted_at:
            raise ValueError(f"Project not found: {project_id}")

        agent_model = await self._get_or_create_default_agent(project_id)
        llm_model = await self._get_default_llm()

        task = Task(
            project_id=project_id,
            agent_id=agent_model.id,
            llm_id=llm_model.id,
            input=prompt,
            status=TaskStatus.PENDING,
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        await redis_client.set_task_status(str(task.id), "pending")

        asyncio.create_task(self._execute_agent(task.id, project, agent_model, llm_model, prompt))

        return task

    async def cancel_task(self, task_id: UUID) -> Task:
        """Cancel a running or pending task."""
        task = await self.db.get(Task, task_id)
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        if task.status not in (TaskStatus.PENDING, TaskStatus.RUNNING):
            raise ValueError(f"Cannot cancel task in status {task.status}")

        task.status = TaskStatus.CANCELLED
        await self.db.commit()

        await redis_client.set_task_status(str(task_id), "cancelled")
        await redis_client.publish_event(str(task_id), {"type": "status", "data": {"status": "cancelled"}})

        return task

    def _is_git_repo(self, path: str) -> bool:
        """检查路径是否是 git 仓库。"""
        return os.path.isdir(os.path.join(path, ".git"))

    async def _execute_agent(self, task_id: UUID, project: Project, agent_model: AgentModel, llm_model: LLM, prompt: str):
        """Execute agent in background."""
        task_id_str = str(task_id)

        try:
            await redis_client.set_task_status(task_id_str, "running")
            await redis_client.publish_event(task_id_str, {"type": "status", "data": {"status": "running"}})

            # 获取项目路径
            project_path = project.path
            if project_path.startswith("server:///"):
                project_path = project_path[len("server://"):]
            elif project_path.startswith("server://"):
                project_path = project_path[len("server://"):]

            # 检查是否是 git 仓库，决定使用调度路径还是单 Agent 路径
            if project.project_type == "local" or not self._is_git_repo(project_path):
                result = await self._execute_single_agent(
                    task_id, task_id_str, project, agent_model, llm_model, prompt, project_path
                )
            else:
                result = await self._execute_scheduled(
                    task_id, task_id_str, project, agent_model, llm_model, prompt, project_path
                )

            # Update task
            task = await self.db.get(Task, task_id)
            task.output = result
            task.status = TaskStatus.COMPLETED
            await self.db.commit()

            await redis_client.set_task_status(task_id_str, "completed")
            await redis_client.publish_event(task_id_str, {"type": "status", "data": {"status": "completed"}})

        except Exception as e:
            logger.exception(f"Agent execution failed for task {task_id}")
            task = await self.db.get(Task, task_id)
            if task:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                await self.db.commit()

            await redis_client.set_task_status(task_id_str, "failed")
            await redis_client.publish_event(task_id_str, {"type": "error", "data": {"message": str(e)}})

    async def _execute_single_agent(
        self, task_id: UUID, task_id_str: str,
        project: Project, agent_model: AgentModel, llm_model: LLM,
        prompt: str, project_path: str,
    ) -> str:
        """单 Agent 执行路径（非 git 仓库或 local 项目）。"""
        # Create tool executor
        if project.project_type == "local":
            from neuralswarm.services.bridge import BridgeRouter
            from neuralswarm.api.ws_client import get_client_manager
            bridge = BridgeRouter(get_client_manager())
            tool_executor = ToolExecutor(
                project_path="",
                bridge=bridge,
                project_type="local",
                project_uri=project.path,
            )
        else:
            tool_executor = ToolExecutor(project_path=project_path)

        tool_executor.register_defaults()

        agent_repo = AgentRepository(self.db)
        agent = Agent(
            agent_id=agent_model.id,
            project_id=project.id,
            tools=tool_executor.list_tools(),
            llm_gateway=self.llm_gateway,
            agent_repo=agent_repo,
            tool_executor=tool_executor,
            context_manager=ContextManager(),
        )

        async def on_event(event_type: str, data: dict):
            await redis_client.publish_event(task_id_str, {"type": event_type, "data": data})

        return await agent.execute(
            task=prompt,
            llm_id=llm_model.id,
            provider=llm_model.provider,
            model_id=llm_model.model_id,
            on_event=on_event,
        )

    async def _execute_scheduled(
        self, task_id: UUID, task_id_str: str,
        project: Project, agent_model: AgentModel, llm_model: LLM,
        prompt: str, project_path: str,
    ) -> str:
        """调度执行路径（git 仓库项目）。"""
        from neuralswarm.core.scheduler.agent_pool import AgentPool
        from neuralswarm.core.scheduler.central import CentralScheduler
        from neuralswarm.core.scheduler.sub_scheduler import SubSchedulerAgent
        from neuralswarm.core.concurrency.conflict_manager import ConflictManager
        from neuralswarm.core.git.worktree import WorktreeManager

        # 1. 创建调度组件
        worktree_manager = WorktreeManager(base_path=project_path)
        agent_pool = AgentPool(max_concurrent=5)
        conflict_manager = ConflictManager()
        agent_repo = AgentRepository(self.db)

        scheduler = CentralScheduler(
            agent_pool=agent_pool,
            worktree_manager=worktree_manager,
        )

        # 2. 准备工具
        tool_executor = ToolExecutor(project_path=project_path)
        tool_executor.register_defaults()
        tool_names = tool_executor.list_tools()

        # 3. 提交任务 → 创建 worktree + sub-scheduler agent
        runtime = await scheduler.submit_task(
            task_id=task_id,
            project_id=project.id,
            agent_repo=agent_repo,
            prompt=prompt,
            llm_config={
                "provider": llm_model.provider,
                "model_id": llm_model.model_id,
            },
            tools=tool_names,
        )

        # 4. 创建 SubSchedulerAgent
        hash_guard = scheduler.task_hash_guards[task_id]
        sub_scheduler = SubSchedulerAgent(
            agent_id=runtime.id,
            task_id=task_id,
            central_scheduler=scheduler,
            hash_guard=hash_guard,
            conflict_manager=conflict_manager,
            llm_gateway=self.llm_gateway,
            agent_repo=agent_repo,
        )

        # 5. 分析任务 → 生成计划
        async def on_event(event_type: str, data: dict):
            await redis_client.publish_event(task_id_str, {"type": event_type, "data": data})

        await on_event("plan_start", {"prompt": prompt})
        plan = await sub_scheduler.analyze_task(prompt)
        await on_event("plan_generated", {"steps": len(plan), "plan": plan})

        # 6. 执行计划
        result = await sub_scheduler.execute_plan(plan)
        await on_event("plan_completed", result)

        # 7. 完成任务
        await scheduler.complete_task(task_id, agent_repo=agent_repo)

        # 返回结果摘要
        if result["success"]:
            outputs = [r.get("output", "") for r in result["results"]]
            return "\n".join(outputs)
        else:
            return f"Errors: {', '.join(result['errors'])}"

    async def _get_or_create_default_agent(self, project_id: UUID) -> AgentModel:
        """Get or create default agent for project."""
        stmt = select(AgentModel).where(AgentModel.project_id == project_id).limit(1)
        result = await self.db.execute(stmt)
        agent = result.scalar_one_or_none()
        if not agent:
            agent = AgentModel(project_id=project_id, name="default-agent", status=AgentStatus.IDLE)
            self.db.add(agent)
            await self.db.commit()
            await self.db.refresh(agent)
        return agent

    async def _get_default_llm(self) -> LLM:
        """Get default LLM."""
        stmt = select(LLM).limit(1)
        result = await self.db.execute(stmt)
        llm = result.scalar_one_or_none()
        if not llm:
            raise ValueError("No LLM configured. Run seed data first.")
        return llm
