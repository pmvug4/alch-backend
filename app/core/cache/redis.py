import aioredis

from core.config.redis import redis_settings
from loguru import logger
redis = None


async def init_redis_conn():
    global redis
    if not redis_settings.HOST:
        logger.info("Caching is disabled all data will be load from db")
    else:
        logger.info("Try to connect redis....")
    redis = await aioredis.from_url(
        url=f"redis://{redis_settings.HOST}:{redis_settings.PORT}",
        password=redis_settings.PASSWORD.get_secret_value()
    )
    try:
        await redis.ping()
    except Exception as e:
        logger.error(f"Exception while test connection to redis: {repr(e)}")
    else:
        logger.info(f"Redis is availiable")


async def close_redis_conn():
    if redis:
        await redis.close()
