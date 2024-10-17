from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from typing import Optional


class PlayerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    PLAYER_DEFAULT_POTIONS: int = Field(
        1000,
        description="Стандартное кол-во зелий у игрока (в начале сезона и при регистрации)",
        validation_alias='PLAYER_DEFAULT_POTIONS'
    )
    PLAYER_DEFAULT_STONES: int = Field(
        25,
        description="Стандартное кол-во философский камней у игрока",
        validation_alias='PLAYER_DEFAULT_STONES'
    )

player_settings = PlayerSettings()
