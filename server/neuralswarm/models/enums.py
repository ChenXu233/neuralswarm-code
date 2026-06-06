from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


class LockMode(str, Enum):
    X = "X"
    S = "S"
    IX = "IX"
    IS = "IS"


class MemoryLevel(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
