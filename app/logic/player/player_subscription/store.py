from asyncpg import UniqueViolationError

from core.objects.store import ObjectStore
from core.db.tables import DBTables

from .errors import PlayerSubscriptionUniqueError, PlayerSubscriptionNotFoundError
from .models import PlayerSubscription, PlayerSubscriptionForm


class PlayerSubscriptionStore(ObjectStore[
        PlayerSubscription,
        PlayerSubscriptionForm,
        None,
        None,
        PlayerSubscriptionNotFoundError,
    ]
):
    _table = DBTables.player_subscription

    _model = PlayerSubscription
    _model_create_form = PlayerSubscriptionForm
    _model_put_form = None
    _model_patch_form = None

    _not_found = PlayerSubscriptionNotFoundError

    async def create(
            self,
            form: PlayerSubscriptionForm
    ) -> PlayerSubscription:
        try:
            return await super().create(form)
        except UniqueViolationError:
            raise PlayerSubscriptionUniqueError
