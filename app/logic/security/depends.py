from typing import Optional

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security, Depends

from databases.core import Connection
from aioredis import Redis

from core.db import get_db
from core.cache import get_redis
from core.config.internal import service_settings
from core.exceptions.exception import AccessForbidden, IncorrectCredentials

from .session_data import SessionData
from .users import User, UserStore
from .service import SecurityService
from .groups import PlayerGroup


BEARER_JWT_KEY = HTTPBearer(scheme_name="JWT", auto_error=False)


def get_access_token(
        bearer: HTTPAuthorizationCredentials | None = Security(BEARER_JWT_KEY),
) -> str | None:
    if bearer is not None:
        return bearer.credentials
    else:
        return None


class PermissionController:
    def __init__(
            self,
            for_free: bool = False,
            for_system: bool = False,
            for_player: bool = False,
            allow_presign: bool = True
    ):
        self._for_free = for_free
        self._for_system = for_system
        self._for_player = for_player
        self._allow_presign = allow_presign

    async def __call__(
            self,
            access_token: str | None = Depends(get_access_token),
            db_conn: Connection = Depends(get_db),
            redis: Redis = Depends(get_redis)
    ) -> None:
        if access_token is None and self._for_free:
            return
        elif service_settings.API_KEY and self._for_system and access_token == service_settings.API_KEY:
            return
        else:
            session_data = await SecurityService.get_session_data(
                conn=db_conn,
                redis=redis,
                access_token=access_token
            )

            if not self._allow_presign and session_data.presign:
                raise AccessForbidden

            if self._for_player and session_data.user_group_id == PlayerGroup.id:
                return

        raise AccessForbidden


class GetSessionData:
    def __init__(
            self,
            optional: bool = False
    ):
        self._optional = optional

    async def __call__(
            self,
            access_token: str | None = Depends(get_access_token),
            db_conn: Connection = Depends(get_db),
            redis: Redis = Depends(get_redis)
    ) -> Optional[SessionData]:
        if access_token is None:
            if self._optional:
                return
            else:
                raise IncorrectCredentials

        return await SecurityService.get_session_data(
            conn=db_conn,
            redis=redis,
            access_token=access_token
        )


class GetCurrentUser:
    def __init__(
            self,
            optional: bool = False
    ):
        self._optional = optional

    async def __call__(
            self,
            access_token: str | None = Depends(get_access_token),
            db_conn: Connection = Depends(get_db),
            redis: Redis = Depends(get_redis)
    ) -> Optional[User]:
        session_data = await GetSessionData(optional=self._optional)(
            access_token=access_token,
            db_conn=db_conn,
            redis=redis
        )

        if session_data is None:
            return
        else:
            return await UserStore(db_conn).get(pk=session_data.user_id)
