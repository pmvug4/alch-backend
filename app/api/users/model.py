from typing import Optional
from pydantic import BaseModel, constr
from uuid import UUID

from core.common.servers import AccessServer
from core.models import phone_regex, phone_type


class UserView(BaseModel):
    username: phone_type
    user_id: int
    group_id: int
    preferences_id: Optional[int]
    deactivated: bool
    uuid: UUID
    access_server: AccessServer = AccessServer.unknown
    app_zone: str

    def get_access_db(self, main_db, demo_db):
        if self.access_server == AccessServer.main:
            return main_db
        elif self.access_server == AccessServer.demo:
            return demo_db
        else:
            raise RuntimeError


class User(UserView):
    username: constr(regex=phone_regex) | constr(regex="DELETED_.+")
    password_hash: Optional[str]
    refresh_token: Optional[str]


class UserForm(BaseModel):
    username: phone_type
    group_id: int
    app_zone: Optional[str]
