import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from neuralswarm.api.agents import router as agents_router
from neuralswarm.api.auth import router as auth_router
from neuralswarm.api.clients import router as clients_router
from neuralswarm.api.conflicts import router as conflicts_router
from neuralswarm.api.health import router as health_router
from neuralswarm.api.memory import router as memory_router
from neuralswarm.api.projects import router as projects_router
from neuralswarm.api.tasks import router as tasks_router
from neuralswarm.api.ws import router as ws_router
from neuralswarm.api.ws_client import router as ws_client_router
from neuralswarm.api.ws_conflicts import router as ws_conflicts_router
from neuralswarm.config import settings
from neuralswarm.services.redis import redis_client

logger = logging.getLogger(__name__)


def run_migrations():
    """运行 Alembic 数据库迁移（自动升级到最新版本）"""
    import os
    from pathlib import Path

    from alembic import command
    from alembic.config import Config

    # 获取 alembic.ini 路径
    server_dir = Path(__file__).parent.parent
    alembic_cfg_path = server_dir / "alembic.ini"

    if not alembic_cfg_path.exists():
        logger.warning("alembic.ini not found at %s, skipping migrations", alembic_cfg_path)
        return

    alembic_cfg = Config(str(alembic_cfg_path))

    # 设置数据库 URL
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

    # 切换到 server 目录（Alembic 需要相对路径）
    original_dir = os.getcwd()
    os.chdir(str(server_dir))

    try:
        logger.info("Running Alembic migrations (upgrade to head)...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations completed successfully")
    except Exception as e:
        logger.error("Migration failed: %s", e)
        raise
    finally:
        os.chdir(original_dir)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时运行迁移并连接 Redis，关闭时断开。"""
    # 运行数据库迁移
    run_migrations()

    # 连接 Redis
    await redis_client.connect()
    logger.info("Application started")

    yield

    # 关闭连接
    await redis_client.close()
    logger.info("Application stopped")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # 注册路由
    app.include_router(health_router)
    app.include_router(auth_router, prefix="/api")
    app.include_router(projects_router)
    app.include_router(tasks_router)
    app.include_router(agents_router)
    app.include_router(ws_router)
    app.include_router(ws_client_router)
    app.include_router(clients_router)
    app.include_router(conflicts_router)
    app.include_router(ws_conflicts_router)
    app.include_router(memory_router)

    return app


app = create_app()
