import pytest
from neuralswarm.models import (
    Agent,
    AuditLog,
    GlobalMemory,
    LLM,
    Lock,
    Project,
    ProjectMemory,
    Task,
    TaskStatus,
    AgentStatus,
    AgentType,
    LockMode,
    MemoryLevel,
)


def test_project_has_tablename():
    assert Project.__tablename__ == "projects"


def test_agent_has_tablename():
    assert Agent.__tablename__ == "agents"


def test_llm_has_tablename():
    assert LLM.__tablename__ == "llms"


def test_task_has_tablename():
    assert Task.__tablename__ == "tasks"


def test_lock_has_tablename():
    assert Lock.__tablename__ == "locks"


def test_project_memory_has_tablename():
    assert ProjectMemory.__tablename__ == "project_memories"


def test_global_memory_has_tablename():
    assert GlobalMemory.__tablename__ == "global_memories"


def test_audit_log_has_tablename():
    assert AuditLog.__tablename__ == "audit_logs"


def test_task_status_enum():
    assert TaskStatus.PENDING == "pending"
    assert TaskStatus.COMPLETED == "completed"


def test_agent_status_enum():
    assert AgentStatus.IDLE == "idle"
    assert AgentStatus.RUNNING == "running"
    assert AgentStatus.PLANNING == "planning"
    assert AgentStatus.WAITING == "waiting"
    assert AgentStatus.COMPLETED == "completed"
    assert AgentStatus.FAILED == "failed"


def test_agent_type_enum():
    assert AgentType.SCHEDULER == "scheduler"
    assert AgentType.WORKER == "worker"


def test_lock_mode_enum():
    assert LockMode.X == "X"
    assert LockMode.S == "S"


def test_memory_level_enum():
    assert MemoryLevel.L1 == "L1"
    assert MemoryLevel.L2 == "L2"
    assert MemoryLevel.L3 == "L3"
