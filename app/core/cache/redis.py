import aioredis
from loguru import logger
from typing import Optional
from contextlib import contextmanager

from core.common.singleton import SingletonMeta

from core.config.external import redis_settings


class Redis(metaclass=SingletonMeta):
    _redis_settings = redis_settings
    _redis: Optional[aioredis.Redis] = None

    async def init_redis(self):
        try:
            logger.info("Try to connect to the redis...")

            self._redis = await aioredis.from_url(
                url=f"redis://{redis_settings.HOST}:{redis_settings.PORT}",
                password=redis_settings.PASSWORD.get_secret_value()
            )

            await self._redis.ping()
        except aioredis.RedisError:
            logger.error("Failed to establish a redis connection.")
            raise
        else:
            logger.info("Redis was connected successfully.")

    async def shutdown_redis(self):
        if self._redis is None:
            logger.debug("No redis connection for shutdown.")
        else:
            try:
                logger.info("Try to gracefully redis shutdown.")
                await self._redis.close()
            except aioredis.RedisError:
                logger.error("Failed to redis shutdown.")
            finally:
                self._redis = None

    @contextmanager
    def get_connection(self) -> aioredis.Redis:
        if self._redis is None:
            raise RuntimeError("Redis is not configured.")

        yield self._redis


def get_redis() -> aioredis.Redis:
    with Redis().get_connection() as conn:  # noqa
        yield conn
