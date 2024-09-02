from asyncpg import UniqueViolationError

from core.objects.store import ObjectStore
from core.db.tables import DBTables

from .errors import PlayerBalanceUniqueError, PlayerBalanceNotFoundError
from .models import PlayerBalanceForm, PlayerBalance


class PlayerBalanceStore(ObjectStore[
        PlayerBalance,
        PlayerBalanceForm,
        None,
        None,
        PlayerBalanceNotFoundError,
    ]
):
    _table = DBTables.player_balance

    _model = PlayerBalance
    _model_create_form = PlayerBalanceForm
    _model_put_form = None
    _model_patch_form = None

    _not_found = PlayerBalanceNotFoundError

    async def create(
            self,
            form: PlayerBalanceForm
    ) -> PlayerBalance:
        try:
            return await super().create(form)
        except UniqueViolationError:
            raise PlayerBalanceUniqueError
