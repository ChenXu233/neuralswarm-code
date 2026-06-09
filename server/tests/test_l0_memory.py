import pytest
from neuralswarm.services.memory.l0_memory import L0Memory

@pytest.fixture
def l0_memory():
    return L0Memory()

async def test_save_and_load_context(l0_memory):
    """测试保存和加载上下文"""
    agent_id = "test-agent"
    context = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]

    await l0_memory.save_context(agent_id, context)
    loaded = await l0_memory.load_context(agent_id)

    assert loaded == context

async def test_compact_context(l0_memory):
    """测试上下文压缩"""
    agent_id = "test-agent"
    context = [
        {"role": "user", "content": "Message 1"},
        {"role": "assistant", "content": "Response 1"},
        {"role": "user", "content": "Message 2"},
        {"role": "assistant", "content": "Response 2"},
        {"role": "user", "content": "Message 3"},
        {"role": "assistant", "content": "Response 3"},
    ]

    await l0_memory.save_context(agent_id, context)
    compacted = await l0_memory.compact_context(agent_id, keep_last=2)

    assert len(compacted) == 2
    assert compacted[-1]["content"] == "Response 3"
