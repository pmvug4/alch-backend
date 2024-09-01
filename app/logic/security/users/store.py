from typing import Optional
from uuid import UUID

from core.db.tables import DBTables
from core.objects.store import ObjectStore

from .models import User, PresignUserForm
from .errors import UserNotFoundError


class UserStore(
    ObjectStore[
        User,
        PresignUserForm,
        None,
        None,
        UserNotFoundError,
    ]
):
    _table = DBTables.users

    _model = User
    _model_create_form = PresignUserForm
    _model_put_form = None
    _model_patch_form = None

    _not_found = UserNotFoundError

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
            for_update: bool = False,
            return_none: bool = False,
            return_deleted: bool = False
    ) -> Optional[User]:
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
        elif email is not None:
            return await super().get(
                pk_value=email,
                pk_field='email',
                for_update=for_update,
                return_none=return_none,
                return_deleted=return_deleted
            )
        else:
            raise TypeError

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
