from fastapi import Request, HTTPException, Depends, Response, Security
from fastapi.security import APIKeyCookie, HTTPBearer, HTTPAuthorizationCredentials
from jwt import DecodeError, ExpiredSignatureError
from starlette.status import HTTP_403_FORBIDDEN
from databases import Database
from loguru import logger

from api.users.model import User, AccessServer
from api.users.store import get_user, multibase_get_user

from core.common.groups_and_roles import GROUP_CUSTOMER, GROUP_COURIER, GROUP_COOPERATOR
from core.common.jwt import decode_token
from core.config.common import common_settings
from core.db import get_main_db, get_demo_db
from core.exception import IncorrectCredentials, AccessForbiden, AccessTokenExpired
from core.config.stripe import StripeServer

from .app_zones import DefaultAppZone

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
    elif common_settings.AUTH_BY_COOKIE:
        return cookie
    return None


def get_api_key(req: Request):
    """
      Авторизация запроса на основании API_KEY
      применять для запросов от своих сервисов и сервисов мониторинга.
    """

    try:
        api_key_header = req.headers["X-API_KEY"]
    except:
        pass
    else:
        if api_key_header == common_settings.API_KEY:
            return True
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )


async def get_current_user(
        req: Request,
        token: str | None = Depends(auth_scheme),
        main_db=Depends(get_main_db),
        demo_db=Depends(get_demo_db)
) -> User:
    try:
        token_data = decode_token(token)
    except ExpiredSignatureError:
        raise AccessTokenExpired
    except DecodeError:
        raise IncorrectCredentials

    if access_server := token_data.get('access_server'):
        if access_server == AccessServer.main:
            db = main_db
        elif access_server == AccessServer.demo:
            db = demo_db
        else:
            raise RuntimeError

        user = await get_user(
            db,
            pk=token_data['user'],
            uuid=token_data.get('user_uuid'),
            return_none=False,
            assert_not_deactivated=True
        )
        user.access_server = access_server

        return user
    else:
        return await multibase_get_user(
            main_db, demo_db,
            pk=token_data['user'],
            return_none=False,
            assert_not_deactivated=True
        )


async def get_current_user_optional(
        req: Request,
        token: str | None = Depends(auth_scheme),
        main_db=Depends(get_main_db),
        demo_db=Depends(get_demo_db)
) -> User | None:
    try:
        return await get_current_user(
            req, token=token,
            main_db=main_db,
            demo_db=demo_db
        )
    except (AccessForbiden, AccessTokenExpired, IncorrectCredentials):
        return


def apply_jwt_cookie(
        response: Response,
        token: str
):
    response.set_cookie(COOKIE_JWT_NAME, token)


def remove_jwt_cookie(
        response: Response,
):
    response.delete_cookie(COOKIE_JWT_NAME)


async def not_for_cooperator(
        user: User = Depends(get_current_user)
):
    if user.group_id == GROUP_COOPERATOR:
        raise AccessForbiden()


class GetCurrentDB:
    def __init__(
            self,
            user_is_optional: bool = False,
            default_access: AccessServer = None
    ):
        if user_is_optional and default_access is None:
            raise TypeError

        self._user_is_optional = user_is_optional
        self._default_access = default_access

    async def __call__(
            self,
            req: Request,
            token: str | None = Depends(auth_scheme),
            main_db=Depends(get_main_db),
            demo_db=Depends(get_demo_db)
    ) -> Database:
        logger.debug(f"Call GetCurrentDB({self._user_is_optional=}, {self._default_access=})")

        if self._user_is_optional:
            user = await get_current_user_optional(
                req=req,
                token=token,
                main_db=main_db,
                demo_db=demo_db
            )

            if user is None:
                logger.debug(f"Return default DB correlation with {self._default_access=}")
                if self._default_access == AccessServer.main:
                    return main_db
                elif self._default_access == AccessServer.demo:
                    return demo_db
                else:
                    raise RuntimeError
        else:
            user = await get_current_user(
                req=req,
                token=token,
                main_db=main_db,
                demo_db=demo_db
            )

        return user.get_access_db(main_db, demo_db)


class GetCurrentAppZone:
    def __init__(
            self,
            user_is_optional: bool = False,
            default_app_zone: DefaultAppZone = None
    ):
        if user_is_optional and default_app_zone is None:
            raise TypeError

        self._user_is_optional = user_is_optional
        self._default_app_zone = default_app_zone

    async def __call__(
            self,
            req: Request,
            token: str | None = Depends(auth_scheme),
            main_db=Depends(get_main_db),
            demo_db=Depends(get_demo_db)
    ) -> str:
        logger.debug(f"Call GetCurrentAppZone({self._user_is_optional=}, {self._default_app_zone=})")

        if self._user_is_optional:
            user = await get_current_user_optional(
                req=req,
                token=token,
                main_db=main_db,
                demo_db=demo_db
            )

            if user is None:
                logger.debug(f"Return default AppZone {self._default_app_zone}")
                return self._default_app_zone
        else:
            user = await get_current_user(
                req=req,
                token=token,
                main_db=main_db,
                demo_db=demo_db
            )

        logger.debug(f"Return current AppZone {user.app_zone}")
        return user.app_zone


get_main_app_zone = lambda: DefaultAppZone.main_la_zone


class GetCurrentStripeServer:
    def __init__(
            self,
            user_is_optional: bool = False,
            default_server: StripeServer = None
    ):
        if user_is_optional and default_server is None:
            raise TypeError

        self._user_is_optional = user_is_optional
        self._default_server = default_server

    async def __call__(
            self,
            req: Request,
            token: str | None = Depends(auth_scheme),
            main_db=Depends(get_main_db),
            demo_db=Depends(get_demo_db)
    ) -> StripeServer:
        if self._user_is_optional:
            user = await get_current_user_optional(
                req=req,
                token=token,
                main_db=main_db,
                demo_db=demo_db
            )

            if user is None:
                return self._default_server
        else:
            user = await get_current_user(
                req=req,
                token=token,
                main_db=main_db,
                demo_db=demo_db
            )

        return StripeServer.get_by_access_server(user.access_server)


class OnlyFor:
    def __init__(
            self, for_cooperator: bool = False,
            for_courier: bool = False,
            for_customer: bool = False,
            for_system: bool = False,
            for_testing: bool = False
    ):
        self._for_cooperator = for_cooperator
        self._for_courier = for_courier
        self._for_customer = for_customer
        self._for_system = for_system
        self._for_testing = for_testing

    async def __call__(
            self,
            req: Request,
            token: str | None = Depends(auth_scheme),
            main_db=Depends(get_main_db),
            demo_db=Depends(get_demo_db)
    ):
        if self._for_system and (token is not None and token == common_settings.API_KEY):
            return
        elif self._for_testing and (token is not None and token == common_settings.TESTING_KEY):
            return

        user = await get_current_user(
            req=req,
            token=token,
            main_db=main_db,
            demo_db=demo_db
        )

        if self._for_courier and user.group_id == GROUP_COURIER:
            return
        elif self._for_customer and user.group_id == GROUP_CUSTOMER:
            return
        elif self._for_cooperator and user.group_id == GROUP_COOPERATOR:
            return

        raise AccessForbiden
