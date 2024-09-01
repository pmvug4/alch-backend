from uuid import UUID
from typing import Optional

from core.db.tables import DBTables
from core.objects.store import ObjectStore

from .models import AuthSessionForm, AuthSession
from .errors import AuthSessionNotFoundError


class AuthSessionStore(
    ObjectStore[
        AuthSession,
        AuthSessionForm,
        None,
        None,
        AuthSessionNotFoundError,
    ]
):
    _table = DBTables.auth_sessions

    _model = AuthSession
    _model_create_form = AuthSessionForm
    _model_put_form = None
    _model_patch_form = None

    _not_found = AuthSessionNotFoundError

    async def get(
            self,
            pk: int = None,
            uuid: UUID = None,
            for_update: bool = False,
            return_none: bool = False,
            return_deleted: bool = False
    ) -> Optional[AuthSession]:
        if pk is not None:
            return await super().get(
                pk_value=pk,
                pk_field='id',
                for_update=for_update,
                return_none=return_none,
                return_deleted=return_deleted
            )
        elif uuid is not None:
            return await super().get(
                pk_value=uuid,
                pk_field='uuid',
                for_update=for_update,
                return_none=return_none,
                return_deleted=return_deleted
            )
        else:
            raise TypeError

    async def refresh_token(
            self,
            uuid: UUID,
            refresh_token: UUID
    ) -> AuthSession:
        sql = f"""
            UPDATE {self._table} 
            SET 
                refresh_token = uuid_generate_v4(),
                updated_at = now()
            WHERE 
                uuid = :uuid AND 
                refresh_token = :refresh_token 
            RETURNING *
        """

        return self._parse(
            await self.conn.fetch_one(
                sql, {
                    'uuid': uuid,
                    'refresh_token': refresh_token
                }
            ),
            return_none=False
        )
