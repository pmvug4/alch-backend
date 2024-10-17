from fastapi import Depends
from databases.core import Connection

from core.db import get_db
from logic.security.depends import GetCurrentUser, User

from .player import Player, PlayerStore
from .models import PlayerFull
from .store import PlayerFullStore


class GetCurrentPlayer:
    async def __call__(
            self,
            conn: Connection = Depends(get_db),
            user: User = Depends(GetCurrentUser(optional=False))
    ) -> Player:
        return await PlayerStore(conn).get(user_id=user.id)


class GetCurrentPlayerFull:
    async def __call__(
            self,
            conn: Connection = Depends(get_db),
            user: User = Depends(GetCurrentUser(optional=False))
    ) -> PlayerFull:
        return await PlayerFullStore(conn).get(user_id=user.id)
