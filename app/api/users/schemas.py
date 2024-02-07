from pydantic import BaseModel, constr

from core.common.groups_and_roles import UserPublicGroups
from core.models import phone_regex


class SelfCreateUser(BaseModel):
    username: constr(regex=phone_regex)
    otp_password: str
    role: UserPublicGroups = UserPublicGroups.customer
