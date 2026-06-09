import pytest

from neuralswarm.services.memory.l3_memory import L3Memory


@pytest.fixture
def l3_memory():
    return L3Memory()


async def test_save_preference(l3_memory):
    """测试保存用户偏好"""
    preference = {
        "language": "中文",
        "tone": "正式",
        "detail_level": "详细"
    }

    await l3_memory.save_preference("user-1", preference)

    assert l3_memory._preferences["user-1"] == preference


async def test_get_preference(l3_memory):
    """测试获取用户偏好"""
    preference = {"language": "English", "tone": "casual"}
    l3_memory._preferences["user-2"] = preference

    result = await l3_memory.get_preference("user-2")

    assert result == preference


async def test_get_preference_returns_none_for_unknown_user(l3_memory):
    """测试获取不存在用户的偏好返回 None"""
    result = await l3_memory.get_preference("nonexistent")

    assert result is None


async def test_save_preference_overwrites_existing(l3_memory):
    """测试保存偏好会覆盖已有偏好"""
    old_preference = {"language": "English"}
    new_preference = {"language": "中文", "tone": "正式"}

    await l3_memory.save_preference("user-1", old_preference)
    await l3_memory.save_preference("user-1", new_preference)

    result = await l3_memory.get_preference("user-1")

    assert result == new_preference


async def test_user_preference_isolation(l3_memory):
    """测试不同用户的偏好互相隔离"""
    preference_1 = {"language": "中文"}
    preference_2 = {"language": "English"}

    await l3_memory.save_preference("user-1", preference_1)
    await l3_memory.save_preference("user-2", preference_2)

    result_1 = await l3_memory.get_preference("user-1")
    result_2 = await l3_memory.get_preference("user-2")

    assert result_1 == preference_1
    assert result_2 == preference_2


async def test_inject_preferences(l3_memory):
    """测试注入用户偏好到 System Prompt"""
    preference = {
        "language": "中文",
        "tone": "正式"
    }
    system_prompt = "你是一个有用的助手。"

    await l3_memory.save_preference("user-1", preference)

    result = await l3_memory.inject_preferences("user-1", system_prompt)

    assert "你是一个有用的助手。" in result
    assert "用户偏好：" in result
    assert "- language: 中文" in result
    assert "- tone: 正式" in result
    assert "请根据用户偏好调整你的回答风格。" in result


async def test_inject_preferences_returns_original_for_unknown_user(l3_memory):
    """测试无偏好时返回原始 System Prompt"""
    system_prompt = "你是一个有用的助手。"

    result = await l3_memory.inject_preferences("nonexistent", system_prompt)

    assert result == system_prompt


async def test_inject_preferences_returns_original_for_empty_preference(l3_memory):
    """测试空偏好时返回原始 System Prompt"""
    system_prompt = "你是一个有用的助手。"

    await l3_memory.save_preference("user-1", {})

    result = await l3_memory.inject_preferences("user-1", system_prompt)

    # 空字典是 falsy，所以应该返回原始 prompt
    assert result == system_prompt


async def test_inject_preferences_preserves_original_prompt(l3_memory):
    """测试注入偏好时保留原始 System Prompt"""
    preference = {"style": "简洁"}
    system_prompt = "你是一个翻译助手。请将用户输入翻译成英文。"

    await l3_memory.save_preference("user-1", preference)

    result = await l3_memory.inject_preferences("user-1", system_prompt)

    # 原始 prompt 应该在结果的开头
    assert result.startswith(system_prompt)


async def test_multiple_preferences_injection(l3_memory):
    """测试多个偏好的注入"""
    preference = {
        "language": "中文",
        "tone": "友好",
        "detail_level": "简洁",
        "examples": "需要"
    }
    system_prompt = "你是一个助手。"

    await l3_memory.save_preference("user-1", preference)

    result = await l3_memory.inject_preferences("user-1", system_prompt)

    for key, value in preference.items():
        assert f"- {key}: {value}" in result


async def test_l3_memory_instance_independence():
    """测试不同 L3Memory 实例互相独立"""
    memory_1 = L3Memory()
    memory_2 = L3Memory()

    await memory_1.save_preference("user-1", {"language": "中文"})

    result = await memory_2.get_preference("user-1")

    assert result is None
