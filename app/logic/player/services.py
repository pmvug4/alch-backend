from databases.core import Connection, Database
import random

from core.config.internal import player_settings

from .models import PlayerFull, PlayerInfoFull
from .player import (
    PlayerStore,
    PlayerForm,
    PlayerUniqueError
)
from .player_info import (
    PlayerInfoStore,
    PlayerInfoForm,
    PlayerInfoUniqueError
)
from .player_balance import (
    PlayerBalanceStore,
    PlayerBalanceForm,
    PlayerBalanceUniqueError
)
from .player_subscription import (
    PlayerSubscriptionStore,
    PlayerSubscriptionForm,
    PlayerSubscriptionUniqueError
)


class PlayerService:
    @staticmethod
    async def init_player(
            conn: Connection | Database,
            user_id: int
    ) -> PlayerFull:
        try:
            async with conn.transaction():
                player = await PlayerStore(conn).create(
                    form=PlayerForm(
                        user_id=user_id
                    )
                )

                player_info = await PlayerInfoStore(conn).create(
                    form=PlayerInfoForm(
                        nickname=f'Player{str(random.randint(1, 100000)).zfill(6)}',
                        player_id=player.id
                    )
                )

                player_balance = await PlayerBalanceStore(conn).create(
                    form=PlayerBalanceForm(
                        potions=player_settings.PLAYER_DEFAULT_POTIONS,
                        stones=player_settings.PLAYER_DEFAULT_STONES,
                        player_id=player.id
                    )
                )

                player_subscription = await PlayerSubscriptionStore(conn).create(
                    form=PlayerSubscriptionForm(
                        player_id=player.id
                    )
                )

                return PlayerFull.from_player(
                    player=player,
                    player_info=PlayerInfoFull.from_player_info(
                        player_info=player_info,
                        avatar=None
                    ),
                    player_balance=player_balance,
                    player_subscription=player_subscription
                )
        except (
                PlayerInfoUniqueError,
                PlayerBalanceUniqueError,
                PlayerSubscriptionUniqueError
        ) as e:
            raise PlayerUniqueError from e
