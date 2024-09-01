from typing import Optional
from pydantic import Field

from logic.media import Media

from .player import Player
from .player_info import PlayerInfo


class PlayerInfoFull(PlayerInfo):
    avatar: Optional[Media] = Field(None, description="Развернутая информация об аватарке")


class PlayerFull(Player):
    player_info: PlayerInfoFull = Field(..., description="Развернутая информация о профиле игрока")
