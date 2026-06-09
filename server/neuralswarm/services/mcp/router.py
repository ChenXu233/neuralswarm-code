"""MCP 路由 - 项目路由"""

import logging

logger = logging.getLogger(__name__)


class McpRouter:
    """MCP 路由"""

    def __init__(self):
        self._project_clients: dict[str, str] = {}  # project_id -> client_id

    def register_project(self, project_id: str, client_id: str) -> None:
        """注册项目到客户端"""
        self._project_clients[project_id] = client_id
        logger.info("Registered project %s to client %s", project_id, client_id)

    def get_client_for_project(self, project_id: str) -> str | None:
        """获取项目对应的客户端"""
        return self._project_clients.get(project_id)

    def list_projects(self) -> list[str]:
        """列出所有项目"""
        return list(self._project_clients.keys())


# 全局 MCP 路由实例
mcp_router = McpRouter()
