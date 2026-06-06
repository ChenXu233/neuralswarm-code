"""Seed data for development and testing."""

import asyncio
from neuralswarm.database import get_engine, get_session_factory
from neuralswarm.models import Project, Agent, LLM, Task, TaskStatus


async def seed():
    """插入测试数据。"""
    engine = get_engine()
    factory = get_session_factory(engine)

    async with factory() as session:
        # 检查是否已有数据
        from sqlalchemy import select
        result = await session.execute(select(Project))
        if result.scalars().first():
            print("Seed data already exists, skipping.")
            return

        # 创建测试项目
        project = Project(
            name="test-project",
            path="/home/user/test-project",
            config={"language": "python"},
        )
        session.add(project)
        await session.flush()

        # 创建测试 Agent
        agent1 = Agent(
            project_id=project.id,
            name="code-agent",
            tools=["file_read", "file_write", "shell", "git"],
        )
        agent2 = Agent(
            project_id=project.id,
            name="review-agent",
            tools=["file_read", "git_diff", "comment"],
        )
        session.add_all([agent1, agent2])
        await session.flush()

        # 创建预注册 LLM
        llm1 = LLM(
            model_id="claude-opus-4-6",
            provider="claude",
            gateway_route="claude-opus",
            capabilities={"codegen": 5, "reasoning": 5, "long_context": 5},
            cost_tier="high",
            rate_limit={"rpm": 30, "tpm": 50000},
        )
        llm2 = LLM(
            model_id="claude-sonnet-4-6",
            provider="claude",
            gateway_route="claude-sonnet",
            capabilities={"codegen": 4, "reasoning": 4, "long_context": 4},
            cost_tier="medium",
            rate_limit={"rpm": 60, "tpm": 100000},
        )
        llm3 = LLM(
            model_id="deepseek-v3",
            provider="openai_compat",
            gateway_route="deepseek",
            capabilities={"codegen": 4, "reasoning": 3, "long_context": 3},
            cost_tier="low",
            rate_limit={"rpm": 100, "tpm": 200000},
            is_free_tier=True,
        )
        session.add_all([llm1, llm2, llm3])
        await session.flush()

        # 创建测试任务
        task = Task(
            project_id=project.id,
            agent_id=agent1.id,
            llm_id=llm2.id,
            input="列出当前目录的文件",
            status=TaskStatus.COMPLETED,
            output="file1.py\nfile2.py\nREADME.md",
        )
        session.add(task)

        await session.commit()
        print("Seed data inserted successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
