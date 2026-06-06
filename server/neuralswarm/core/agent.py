from __future__ import annotations
from uuid import UUID

from neuralswarm.core.context_manager import ContextManager
from neuralswarm.core.repository import AgentRepository
from neuralswarm.core.tool_executor import ToolExecutor
from neuralswarm.models.enums import AgentStatus
from neuralswarm.services.llm.gateway import LLMGateway
from neuralswarm.services.llm.types import LLMError


class Agent:
    """有状态的 Agent 运行时。"""

    def __init__(
        self,
        agent_id: UUID,
        project_id: UUID,
        tools: list[str],
        llm_gateway: LLMGateway,
        agent_repo: AgentRepository,
        tool_executor: ToolExecutor,
        context_manager: ContextManager,
    ):
        self.agent_id = agent_id
        self.project_id = project_id
        self.tools = tools
        self.llm_gateway = llm_gateway
        self.agent_repo = agent_repo
        self.tool_executor = tool_executor
        self.context_manager = context_manager

    async def execute(
        self,
        task: str,
        llm_id: UUID,
        provider: str,
        model_id: str,
        max_iterations: int = 10,
    ) -> str:
        """执行任务，返回结果。"""
        await self.agent_repo.update_status(self.agent_id, AgentStatus.RUNNING)

        try:
            self.context_manager.add_message("user", task)

            for _ in range(max_iterations):
                messages = self.context_manager.get_messages()

                response = await self.llm_gateway.chat(
                    provider=provider,
                    model_id=model_id,
                    messages=messages,
                )

                self.context_manager.update_tokens(response.usage)

                if self.context_manager.auto_compact_check():
                    summary_response = await self.llm_gateway.chat(
                        provider=provider,
                        model_id=model_id,
                        messages=[
                            {"role": "system", "content": "Summarize the conversation concisely."},
                            *self.context_manager.get_messages(),
                        ],
                    )
                    self.context_manager.compact(summary_response.content)

                self.context_manager.add_message("assistant", response.content)

                await self.agent_repo.save_context(
                    self.agent_id,
                    {"messages": self.context_manager.get_messages()},
                )

                await self.agent_repo.update_status(self.agent_id, AgentStatus.IDLE)
                return response.content

            await self.agent_repo.update_status(self.agent_id, AgentStatus.IDLE)
            return "Error: Max iterations reached"

        except LLMError as e:
            await self.agent_repo.update_status(self.agent_id, AgentStatus.IDLE)
            return f"Error: {e}"
        except Exception as e:
            await self.agent_repo.update_status(self.agent_id, AgentStatus.IDLE)
            return f"Error: {e}"
