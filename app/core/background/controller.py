import asyncio
from typing import Coroutine

from core.common.singleton import SingletonMeta


class BackgroundTasks(metaclass=SingletonMeta):
    @staticmethod
    async def create(coro: Coroutine) -> None:
        # async func for the future
        asyncio.create_task(coro)  # noqa
