from typing import Callable

from core.db import DBConnPool
from core.cache.redis import Redis


def create_start_app_handler(
) -> Callable:
    async def startup():
        await DBConnPool().init_db()
        await Redis().init_redis()

    return startup


def create_stop_app_handler(
) -> Callable:
    async def shutdown():
        await DBConnPool().close_db()
        await Redis().shutdown_redis()

    return shutdown
