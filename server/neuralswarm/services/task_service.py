import asyncio
import logging
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

    async def _execute_agent(self, task_id: UUID, project: Project, agent_model: AgentModel, llm_model: LLM, prompt: str):
        """Execute agent in background."""
        task_id_str = str(task_id)

        try:
            await redis_client.set_task_status(task_id_str, "running")
            await redis_client.publish_event(task_id_str, {"type": "status", "data": {"status": "running"}})

            # Extract project path
            project_path = project.path
            if project_path.startswith("server:///"):
                project_path = project_path[len("server://"):]
            elif project_path.startswith("server://"):
                project_path = project_path[len("server://"):]

            # Create tool executor with project path
            tool_executor = ToolExecutor(project_path=project_path)
            tool_executor.register_defaults()

            # Create agent repository
            agent_repo = AgentRepository(self.db)

            # Create agent
            agent = Agent(
                agent_id=agent_model.id,
                project_id=project.id,
                tools=tool_executor.list_tools(),
                llm_gateway=self.llm_gateway,
                agent_repo=agent_repo,
                tool_executor=tool_executor,
                context_manager=ContextManager(),
            )

            # Event callback for Redis
            async def on_event(event_type: str, data: dict):
                await redis_client.publish_event(task_id_str, {"type": event_type, "data": data})

            # Execute
            result = await agent.execute(
                task=prompt,
                llm_id=llm_model.id,
                provider=llm_model.provider,
                model_id=llm_model.model_id,
                on_event=on_event,
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
