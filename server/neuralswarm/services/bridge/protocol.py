from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class ExecuteCommand:
    """Server → Client: execute command."""
    command: str  # file_read, file_write, shell
    params: dict
    request_id: str = field(default_factory=lambda: str(uuid4()))

    def to_json(self) -> dict:
        return {
            "type": "execute",
            "command": self.command,
            "params": self.params,
            "request_id": self.request_id,
        }


@dataclass
class CommandResult:
    """Client → Server: execution result."""
    request_id: str
    status: str  # "success" or "error"
    data: dict = field(default_factory=dict)

    @classmethod
    def from_json(cls, data: dict) -> "CommandResult":
        return cls(
            request_id=data["request_id"],
            status=data["status"],
            data=data.get("data", {}),
        )
