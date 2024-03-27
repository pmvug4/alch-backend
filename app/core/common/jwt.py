from datetime import datetime, timedelta

import jwt

from core.config.internal import auth_settings
from core.exceptions.exception import AccessTokenExpired, IncorrectCredentials


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            auth_settings.AUTH_SECRET,
            algorithms=[auth_settings.AUTH_ALG]
        )
    except jwt.ExpiredSignatureError:
        raise AccessTokenExpired
    except jwt.DecodeError:
        raise IncorrectCredentials


def create_token(
        data: dict,
        expires_in: int = auth_settings.AUTH_ACCESS_TOKEN_EXPIRES_IN_SECONDS
) -> str:
    expire = datetime.utcnow() + timedelta(seconds=expires_in)

    encoded_jwt = jwt.encode(
        data | {'exp': expire},
        auth_settings.AUTH_SECRET,
        algorithm=auth_settings.AUTH_ALG
    )

    return encoded_jwt
