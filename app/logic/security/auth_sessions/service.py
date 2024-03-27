from uuid import UUID

from databases.core import Database, Connection

from .store import AuthSessionStore
from .errors import WrongAuthSessionRefreshToken


class AuthSessionService:
    @staticmethod
    async def refresh_token(
            conn: Database | Connection,
            session_uuid: UUID,
            refresh_token: UUID
    ) -> UUID:
        auth_session = await AuthSessionStore(conn).get(uuid=session_uuid)

        if auth_session.refresh_token != refresh_token:
            raise WrongAuthSessionRefreshToken

        return (await AuthSessionStore(conn).refresh_token(
            uuid=session_uuid,
            refresh_token=refresh_token
        )).refresh_token
