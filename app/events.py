from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db_utils import DatabaseOperations
from app.dependencies import init_model, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.redis = await init_redis()
    app.engine, app.session = await init_model()
    app.db_helper = DatabaseOperations(db_helper=app.session)
    yield
    await app.redis.close()
    await app.engine.dispose()
