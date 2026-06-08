"""E2E 测试 fixtures。"""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from neuralswarm.core.concurrency.hash_guard import HashGuard
from neuralswarm.core.concurrency.conflict_manager import ConflictManager
from neuralswarm.core.git.worktree import WorktreeManager, WorktreeInfo
from neuralswarm.core.scheduler.agent_pool import AgentPool, AgentRuntime
from neuralswarm.core.scheduler.central import CentralScheduler
from neuralswarm.core.scheduler.sub_scheduler import SubSchedulerAgent
from neuralswarm.models.enums import AgentType, AgentStatus


@pytest.fixture
async def temp_git_repo(tmp_path):
    """创建临时 git 仓库。"""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    # git init
    proc = await asyncio.create_subprocess_exec(
        "git", "init",
        cwd=str(repo_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()

    # git config
    proc = await asyncio.create_subprocess_exec(
        "git", "config", "user.email", "test@test.com",
        cwd=str(repo_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()

    proc = await asyncio.create_subprocess_exec(
        "git", "config", "user.name", "Test",
        cwd=str(repo_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()

    # initial commit
    readme = repo_path / "README.md"
    readme.write_text("# Test Repo")
    proc = await asyncio.create_subprocess_exec(
        "git", "add", ".",
        cwd=str(repo_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()

    proc = await asyncio.create_subprocess_exec(
        "git", "commit", "-m", "initial",
        cwd=str(repo_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()

    return repo_path


@pytest.fixture
def worktree_manager(temp_git_repo):
    """创建真实的 WorktreeManager。"""
    return WorktreeManager(base_path=str(temp_git_repo))


@pytest.fixture
def agent_pool():
    """创建 AgentPool（mock DB）。"""
    pool = AgentPool(max_concurrent=5)
    return pool


@pytest.fixture
def mock_agent_repo():
    """创建 mock AgentRepository。"""
    repo = AsyncMock()

    async def create_agent(agent):
        agent.id = uuid4()
        return agent

    repo.create_agent = AsyncMock(side_effect=create_agent)
    return repo


@pytest.fixture
def central_scheduler(agent_pool, worktree_manager):
    """创建 CentralScheduler。"""
    return CentralScheduler(
        agent_pool=agent_pool,
        worktree_manager=worktree_manager,
    )


@pytest.fixture
def conflict_manager():
    """创建 ConflictManager。"""
    return ConflictManager()


class FakeLLMResponse:
    def __init__(self, content):
        self.content = content


class FakeLLMGateway:
    """Fake LLM Gateway，返回预定义的计划。"""

    def __init__(self, plan):
        self.plan = plan

    async def chat(self, messages=None, **kwargs):
        import json
        return FakeLLMResponse(content=json.dumps(self.plan))


@pytest.fixture
def fake_llm_simple():
    """返回简单计划的 Fake LLM。"""
    return FakeLLMGateway(plan=[
        {
            "type": "shell",
            "command": "echo 'hello from LLM'",
            "description": "LLM generated step",
            "is_simple": True,
        }
    ])


@pytest.fixture
def fake_llm_file_ops(tmp_path):
    """返回文件操作计划的 Fake LLM。"""
    return FakeLLMGateway(plan=[
        {
            "type": "file_create",
            "path": "src/hello.py",
            "content": "print('hello world')",
            "description": "Create hello.py",
            "is_simple": True,
        },
        {
            "type": "file_edit",
            "path": "src/hello.py",
            "content": "print('hello world edited')",
            "description": "Edit hello.py",
            "is_simple": True,
        },
    ])
