from fastapi import FastAPI

from neuralswarm.api.health import router as health_router
from neuralswarm.api.projects import router as projects_router
from neuralswarm.api.tasks import router as tasks_router
from neuralswarm.api.ws import router as ws_router
from neuralswarm.config import settings


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        debug=settings.DEBUG,
    )

    # 注册路由
    app.include_router(health_router)
    app.include_router(projects_router)
    app.include_router(tasks_router)
    app.include_router(ws_router)

    return app


app = create_app()
