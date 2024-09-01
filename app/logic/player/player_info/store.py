from asyncpg import UniqueViolationError

from core.objects.store import ObjectStore
from core.db.tables import DBTables

from .errors import PlayerInfoUniqueError, PlayerInfoNotFoundError
from .models import PlayerInfoForm, PlayerInfo, PlayerInfoPutForm


class PlayerInfoStore(ObjectStore[
        PlayerInfo,
        PlayerInfoForm,
        PlayerInfoPutForm,
        None,
        PlayerInfoNotFoundError,
    ]
):
    _table = DBTables.player_info

    _model = PlayerInfo
    _model_create_form = PlayerInfoForm
    _model_put_form = PlayerInfoPutForm
    _model_patch_form = None

    _not_found = PlayerInfoNotFoundError

    async def create(
            self,
            form: PlayerInfoForm
    ) -> PlayerInfo:
        try:
            return await super().create(form)
        except UniqueViolationError:
            raise PlayerInfoUniqueError
