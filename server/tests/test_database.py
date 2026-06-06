import pytest
from neuralswarm.database import get_engine, get_session_factory


def test_get_engine():
    """测试创建数据库引擎"""
    engine = get_engine("sqlite+aiosqlite:///:memory:")
    assert engine is not None


def test_get_session_factory():
    """测试创建 session 工厂"""
    engine = get_engine("sqlite+aiosqlite:///:memory:")
    session_factory = get_session_factory(engine)
    assert session_factory is not None
