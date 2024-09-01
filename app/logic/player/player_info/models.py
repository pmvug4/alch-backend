import datetime as dt
from pydantic import BaseModel, constr, Field
from uuid import UUID
from typing import Optional


class PlayerInfoBaseForm(BaseModel):
    nickname: constr(max_length=63) = Field(..., description="Никнейм игрока")
    avatar_uuid: Optional[UUID] = Field(None, description="Media UUID аватара")


class PlayerInfoForm(PlayerInfoBaseForm):
    player_id: int


class PlayerInfoPutForm(PlayerInfoBaseForm):
    pass


class PlayerInfo(PlayerInfoForm):
    id: int
    created_at: dt.datetime
    updated_at: Optional[dt.datetime]
