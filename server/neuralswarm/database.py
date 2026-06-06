from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from neuralswarm.config import settings


class Base(DeclarativeBase):
    pass


def get_engine(url: str | None = None):
    """创建异步数据库引擎"""
    database_url = url or settings.DATABASE_URL
    return create_async_engine(
        database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )


def get_session_factory(engine):
    """创建异步 session 工厂"""
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


# 默认引擎和 session 工厂（延迟初始化）
_engine = None
_session_factory = None


def get_db_engine():
    """获取全局数据库引擎"""
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine


def get_db_session_factory():
    """获取全局 session 工厂"""
    global _session_factory
    if _session_factory is None:
        _session_factory = get_session_factory(get_db_engine())
    return _session_factory


async def get_db() -> AsyncSession:
    """FastAPI 依赖：获取数据库 session"""
    factory = get_db_session_factory()
    async with factory() as session:
        yield session
