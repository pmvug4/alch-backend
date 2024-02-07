from datetime import datetime, timedelta

import jwt

from api.users.model import User
from core.config.common import common_settings


def decode_token(token: str):
    return jwt.decode(token,common_settings.AUTH_SECRET, algorithms=[common_settings.AUTH_ALG])


def create_access_token(
        user: User,
        expires_delta_seconds: int = common_settings.AUTH_ACCESS_TOKEN_EXPIRE_IN_SECONDS
):
    expire = datetime.utcnow() + timedelta(seconds=expires_delta_seconds)
    _data = {
        'user': user.user_id,
        'user_uuid': str(user.uuid),
        'access_server': user.access_server,
        'exp': expire
    }

    encoded_jwt = jwt.encode(_data, common_settings.AUTH_SECRET, algorithm=common_settings.AUTH_ALG)
    return encoded_jwt
