from typing import Optional
from uuid import UUID

from core.db.tables import DBTables

from core.objects.store import ObjectStore

from .models import User, PresignUserForm
from .errors import UserNotFoundError


class UserStore(ObjectStore):
    _table = DBTables.users
    _model = User
    _not_found = UserNotFoundError

    async def create_presign(
            self,
            form: PresignUserForm
    ) -> User:
        sql = f"""
            INSERT INTO {self._table} (group_id) VALUES (:group_id) RETURNING *;
        """

        return self._parse(
            await self.conn.fetch_one(sql, form.dict()),
            return_none=False
        )

    async def register(
            self,
            pk: int,
            email: str,
            password_hash: str
    ) -> User:
        sql = f"""
            UPDATE {self._table} SET 
                email = :email,
                password_hash = :password_hash,
                updated_at = now()
            WHERE id = :pk
            RETURNING *
        """

        return self._parse(
            await self.conn.fetch_one(
                sql, {
                    'email': email,
                    'password_hash': password_hash,
                    'pk': pk
                }
            )
        )

    async def get(
            self,
            pk: int = None,
            uuid: UUID = None,
            email: str = None,
            only_not_deleted: bool = None,
            return_none: bool = False
    ) -> Optional[User]:
        values = {}
        sql = f"SELECT * FROM {self._table} WHERE "

        if pk is not None:
            sql += " id = :pk "
            values['pk'] = pk
        elif uuid is not None:
            sql += " uuid = :uuid "
            values['uuid'] = uuid
        elif email is not None:
            sql += " email = :email "
            values['email'] = email
        else:
            raise TypeError

        if only_not_deleted:
            sql += " AND deleted_at IS NULL "

        return self._parse(
            await self.conn.fetch_one(sql, values),
            return_none=return_none
        )

    async def get_for_login(
            self,
            email: str,
            password_hash: str,
            group_id: int,
            return_none: bool = False
    ) -> Optional[User]:
        sql = f"""
            SELECT * FROM {self._table} 
            WHERE 
                email = :email AND
                password_hash = :password_hash AND
                group_id = :group_id
        """

        return self._parse(
            await self.conn.fetch_one(
                sql, {
                    'email': email,
                    'password_hash': password_hash,
                    'group_id': group_id
                }
            ),
            return_none=return_none
        )
