from pydantic import BaseModel


class Preferences(BaseModel):
    id: int
    news_enabled: bool
    push_enabled: bool
    sms_enabled: bool
