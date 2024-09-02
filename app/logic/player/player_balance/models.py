import datetime as dt
from pydantic import BaseModel, Field, conint
from typing import Optional


class PlayerBalanceBaseForm(BaseModel):
    potions: conint(lt=10**6) = Field(..., description="Кол-во зелий у игрока")
    stones: conint(lt=10**6) = Field(..., description="Кол-во философских камней у игрока")


class PlayerBalanceForm(PlayerBalanceBaseForm):
    player_id: int


class PlayerBalance(PlayerBalanceForm):
    id: int
    created_at: dt.datetime
    updated_at: Optional[dt.datetime]
