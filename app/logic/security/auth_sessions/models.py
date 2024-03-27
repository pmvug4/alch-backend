import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from enum import Enum


class AuthSessionPlatformNames(str, Enum):
    mobile_android_app = 'mobile_android_app'
    mobile_ios_app = 'mobile_ios_app'
    web = 'web'


class AuthSessionPlatform(BaseModel):
    id: int
    name: AuthSessionPlatformNames

    @classmethod
    def get_by_name(
            cls,
            name: AuthSessionPlatformNames
    ) -> 'AuthSessionPlatform':
        if name == AuthSessionPlatformNames.mobile_android_app:
            return cls(id=1, name='mobile_android_app')
        elif name == AuthSessionPlatformNames.mobile_ios_app:
            return cls(id=2, name='mobile_ios_app')
        elif name == AuthSessionPlatformNames.web:
            return cls(id=10, name='web')
        else:
            raise TypeError


class AuthSessionForm(BaseModel):
    user_id: int
    platform: AuthSessionPlatformNames
    presign: bool


class AuthSession(AuthSessionForm):
    id: int
    uuid: UUID
    refresh_token: UUID
    fcm_token: Optional[str]
    created_at: datetime.datetime
    updated_at: Optional[datetime.datetime]
    revoked_at: Optional[datetime.datetime]
