from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentStatus(str, Enum):
    IDLE = "idle"           # 空闲，等待任务
    PLANNING = "planning"   # Sub-scheduler 对话规划中
    RUNNING = "running"     # 执行中
    WAITING = "waiting"     # 等待资源/锁
    COMPLETED = "completed" # 完成
    FAILED = "failed"       # 失败


class AgentType(str, Enum):
    SCHEDULER = "scheduler"   # Sub-scheduler LLM（规划+执行）
    WORKER = "worker"         # Worker Agent（执行具体工作）


class LockMode(str, Enum):
    X = "X"
    S = "S"
    IX = "IX"
    IS = "IS"


class MemoryLevel(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class ConflictStatus(str, Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
    TIMEOUT = "timeout"


class ConflictAction(str, Enum):
    RE_READ = "re_read"
    OVERWRITE = "overwrite"
    SUBMIT_TO_SCHEDULER = "submit_to_scheduler"
