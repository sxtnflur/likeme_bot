from config import settings
from fastapi import FastAPI
from api.routers import __routers__
from starlette.middleware.cors import CORSMiddleware
from starlette.types import Lifespan


def create_app(prefix: str, lifespan: Lifespan | None = None) -> FastAPI:
    app = FastAPI(
        root_path=prefix,
        lifespan=lifespan
    )

    origins = [
        "http://localhost",
        "http://127.0.0.1",
        "http://127.0.0.1:80",
        "http://localhost:80",

        "https://bigling.ru"
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Set-Cookie",
            "Access-Control-Allow-Credentials",
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Methods",
        ]
    )

    for router in __routers__:
        app.include_router(router)
    return app
