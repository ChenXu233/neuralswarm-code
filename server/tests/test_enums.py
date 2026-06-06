from neuralswarm.models.enums import TaskStatus, AgentStatus, LockMode, MemoryLevel


def test_task_status_values():
    assert TaskStatus.PENDING == "pending"
    assert TaskStatus.RUNNING == "running"
    assert TaskStatus.COMPLETED == "completed"
    assert TaskStatus.FAILED == "failed"
    assert TaskStatus.CANCELLED == "cancelled"


def test_agent_status_values():
    assert AgentStatus.IDLE == "idle"
    assert AgentStatus.RUNNING == "running"
    assert AgentStatus.PAUSED == "paused"
    assert AgentStatus.STOPPED == "stopped"


def test_lock_mode_values():
    assert LockMode.X == "X"
    assert LockMode.S == "S"
    assert LockMode.IX == "IX"
    assert LockMode.IS == "IS"


def test_memory_level_values():
    assert MemoryLevel.L1 == "L1"
    assert MemoryLevel.L2 == "L2"
    assert MemoryLevel.L3 == "L3"
