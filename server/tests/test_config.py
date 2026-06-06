import pytest
from neuralswarm.config import Settings


def test_settings_defaults():
    """测试默认配置值"""
    settings = Settings()
    assert settings.APP_NAME == "neuralswarm"
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 8000
    assert settings.DEBUG is False


def test_settings_from_env(monkeypatch):
    """测试从环境变量加载配置"""
    monkeypatch.setenv("NS_APP_NAME", "test-app")
    monkeypatch.setenv("NS_PORT", "9000")
    monkeypatch.setenv("NS_DEBUG", "true")

    settings = Settings()
    assert settings.APP_NAME == "test-app"
    assert settings.PORT == 9000
    assert settings.DEBUG is True


def test_database_url_default():
    """测试默认数据库 URL"""
    settings = Settings()
    assert "postgresql+asyncpg://" in settings.DATABASE_URL


def test_redis_url_default():
    """测试默认 Redis URL"""
    settings = Settings()
    assert settings.REDIS_URL.startswith("redis://")
