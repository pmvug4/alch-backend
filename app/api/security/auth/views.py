from uuid import UUID

from fastapi import Depends, APIRouter
from databases.core import Connection

from core.schemas import get_response_models, prepare_response_scheme
from core.db import get_db

from logic.security.service import SecurityService
from logic.security.models import AuthResponse, EmailVerificationResponse
from logic.security.auth_sessions import AuthSessionPlatformNames
from logic.security.depends import GetSessionData, SessionData

from .schemas import (
    LoginRequest,
    StartEmailVerificationRequest,
    CompleteEmailVerificationRequest,
    RegisterAccountRequest
)

router = APIRouter()


@router.get(
    "/token/presign/",
    description="Get presign token",
    response_model=AuthResponse,
    responses=get_response_models(
        "get_presign_token",
        [],
        with_422_error=False,
        resp200ok=prepare_response_scheme(AuthResponse)
    )
)
async def get_presign_token(
        platform: AuthSessionPlatformNames,
        db_conn: Connection = Depends(get_db)
) -> AuthResponse:
    return await SecurityService.create_presign_user(
        conn=db_conn,
        platform=platform
    )


@router.post(
    "/token/refresh/",
    description="Refresh token",
    response_model=AuthResponse,
    responses=get_response_models(
        "refresh_token",
        [],
        with_422_error=False,
        resp200ok=prepare_response_scheme(AuthResponse)
    )
)
async def refresh_token(
        session_uuid: UUID,
        refresh_token: UUID,
        db_conn: Connection = Depends(get_db)
) -> AuthResponse:
    return await SecurityService.refresh_token(
        conn=db_conn,
        refresh_token=refresh_token,
        session_uuid=session_uuid
    )


@router.post(
    "/login/",
    description="Login by password",
    response_model=AuthResponse,
    responses=get_response_models(
        "login_by_password",
        [],
        with_422_error=False,
        resp200ok=prepare_response_scheme(AuthResponse)
    )
)
async def login_by_password(
        request: LoginRequest,
        db_conn: Connection = Depends(get_db)
) -> AuthResponse:
    return await SecurityService.login_by_password(
        db_conn,
        platform=request.platform,
        email=request.email,
        password=request.platform,
        group_id=request.group_id
    )


@router.post(
    "/verification/email/start/",
    description="Start email verification",
    response_model=EmailVerificationResponse,
    responses=get_response_models(
        "start_email_verification",
        [],
        with_422_error=False,
        resp200ok=prepare_response_scheme(EmailVerificationResponse)
    )
)
async def start_email_verification(
        request: StartEmailVerificationRequest,
        db_conn: Connection = Depends(get_db)
) -> EmailVerificationResponse:
    return await SecurityService.start_email_verification(
        db_conn,
        email=request.email,
    )


@router.post(
    "/verification/email/complete/",
    description="Complete email verification",
    response_model=EmailVerificationResponse,
    responses=get_response_models(
        "complete_email_verification",
        [],
        with_422_error=False,
        resp200ok=prepare_response_scheme(EmailVerificationResponse)
    )
)
async def complete_email_verification(
        request: CompleteEmailVerificationRequest,
        db_conn: Connection = Depends(get_db)
) -> EmailVerificationResponse:
    return await SecurityService.complete_email_verification(
        db_conn,
        key=request.key,
        code=request.code
    )


@router.post(
    "/register/",
    description="Register account",
    response_model=AuthResponse,
    responses=get_response_models(
        "register_account",
        [],
        with_422_error=False,
        resp200ok=prepare_response_scheme(AuthResponse)
    )
)
async def register_account(
        request: RegisterAccountRequest,
        session_data: SessionData = Depends(GetSessionData()),
        db_conn: Connection = Depends(get_db)
) -> AuthResponse:
    return await SecurityService.register_account(
        db_conn,
        session_data=session_data,
        password=request.password,
        email_verification_key=request.email_verification_key
    )


# todo logout, инвалидация
