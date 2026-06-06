from fastapi import FastAPI

from neuralswarm.api.health import router as health_router
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

    return app


app = create_app()
