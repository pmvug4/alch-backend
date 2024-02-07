from fastapi import APIRouter, Depends, Response

from core.common.security import apply_jwt_cookie, AccessServer, get_main_app_zone
from core.config.common import common_settings
from core.db import get_main_db

from core.schemas import get_response_models, prepare_response_scheme

from api.auth.errors import NeedNewOTPPassword, IncorrectOTPPassword
from api.auth.schemas import AuthResponse
from api.auth.services import get_tokens
from api.users.errors import UserCreationError
from api.users.schemas import SelfCreateUser
from api.users.services import register_user
from api.users.store import get_user

router = APIRouter(tags=["users"])


_possible_exceptions = [NeedNewOTPPassword, IncorrectOTPPassword, UserCreationError]


@router.post(
    "",
    description="Регистрация пользователя",
    response_model=AuthResponse,
    responses=get_response_models("user_post",
                                  _possible_exceptions,
                                  with_422_error=True,
                                  resp200ok=prepare_response_scheme(AuthResponse))
)
async def create_user(
        response: Response,
        data: SelfCreateUser,
        db=Depends(get_main_db),
        app_zone: str = Depends(get_main_app_zone)
):
    user_id = await register_user(
        db, data.username,
        data.otp_password,
        data.role,
        app_zone=app_zone
    )

    user = await get_user(db, pk=user_id, return_none=False)
    user.access_server = AccessServer.main

    auth_resp = await get_tokens(db, user)

    if common_settings.AUTH_BY_COOKIE:
        apply_jwt_cookie(response, auth_resp.access_token)

    return auth_resp
