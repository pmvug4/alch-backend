import datetime
from redis.asyncio import Redis, ResponseError
from typing import Type, Optional

from pydantic import BaseModel, ValidationError


class ObjectCache[
    Model: BaseModel
]:
    _model: Type[Model]
    _prefix: str

    def __init__(self, redis: Redis):
        self.redis = redis

    def _fetch_key(
            self,
            data: Model
    ) -> str:
        raise NotImplementedError

    async def set(
            self,
            data: Model,
            ex: Optional[int | datetime.timedelta] = None
    ) -> None:
        return await self._set(
            data=data,
            override_key=None,
            ex=ex
        )

    async def _set(
            self,
            data: Model,
            override_key: str = None,
            ex: Optional[int | datetime.timedelta] = None
    ) -> None:
        await self.redis.set(
            f'{self._prefix}__{override_key or self._fetch_key(data)}',
            value=data.model_dump_json(),
            ex=ex
        )

    async def _get(
            self,
            key: str
    ) -> Optional[Model]:
        try:
            return self._model.model_validate_json(
                await self.redis.get(f'{self._prefix}__{key}')
            )
        except (ResponseError, ValidationError, ValueError):
            return None
