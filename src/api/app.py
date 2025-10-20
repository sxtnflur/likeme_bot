from config import settings
from fastapi import FastAPI
from api.routers import __routers__
from starlette.types import Lifespan


def create_app(prefix: str, lifespan: Lifespan) -> FastAPI:
    app = FastAPI(
        root_path=prefix,
        lifespan=lifespan
    )
    for router in __routers__:
        app.include_router(router)
    return app
