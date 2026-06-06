from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from neuralswarm.models import Agent, Task
from neuralswarm.models.enums import AgentStatus, TaskStatus


class AgentRepository:
    """Agent 数据库操作。"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_agent(self, agent_id: UUID) -> Agent | None:
        """获取 Agent。"""
        result = await self.session.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        return result.scalar_one_or_none()

    async def update_status(self, agent_id: UUID, status: AgentStatus):
        """更新 Agent 状态。"""
        await self.session.execute(
            update(Agent).where(Agent.id == agent_id).values(status=status)
        )
        await self.session.commit()

    async def save_context(self, agent_id: UUID, context: dict):
        """保存 Agent 上下文。"""
        await self.session.execute(
            update(Agent).where(Agent.id == agent_id).values(context=context)
        )
        await self.session.commit()

    async def create_task(self, task: Task) -> Task:
        """创建任务。"""
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def update_task(
        self,
        task_id: UUID,
        status: TaskStatus,
        output: str | None = None,
        error: str | None = None,
    ):
        """更新任务状态。"""
        values = {"status": status}
        if output is not None:
            values["output"] = output
        if error is not None:
            values["error"] = error
        await self.session.execute(
            update(Task).where(Task.id == task_id).values(**values)
        )
        await self.session.commit()
