from uuid import UUID
from typing import Optional

from core.db.tables import DBTables
from core.objects.store import ObjectStore

from .models import AuthSessionForm, AuthSession
from .errors import AuthSessionNotFoundError


class AuthSessionStore(ObjectStore):
    _table = DBTables.auth_sessions
    _model = AuthSession
    _not_found = AuthSessionNotFoundError

    async def create(
            self,
            form: AuthSessionForm
    ) -> AuthSession:
        sql = f"""
            INSERT INTO {self._table} (user_id, platform, presign) VALUES (:user_id, :platform, :presign) RETURNING *;
        """

        return self._parse(
            await self.conn.fetch_one(sql, form.dict()),
            return_none=False
        )

    async def get(
            self,
            pk: int = None,
            uuid: UUID = None,
            for_update: bool = False,
            return_none: bool = False
    ) -> Optional[AuthSession]:
        values = {}

        if pk is not None:
            condition = ' id = :pk '
            values['pk'] = pk
        elif uuid is not None:
            condition = ' uuid = :uuid '
            values['uuid'] = uuid
        else:
            raise TypeError

        sql = f"SELECT * FROM {self._table} WHERE {condition} {'FOR UPDATE' if for_update else ''}"

        return self._parse(
            await self.conn.fetch_one(sql, values),
            return_none=return_none
        )

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
