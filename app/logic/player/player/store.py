from asyncpg import UniqueViolationError

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
