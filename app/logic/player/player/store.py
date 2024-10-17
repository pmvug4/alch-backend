from asyncpg import UniqueViolationError
from typing import Optional
from uuid import UUID

from core.objects.store import ObjectStore
from core.db.tables import DBTables, DBIndexes

from .errors import PlayerUniqueError, PlayerNotFoundError
from .models import PlayerForm, Player


class PlayerStore(ObjectStore[
        Player,
        PlayerForm,
        None,
        None,
        PlayerNotFoundError,
    ]
):
    _table = DBTables.player

    _model = Player
    _model_create_form = PlayerForm
    _model_put_form = None
    _model_patch_form = None

    _not_found = PlayerNotFoundError

    async def create(
            self,
            form: PlayerForm
    ) -> Player:
        try:
            return await super().create(form)
        except UniqueViolationError as e:
            if DBIndexes.ui_player in str(e):
                raise PlayerUniqueError

    async def get(
            self,
            pk: int = None,
            uuid: UUID = None,
            user_id: int = None,
            for_update: bool = False,
            return_none: bool = False,
            return_deleted: bool = False,
    ) -> Optional[Player]:
        if pk is not None:
            v = {
                'pk_field': 'id',
                'pk_value': pk
            }
        elif uuid is not None:
            v = {
                'pk_field': 'id',
                'pk_value': uuid
            }
        elif user_id is not None:
            v = {
                'pk_field': 'user_id',
                'pk_value': user_id
            }
        else:
            raise TypeError

        return await super().get(
            **v,
            for_update=for_update,
            return_none=return_none,
            return_deleted=return_deleted
        )
