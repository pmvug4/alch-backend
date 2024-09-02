from asyncpg import Record
from typing import Optional, Type
from uuid import UUID

from core.db.tools import FetchRelated
from core.objects.store import ObjectFullStore, PaginatedObjects, PaginationRequest
from core.db.tables import DBTables
from core.db import tools as db_tools

from .player.errors import PlayerNotFoundError
from .models import PlayerFull


class PlayerFullStore(
    ObjectFullStore[
        PlayerFull,
        PlayerNotFoundError
    ]
):
    _table: str = DBTables.player
    _returning: str = '*'
    _fetch_related: list[db_tools.FetchRelated] = [
        FetchRelated(
            table=DBTables.player_info,
            join_on=f'{DBTables.player_info}.player_id',
            join_to=f'{_table}.id',
            inner_join=True,
            returning_as='player_info'
        ),
        FetchRelated(
            table=DBTables.media,
            join_on=f'{DBTables.player_info}.avatar_uuid',
            join_to=f'{DBTables.media}.uuid',
            inner_join=False,
            returning_as='player_info_avatar'
        ),
        FetchRelated(
            table=DBTables.player_balance,
            join_on=f'{DBTables.player_balance}.player_id',
            join_to=f'{_table}.id',
            inner_join=True,
            returning_as='player_balance'
        ),
        FetchRelated(
            table=DBTables.player_subscription,
            join_on=f'{DBTables.player_subscription}.player_id',
            join_to=f'{_table}.id',
            inner_join=True,
            returning_as='player_subscription'
        )
    ]

    _model = PlayerFull
    _not_found = PlayerNotFoundError

    @classmethod
    def _record_to_model(
            cls,
            record: Record
    ) -> PlayerFull:
        data: dict = db_tools.get_data(record)
        data['player_info']['avatar'] = data['player_info_avatar']

        return cls._model.model_validate(data)

    async def get(
            self,
            user_id: Optional[int] = None,
            player_id: Optional[int] = None,
            player_uuid: Optional[UUID] = None,
            return_deleted: bool = False,
            return_none: bool = False
    ) -> Optional[PlayerFull]:
        if player_id is not None:
            v = {
                'pk_field': f'{self._table}.id',
                'pk_value': player_id
            }
        elif player_uuid is not None:
            v = {
                'pk_field': f'{self._table}.uuid',
                'pk_value': player_uuid
            }
        elif user_id is not None:
            v = {
                'pk_field': f'{self._table}.user_id',
                'pk_value': user_id
            }
        else:
            raise TypeError

        return await self._get(
            **v,
            return_deleted=return_deleted,
            return_none=return_none
        )

    async def get_list(
            self,
            return_deleted: bool = False,
            pagination: Optional[PaginationRequest] = None
    ) -> PaginatedObjects[Type[PlayerFull]]:
        return await self._get_list(
            return_deleted=return_deleted,
            pagination=pagination
        )
