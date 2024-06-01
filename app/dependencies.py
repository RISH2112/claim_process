import datetime
from collections import deque
from http import HTTPStatus
from fastapi import HTTPException

from fastapi.requests import Request
from functools import wraps

import aioredis
import logging

from pottery import Redlock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlalchemy import URL

from app.constants import REDIS_KEY_RATE_LIMITER, REQUEST_LIMIT, RATE_LIMITER_TIME_GAP
from app.settings import REDIS_HOST, REDIS_PORT, DB_HOST, DB_PASSWORD, DB_NAME, DB_PORT, DB_USER

logger = logging.getLogger(__name__)


async def init_redis() -> aioredis.Redis:
    r = await aioredis.from_url(f'redis://{REDIS_HOST}:{REDIS_PORT}')
    logger.debug("Redis connected")
    return r


async def init_model() -> sessionmaker:
    DATABASE_URL = URL.create(
        host=DB_HOST,
        port=DB_PORT,
        username=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        drivername="postgresql+asyncpg",
    )
    engine = create_async_engine(DATABASE_URL, echo=True, future=True)
    print(DATABASE_URL)
    session = async_sessionmaker(bind=engine, class_=AsyncSession)
    # Create the database tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    print("Read Replica >>> DB Engine Created...")
    print(f"Read Replica  >>> Pool Status >>> {engine.pool.status()}")
    return engine, session


def rate_limiter(func):
    @wraps(func)
    async def wrapper(*args, request: Request, **kwargs):
        rl_queue = []
        request_time = datetime.datetime.now()
        rl_lock = Redlock(key="rate_limiter", masters={
            request.app.redis})  # take redis lock on above key to handle request coming concurrently and on parallel servers
        with rl_lock:
            rate_limiter_data = await get_rate_limiter_redis(request)

            if rate_limiter_data:

                rl_queue = deque(rate_limiter_data.decode("utf-8").split(","))
                # pop all timestamp which are not in time range

                while rl_queue and datetime.datetime.fromtimestamp(float(rl_queue[0])) < request_time - datetime.timedelta(
                        seconds=RATE_LIMITER_TIME_GAP):
                    rl_queue.popleft()

                if len(rl_queue) >= REQUEST_LIMIT:
                    raise HTTPException(status_code=HTTPStatus.TOO_MANY_REQUESTS)

                else:
                    request_time = str(datetime.datetime.timestamp(request_time))
                    rl_queue.append(request_time)
                    await request.app.redis.set(REDIS_KEY_RATE_LIMITER, ",".join(rl_queue))

            else:
                request_time = str(datetime.datetime.timestamp(request_time))
                rl_queue.append(request_time)
                await request.app.redis.set(REDIS_KEY_RATE_LIMITER, ",".join(rl_queue))

        return await func(*args, request=request, **kwargs)

    return wrapper


async def get_rate_limiter_redis(request: Request):
    prefix = REDIS_KEY_RATE_LIMITER
    print(await request.app.redis.get(prefix))
    return await request.app.redis.get(prefix)
