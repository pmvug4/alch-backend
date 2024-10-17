from pydantic import BaseModel
from uuid import UUID
from typing import Optional

from ..auth_sessions.models import AuthSessionPlatformNames


class SessionData(BaseModel):
    session_id: int
    session_uuid: UUID

    presign: bool

    user_id: int
    user_uuid: UUID
    user_group_id: int

    platform: AuthSessionPlatformNames

    player_id: Optional[int]
    player_uuid: Optional[UUID]
