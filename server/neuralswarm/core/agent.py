from __future__ import annotations
from uuid import UUID

from neuralswarm.core.context_manager import ContextManager
from neuralswarm.core.repository import AgentRepository
from neuralswarm.core.tool_executor import ToolExecutor
from neuralswarm.models.enums import AgentStatus
from neuralswarm.services.llm.gateway import LLMGateway
from neuralswarm.services.llm.types import LLMError
from neuralswarm.services.memory.l0_memory import l0_memory
from neuralswarm.services.memory.l1_memory import l1_memory
from neuralswarm.services.memory.l3_memory import l3_memory
from neuralswarm.services.event_bus import event_bus


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
        on_event=None,
    ) -> str:
        """执行任务，返回结果。"""
        await self.agent_repo.update_status(self.agent_id, AgentStatus.RUNNING)

        try:
            # 记录任务开始事件到 L1 记忆
            await l1_memory.record_event(
                str(self.project_id),
                "task_start",
                f"Agent {self.agent_id} 开始执行任务: {task[:100]}..."
            )

            # 发布事件到事件总线
            await event_bus.publish("agent.task_start", {
                "agent_id": str(self.agent_id),
                "project_id": str(self.project_id),
                "task": task[:100],
            })

            self.context_manager.add_message("user", task)

            for iteration in range(max_iterations):
                messages = self.context_manager.get_messages()

                # Get tool schemas
                tools = None
                if self.tool_executor.list_tools():
                    tools = (
                        self.tool_executor.to_openai_tools()
                        if provider == "openai"
                        else self.tool_executor.to_anthropic_tools()
                    )

                response = await self.llm_gateway.chat(
                    provider=provider,
                    model_id=model_id,
                    messages=messages,
                    tools=tools,
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

                # Tool calls
                if response.tool_calls:
                    self.context_manager.add_message(
                        "assistant", response.content or "", tool_calls=response.tool_calls
                    )

                    for call in response.tool_calls:
                        if on_event:
                            await on_event("tool_call", {
                                "call_id": call.id,
                                "tool": call.name,
                                "args": call.arguments,
                            })

                        # 记录工具调用到 L1 记忆
                        await l1_memory.record_event(
                            str(self.project_id),
                            "tool_call",
                            f"调用工具: {call.name}"
                        )

                        result = await self.tool_executor.execute(call.name, call.arguments)
                        self.context_manager.add_tool_result(call.id, result)

                        if on_event:
                            await on_event("tool_result", {
                                "call_id": call.id,
                                "tool": call.name,
                                "output": result,
                            })
                else:
                    # Final response
                    self.context_manager.add_message("assistant", response.content)

                    if on_event:
                        await on_event("message", {"content": response.content})

                    await self.agent_repo.save_context(
                        self.agent_id,
                        {"messages": self.context_manager.get_messages()},
                    )
                    await self.agent_repo.update_status(self.agent_id, AgentStatus.IDLE)

                    # 记录任务完成事件到 L1 记忆
                    await l1_memory.record_event(
                        str(self.project_id),
                        "task_complete",
                        f"Agent {self.agent_id} 完成任务"
                    )

                    # 发布事件到事件总线
                    await event_bus.publish("agent.task_complete", {
                        "agent_id": str(self.agent_id),
                        "project_id": str(self.project_id),
                    })

                    # 存储最终结果到 L3 记忆（长期记忆）
                    # L3 记忆主要用于用户偏好，这里记录到 L1 事件
                    await l1_memory.record_event(
                        str(self.project_id),
                        "task_result_stored",
                        f"任务结果已存储: {response.content[:100]}..."
                    )

                    return response.content

            await self.agent_repo.update_status(self.agent_id, AgentStatus.IDLE)
            return "Error: Max iterations reached"

        except LLMError as e:
            await self.agent_repo.update_status(self.agent_id, AgentStatus.IDLE)
            # 记录错误事件到 L1 记忆
            await l1_memory.record_event(
                str(self.project_id),
                "task_error",
                f"Agent {self.agent_id} 执行失败: {str(e)}"
            )
            return f"Error: {e}"
        except Exception as e:
            await self.agent_repo.update_status(self.agent_id, AgentStatus.IDLE)
            # 记录错误事件到 L1 记忆
            await l1_memory.record_event(
                str(self.project_id),
                "task_error",
                f"Agent {self.agent_id} 执行失败: {str(e)}"
            )
            return f"Error: {e}"
