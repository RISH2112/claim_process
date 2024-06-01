from fastapi import FastAPI

from app.events import lifespan
from app.routes import claims


def get_application() -> FastAPI:
    app = FastAPI(
        docs_url="/docs",
        redoc_url="/redocs",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.include_router(claims, tags=["claims"])

    return app


app = get_application()
