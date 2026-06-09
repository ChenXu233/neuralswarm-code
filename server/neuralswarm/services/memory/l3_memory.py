"""L3 过程性记忆 - 用户偏好"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class L3Memory:
    """L3 过程性记忆 - 使用内存存储"""

    def __init__(self):
        self._preferences: dict[str, dict[str, Any]] = {}  # user_id -> preferences

    async def save_preference(
        self,
        user_id: str,
        preference: dict[str, Any]
    ) -> None:
        """保存用户偏好"""
        self._preferences[user_id] = preference
        logger.debug("Saved preference for user %s", user_id)

    async def get_preference(
        self,
        user_id: str
    ) -> dict[str, Any] | None:
        """获取用户偏好"""
        return self._preferences.get(user_id)

    async def inject_preferences(
        self,
        user_id: str,
        system_prompt: str
    ) -> str:
        """将用户偏好注入 System Prompt"""
        preference = await self.get_preference(user_id)
        if not preference:
            return system_prompt

        # 构建偏好描述
        pref_lines = []
        for key, value in preference.items():
            pref_lines.append(f"- {key}: {value}")

        pref_text = "\n".join(pref_lines)

        return f"""{system_prompt}

用户偏好：
{pref_text}

请根据用户偏好调整你的回答风格。"""


# 全局 L3 记忆实例
l3_memory = L3Memory()
