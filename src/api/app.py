from config import settings
from fastapi import FastAPI
from api.routers import __routers__


def create_app(_=None) -> FastAPI:
    app = FastAPI(
        root_path=settings.API_PREFIX
    )
    for router in __routers__:
        app.include_router(router)
    return app