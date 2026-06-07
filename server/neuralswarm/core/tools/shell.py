import asyncio

from neuralswarm.core.tool_metadata import ToolMetadata, ToolParameter


def create_shell(project_path: str):
    """创建 shell 工具，绑定项目路径作为默认 cwd。"""

    async def shell(command: str, timeout: int = 30, cwd: str | None = None) -> str:
        """执行 shell 命令。cwd 默认为项目路径。"""
        effective_cwd = cwd or project_path
        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=effective_cwd,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            output = stdout.decode("utf-8", errors="replace")
            if stderr:
                output += "\n" + stderr.decode("utf-8", errors="replace")
            return output.strip()
        except asyncio.TimeoutError:
            return f"Error: Command timed out after {timeout}s"
        except Exception as e:
            return f"Error executing command: {e}"

    meta = ToolMetadata(
        name="shell",
        description="Execute shell command. Working directory defaults to project directory.",
        parameters=[
            ToolParameter(name="command", type="string", description="Shell command to execute"),
            ToolParameter(name="timeout", type="integer", description="Timeout in seconds", required=False, default=30),
            ToolParameter(name="cwd", type="string", description="Working directory override (absolute path)", required=False),
        ],
    )

    return shell, meta
