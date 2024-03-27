from aioredis import Redis, ResponseError
from typing import Type, Optional

from pydantic import BaseModel, ValidationError


class ObjectCache:
    _model: Type[BaseModel]
    _prefix: str

    def __init__(self, redis: Redis):
        self.redis = redis

    def _fetch_key(
            self,
            data: '_model'
    ) -> str:
        raise NotImplementedError

    async def _set(
            self,
            data: '_model',
            override_key: str = None
    ) -> None:
        await self.redis.hset(
            f'{self._prefix}__{override_key or self._fetch_key(data)}',
            mapping=data.dict()
        )

    async def _get(
            self,
            key: str
    ) -> Optional['_model']:
        try:
            return self._model.parse_obj(
                await self.redis.hgetall(f'{self._prefix}__{key}')
            )
        except (ResponseError, ValidationError, ValueError):
            return None
