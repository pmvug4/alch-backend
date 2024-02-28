from fastapi import Request, Depends
from databases.core import Database, Connection

from api.users.model import User
from api.users.store import get_user

from core.common.groups_and_roles import GROUP_ADMIN, GROUP_PLAYER
from core.config.internal import service_settings
from core.db import get_db
from core.exception import AccessForbidden

from .tokens import get_token_data, get_raw_token


async def get_current_user(
        token_data: dict = Depends(get_token_data),
        db_conn: Database | Connection = Depends(get_db)
) -> User:
    return await get_user(
        db_conn,
        pk=token_data['user'],
        uuid=token_data.get('user_uuid'),
        return_none=False,
        assert_not_deactivated=True
    )


class OnlyFor:
    def __init__(
            self,
            for_admin: bool = False,
            for_player: bool = False,
            for_system: bool = False,
            for_testing: bool = False
    ):
        self._for_admin = for_admin
        self._for_player = for_player
        self._for_system = for_system
        self._for_testing = for_testing

    async def __call__(
            self,
            req: Request,
            token: str | None = Depends(get_raw_token),
            db_conn: Database | Connection = Depends(get_db)
    ):
        if self._for_system and (token is not None and token == service_settings.API_KEY):
            return
        elif self._for_testing and (token is not None and token == service_settings.TESTING_KEY):
            return
        else:
            user = await get_current_user(
                token_data=await get_token_data(token),
                db_conn=db_conn
            )

            if self._for_player and user.group_id == GROUP_PLAYER:
                return
            elif self._for_admin and user.group_id == GROUP_ADMIN:
                return

        raise AccessForbidden
