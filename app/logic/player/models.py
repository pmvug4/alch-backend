from typing import Optional
from pydantic import Field

from logic.media import Media

from .player import Player
from .player_info import PlayerInfo
from .player_balance import PlayerBalance
from .player_subscription import PlayerSubscription


class PlayerInfoFull(PlayerInfo):
    avatar: Optional[Media] = Field(None, description="Развернутая информация об аватарке")

    @classmethod
    def from_player_info(
            cls,
            player_info: PlayerInfo,
            avatar: Optional[Media] = None
    ) -> 'PlayerInfoFull':
        return cls(
            **player_info.model_dump(),
            avatar=avatar
        )


class PlayerFull(Player):
    player_info: PlayerInfoFull = Field(..., description="Развернутая информация о профиле")
    player_balance: PlayerBalance = Field(..., description="Развернутая информация о балансе")
    player_subscription: PlayerSubscription = Field(..., description="Развернутая информация о подписке")

    @classmethod
    def from_player(
            cls,
            player: Player,
            player_info: PlayerInfoFull,
            player_balance: PlayerBalance,
            player_subscription: PlayerSubscription
    ) -> 'PlayerFull':
        return cls(
            **player.model_dump(),
            player_info=player_info,
            player_balance=player_balance,
            player_subscription=player_subscription
        )
