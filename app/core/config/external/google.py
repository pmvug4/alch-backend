from pydantic import BaseSettings, Field


class GoogleSettings(BaseSettings):
    APPLICATION_CREDENTIALS: str = Field(
        ...,
        env='GOOGLE_APPLICATION_CREDENTIALS',
        description="Path to google credentials file"
    )


google_settings = GoogleSettings()
