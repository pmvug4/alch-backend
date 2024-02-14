from socket import AF_INET
from typing import Optional

import aiohttp

from core.config.external.telegram import telegram_settings


class SingletonAiohttpTelegram:
    aiohttp_client: Optional[aiohttp.ClientSession] = None

    @classmethod
    def _is_alive(cls) -> bool:
        return not cls.aiohttp_client.closed

    @classmethod
    def get_aiohttp_client(cls) -> aiohttp.ClientSession:
        if cls.aiohttp_client is None or not cls._is_alive():
            timeout = aiohttp.ClientTimeout(total=7)
            connector = aiohttp.TCPConnector(
                family=AF_INET,
                limit_per_host=telegram_settings.SIZE_POOL_AIOHTTP
            )
            cls.aiohttp_client = aiohttp.ClientSession(timeout=timeout, connector=connector)

        return cls.aiohttp_client

    @classmethod
    async def close_aiohttp_client(cls) -> None:
        if cls.aiohttp_client:
            await cls.aiohttp_client.close()
            cls.aiohttp_client = None
