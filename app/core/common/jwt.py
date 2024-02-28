from datetime import datetime, timedelta

import jwt

from api.users.model import User
from core.config.internal import auth_settings


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        auth_settings.AUTH_SECRET,
        algorithms=[auth_settings.AUTH_ALG]
    )


def create_access_token(
        user: User,
        expires_in: int = auth_settings.AUTH_ACCESS_TOKEN_EXPIRES_IN_SECONDS
) -> str:
    expire = datetime.utcnow() + timedelta(seconds=expires_in)
    data = {
        'user': user.user_id,
        'user_uuid': str(user.uuid),
        'exp': expire
    }

    encoded_jwt = jwt.encode(
        data,
        auth_settings.AUTH_SECRET,
        algorithm=auth_settings.AUTH_ALG
    )

    return encoded_jwt
