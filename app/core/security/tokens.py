from fastapi import Depends, Security, Response
from fastapi.security import APIKeyCookie, HTTPBearer, HTTPAuthorizationCredentials
from jwt import DecodeError, ExpiredSignatureError
from core.common.jwt import decode_token
from core.exception import IncorrectCredentials, AccessTokenExpired
from core.config.internal import auth_settings


COOKIE_JWT_NAME = "X-JWT-AUTH"
COOKIE_JWT_KEY = APIKeyCookie(name=COOKIE_JWT_NAME, scheme_name="JWT", auto_error=False)

BEARER_JWT_KEY = HTTPBearer(scheme_name="JWT", auto_error=False)


def auth_scheme(
        cookie: str | None = Security(COOKIE_JWT_KEY),
        bearer: HTTPAuthorizationCredentials | None = Security(BEARER_JWT_KEY),
) -> str | None:
    """
        Returns JWT from "Authorization" header or cookie.
        Auth methods have the same scheme_name on purpose, only the last arg of this function is shown in Swagger UI.
    """
    if bearer is not None:
        return bearer.credentials
    elif auth_settings.AUTH_BY_COOKIE:
        return cookie
    else:
        return None


async def get_raw_token(
        token: str | None = Depends(auth_scheme),
) -> str | None:
    return token


async def get_token_data(
        token: str | None = Depends(auth_scheme),
) -> dict:
    try:
        return decode_token(token)
    except ExpiredSignatureError:
        raise AccessTokenExpired
    except DecodeError:
        raise IncorrectCredentials


def apply_jwt_cookie(
        response: Response,
        token: str
):
    response.set_cookie(COOKIE_JWT_NAME, token)


def remove_jwt_cookie(
        response: Response,
):
    response.delete_cookie(COOKIE_JWT_NAME)
