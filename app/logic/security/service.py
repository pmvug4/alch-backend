from uuid import UUID
from databases.core import Connection, Database
from redis.asyncio import Redis
from pydantic import EmailStr
from hashlib import md5

from core.common import jwt
from core.config.internal import auth_settings

from .groups import PlayerGroup
from .users import UserStore, PresignUserForm, User, UserAlreadyExists
from .auth_sessions import AuthSessionStore, AuthSessionForm, AuthSessionPlatformNames, AuthSession, AuthSessionService
from .models import AuthResponse, EmailVerificationResponse
from .session_data import SessionData, SessionDataCache
from .verifications import EmailVerificationService


class SecurityService:
    @staticmethod
    async def create_presign_user(
            conn: Connection | Database,
            platform: AuthSessionPlatformNames
    ) -> AuthResponse:
        async with conn.transaction():
            user = await UserStore(conn).create(
                PresignUserForm(group_id=PlayerGroup.id)
            )

            auth_session = await AuthSessionStore(conn).create(
                AuthSessionForm(
                    user_id=user.id,
                    platform=platform,
                    presign=True
                )
            )

            return AuthResponse(
                access_token=SecurityService._generate_access_token(auth_session.uuid),
                refresh_token=auth_session.refresh_token,
                session_uuid=auth_session.uuid
            )

    @staticmethod
    async def login_by_password(
            conn: Connection | Database,
            platform: AuthSessionPlatformNames,
            email: EmailStr,
            password: str,
            group_id: int
    ) -> AuthResponse:
        password_hash = SecurityService._get_password_hash(password)

        user = await UserStore(conn).get_for_login(
            email=email,
            password_hash=password_hash,
            group_id=group_id
        )

        auth_session = await AuthSessionStore(conn).create(
            AuthSessionForm(
                user_id=user.id,
                platform=platform,
                presign=False
            )
        )

        return AuthResponse(
            access_token=SecurityService._generate_access_token(auth_session.uuid),
            refresh_token=auth_session.refresh_token,
            session_uuid=auth_session.uuid
        )

    @staticmethod
    async def refresh_token(
            conn: Connection | Database,
            refresh_token: UUID,
            session_uuid: UUID
    ) -> AuthResponse:
        new_refresh_token = await AuthSessionService.refresh_token(
            conn,
            session_uuid=session_uuid,
            refresh_token=refresh_token
        )

        return AuthResponse(
            access_token=SecurityService._generate_access_token(session_uuid),
            refresh_token=new_refresh_token,
            session_uuid=session_uuid
        )

    @staticmethod
    async def get_session_data(
            conn: Connection | Database,
            redis: Redis,
            access_token: str
    ) -> SessionData:
        session_uuid = SecurityService._fetch_session_uuid(access_token)

        session_data = await SessionDataCache(redis).get(session_uuid)
        if session_data is None:
            session_data = await SecurityService.load_session_data(
                conn=conn,
                redis=redis,
                session_uuid=session_uuid
            )

        return session_data

    @staticmethod
    async def load_session_data(
            conn: Connection | Database,
            redis: Redis,
            session_uuid: UUID
    ) -> SessionData:
        auth_session = await AuthSessionStore(conn).get(uuid=session_uuid)
        user = await UserStore(conn).get(pk=auth_session.user_id)

        session_data = SecurityService._build_session_data(
            auth_session=auth_session,
            user=user
        )

        await SessionDataCache(redis).set(
            session_data,
            ex=auth_settings.AUTH_CACHE_SESSION_ALIVE_SECONDS
        )

        return session_data

    @staticmethod
    async def start_email_verification(
            conn: Connection | Database,
            email: EmailStr
    ) -> EmailVerificationResponse:
        email_verification = await EmailVerificationService.start_verification(
            conn,
            email=email
        )

        return EmailVerificationResponse(
            key=email_verification.key,
            verified=email_verification.verified,
            attempts_left=email_verification.attempts_left,
            valid_until=email_verification.valid_until
        )

    @staticmethod
    async def complete_email_verification(
            conn: Connection | Database,
            key: UUID,
            code: str
    ) -> EmailVerificationResponse:
        email_verification = await EmailVerificationService.complete_verification(
            conn,
            key=key,
            code=code
        )

        return EmailVerificationResponse(
            key=email_verification.key,
            verified=email_verification.verified,
            attempts_left=email_verification.attempts_left,
            valid_until=email_verification.valid_until
        )

    @staticmethod
    async def register_account(
            conn: Connection | Database,
            session_data: SessionData,
            password: str,
            email_verification_key: UUID
    ) -> AuthResponse:
        email_verification = await EmailVerificationService.validate_verified(conn, key=email_verification_key)

        if await UserStore(conn).get(
            email=email_verification.email,
            return_deleted=False,
            return_none=True
        ):
            raise UserAlreadyExists

        await UserStore(conn).register(
            pk=session_data.user_id,
            email=email_verification.email,
            password_hash=SecurityService._get_password_hash(password)
        )

        # todo Инвалидация гостевого токена
        auth_session = await AuthSessionStore(conn).create(
            AuthSessionForm(
                user_id=session_data.user_id,
                platform=session_data.platform,
                presign=False
            )
        )

        return AuthResponse(
            access_token=SecurityService._generate_access_token(auth_session.uuid),
            refresh_token=auth_session.refresh_token,
            session_uuid=auth_session.uuid
        )

    @staticmethod
    def _build_session_data(
            auth_session: AuthSession,
            user: User
    ) -> SessionData:
        return SessionData(
            session_id=auth_session.id,
            session_uuid=auth_session.uuid,
            presign=auth_session.presign,
            user_id=user.id,
            user_uuid=user.uuid,
            user_group_id=user.group_id,
            platform=auth_session.platform
        )

    @staticmethod
    def _generate_access_token(session_uuid: UUID) -> str:
        return jwt.create_token(
            {'session_uuid': str(session_uuid)}
        )

    @staticmethod
    def _fetch_session_uuid(access_token: str) -> UUID:
        return UUID(jwt.decode_token(access_token)['session_uuid'])

    @staticmethod
    def _get_password_hash(password: str) -> str:
        return md5((password + auth_settings.AUTH_PASSWORD_SALT).encode()).hexdigest()
