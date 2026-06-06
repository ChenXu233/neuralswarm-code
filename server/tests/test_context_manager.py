import pytest
from neuralswarm.core.context_manager import ContextManager


def test_add_message():
    cm = ContextManager(max_tokens=1000)
    cm.add_message("user", "hello")
    assert len(cm.messages) == 1
    assert cm.messages[0]["role"] == "user"
    assert cm.messages[0]["content"] == "hello"


def test_get_messages():
    cm = ContextManager()
    cm.add_message("user", "a")
    cm.add_message("assistant", "b")
    messages = cm.get_messages()
    assert len(messages) == 2


def test_update_tokens():
    cm = ContextManager()
    cm.update_tokens({"total_tokens": 100})
    assert cm.total_tokens == 100
    cm.update_tokens({"total_tokens": 50})
    assert cm.total_tokens == 150


def test_auto_compact_not_triggered():
    cm = ContextManager(max_tokens=1000)
    cm.add_message("user", "hello")
    cm.update_tokens({"total_tokens": 100})
    assert len(cm.messages) == 1


def test_compact():
    cm = ContextManager(max_tokens=100, compact_keep=3)
    for i in range(10):
        cm.add_message("user", f"message {i}")
    cm.update_tokens({"total_tokens": 200})
    assert cm.needs_compact()
    cm.compact("Summary of old messages")
    assert len(cm.messages) == 4  # 1 summary + 3 kept
    assert cm.messages[0]["role"] == "system"
    assert "Summary" in cm.messages[0]["content"]
    assert cm.total_tokens == 0
