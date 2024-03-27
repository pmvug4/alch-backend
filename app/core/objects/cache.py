import datetime
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
            data: BaseModel
    ) -> str:
        raise NotImplementedError

    async def _set(
            self,
            data: BaseModel,
            override_key: str = None,
            ex: Optional[int | datetime.timedelta] = None
    ) -> None:
        await self.redis.set(
            f'{self._prefix}__{override_key or self._fetch_key(data)}',
            value=data.json(),
            ex=ex
        )

    async def _get(
            self,
            key: str
    ) -> Optional[BaseModel]:
        try:
            return self._model.parse_raw(
                await self.redis.get(f'{self._prefix}__{key}')
            )
        except (ResponseError, ValidationError, ValueError):
            return None
