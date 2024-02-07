from typing import Callable

from core.cache.redis import init_redis_conn, close_redis_conn
from core.db import DBConnPool, DBDemoConnPool


def create_start_app_handler(
) -> Callable:
    async def startup():
        await DBConnPool().init_db()
        await DBDemoConnPool().init_db()
        await init_redis_conn()
    return startup


def create_stop_app_handler(
) -> Callable:
    async def shutdown():
        await DBConnPool().close_db()
        await DBDemoConnPool().close_db()
        await close_redis_conn()
    return shutdown
