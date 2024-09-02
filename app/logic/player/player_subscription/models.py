import datetime as dt
from pydantic import BaseModel, Field
from typing import Optional


class PlayerSubscriptionBaseForm(BaseModel):
    is_vip: bool = Field(False, description="Является ли игрок VIP ?")
    vip_until: Optional[dt.datetime] = Field(None, description="Время, до которого действует VIP")


class PlayerSubscriptionForm(PlayerSubscriptionBaseForm):
    player_id: int


class PlayerSubscription(PlayerSubscriptionForm):
    id: int
    created_at: dt.datetime
    updated_at: Optional[dt.datetime]
