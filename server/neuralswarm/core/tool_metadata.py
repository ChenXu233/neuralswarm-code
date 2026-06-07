from dataclasses import dataclass, field


@dataclass
class ToolParameter:
    """工具参数定义。"""
    name: str
    type: str  # "string", "integer", "boolean", "number"
    description: str
    required: bool = True
    enum: list[str] | None = None
    default: object = None


@dataclass
class ToolMetadata:
    """工具元数据，用于 LLM function calling。"""
    name: str
    description: str
    parameters: list[ToolParameter] = field(default_factory=list)

    def to_openai_schema(self) -> dict:
        """转换为 OpenAI function calling 格式。"""
        properties = {}
        required = []
        for p in self.parameters:
            prop: dict = {"type": p.type, "description": p.description}
            if p.enum:
                prop["enum"] = p.enum
            properties[p.name] = prop
            if p.required:
                required.append(p.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    def to_anthropic_schema(self) -> dict:
        """转换为 Anthropic tool use 格式。"""
        properties = {}
        required = []
        for p in self.parameters:
            prop: dict = {"type": p.type, "description": p.description}
            if p.enum:
                prop["enum"] = p.enum
            properties[p.name] = prop
            if p.required:
                required.append(p.name)

        return {
            "name": self.name,
            "description": self.description,
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }
