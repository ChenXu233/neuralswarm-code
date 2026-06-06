import pytest
from unittest.mock import AsyncMock, MagicMock
from neuralswarm.core.repository import AgentRepository
from neuralswarm.models.enums import AgentStatus, TaskStatus


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repo(mock_session):
    return AgentRepository(mock_session)


@pytest.mark.asyncio
async def test_update_status(repo, mock_session):
    await repo.update_status("agent-id", AgentStatus.RUNNING)
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_task(repo, mock_session):
    await repo.update_task("task-id", TaskStatus.COMPLETED, output="result")
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_called_once()
