from contextlib import asynccontextmanager

from fastapi import FastAPI

from neuralswarm.api.health import router as health_router
from neuralswarm.api.projects import router as projects_router
from neuralswarm.api.tasks import router as tasks_router
from neuralswarm.api.ws import router as ws_router
from neuralswarm.api.ws_client import router as ws_client_router
from neuralswarm.config import settings
from neuralswarm.services.redis import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时连接 Redis，关闭时断开。"""
    await redis_client.connect()
    yield
    await redis_client.close()


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
    app.include_router(projects_router)
    app.include_router(tasks_router)
    app.include_router(ws_router)
    app.include_router(ws_client_router)

    return app


app = create_app()
