import datetime as dt
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class PlayerForm(BaseModel):
    user_id: int


class Player(PlayerForm):
    id: int
    uuid: UUID
    created_at: dt.datetime
    deleted_at: Optional[dt.datetime]
