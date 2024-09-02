from typing import Optional
from pydantic import Field

from logic.media import Media

from .player import Player
from .player_info import PlayerInfo
from .player_balance import PlayerBalance
from .player_subscription import PlayerSubscription


class PlayerInfoFull(PlayerInfo):
    avatar: Optional[Media] = Field(None, description="Развернутая информация об аватарке")


class PlayerFull(Player):
    player_info: PlayerInfoFull = Field(..., description="Развернутая информация о профиле")
    player_balance: PlayerBalance = Field(..., description="Развернутая информация о балансе")
    player_subscription: PlayerSubscription = Field(..., description="Развернутая информация о подписке")
