from __future__ import annotations

import asyncio
import logging
from uuid import UUID
from neuralswarm.core.repository import AgentRepository
from neuralswarm.models import Agent
from neuralswarm.models.enums import AgentStatus, AgentType

logger = logging.getLogger(__name__)


class AgentRuntime:
    """Agent 运行时包装器，组合 DB 模型与运行时状态。"""

    def __init__(self, agent_model: Agent):
        self.model = agent_model
        self.id: UUID = agent_model.id
        self.type: AgentType = agent_model.agent_type
        self.status: AgentStatus = agent_model.status
        self._started = False

    async def start(self, agent_repo: AgentRepository):
        """启动 Agent，更新状态为 RUNNING。"""
        await agent_repo.update_status(self.id, AgentStatus.RUNNING)
        self.status = AgentStatus.RUNNING
        self._started = True
        logger.info("Agent %s started (type=%s)", self.id, self.type)

    async def stop(self, agent_repo: AgentRepository, final_status: AgentStatus = AgentStatus.COMPLETED):
        """停止 Agent，更新状态为终态。"""
        await agent_repo.update_status(self.id, final_status)
        self.status = final_status
        self._started = False
        logger.info("Agent %s stopped with status=%s", self.id, final_status)


class AgentPool:
    """管理 Agent 实例的并发池。"""

    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_agents: dict[UUID, AgentRuntime] = {}  # agent_id -> runtime

    async def create_agent(
        self,
        agent_repo: AgentRepository,
        agent_type: AgentType,
        task_id: UUID,
        project_id: UUID,
        worktree_path: str,
        llm_config: dict,
        tools: list[str],
        name: str = "",
        parent_id: UUID | None = None,
    ) -> AgentRuntime:
        """创建 Agent 并注册到池中。

        1. 创建 DB 记录
        2. 包装为 AgentRuntime
        3. 注册到 active_agents
        """
        agent = Agent(
            project_id=project_id,
            name=name or f"agent-{agent_type.value}",
            agent_type=agent_type,
            status=AgentStatus.IDLE,
            task_id=task_id,
            parent_id=parent_id,
            tools=tools,
            llm_config=llm_config,
            worktree_path=worktree_path,
        )

        try:
            agent = await agent_repo.create_agent(agent)
        except Exception:
            logger.exception("Failed to create agent (type=%s, task=%s)", agent_type, task_id)
            raise

        runtime = AgentRuntime(agent_model=agent)
        self.active_agents[agent.id] = runtime
        logger.info("Agent %s created (type=%s, task=%s)", agent.id, agent_type, task_id)
        return runtime

    async def destroy_agent(self, agent_id: UUID, agent_repo: AgentRepository, failed: bool = False):
        """销毁 Agent 并清理资源。

        1. 从 active_agents 移除
        2. 更新 DB 状态为 COMPLETED 或 FAILED
        """
        runtime = self.active_agents.pop(agent_id, None)
        if runtime is None:
            logger.warning("Agent %s not found in pool", agent_id)
            return

        final_status = AgentStatus.FAILED if failed else AgentStatus.COMPLETED
        await runtime.stop(agent_repo, final_status=final_status)
        logger.info("Agent %s destroyed (status=%s)", agent_id, final_status)

    def get_agent(self, agent_id: UUID) -> AgentRuntime | None:
        """获取运行中的 Agent。"""
        return self.active_agents.get(agent_id)

    def list_agents(self) -> list[AgentRuntime]:
        """列出所有活跃 Agent。"""
        return list(self.active_agents.values())

    async def execute_with_limit(self, agent_id: UUID, coro):
        """在并发限制下执行协程。"""
        async with self.semaphore:
            logger.debug("Agent %s acquired semaphore slot", agent_id)
            try:
                return await coro
            finally:
                logger.debug("Agent %s released semaphore slot", agent_id)
