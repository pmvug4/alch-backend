import datetime
from typing import Optional
from uuid import UUID

from core.objects.store import ObjectStore
from core.db.tables import DBTables

from .errors import EmailVerificationNotFound
from .models import EmailVerification, EmailVerificationForm


class EmailVerificationStore(ObjectStore[
        EmailVerification,
        EmailVerificationForm,
        None,
        EmailVerificationNotFound,
    ]
):
    _table = DBTables.email_verifications

    _model = EmailVerification
    _model_create_form = EmailVerificationForm
    _model_update_form = None

    _not_found = EmailVerificationNotFound

    async def get(
            self,
            pk: int = None,
            key: UUID = None,
            for_update: bool = False,
            return_none: bool = False,
            return_deleted: bool = False
    ) -> Optional[EmailVerification]:
        if pk is not None:
            return await super().get(
                pk_value=pk,
                pk_field='id',
                for_update=for_update,
                return_none=return_none,
                return_deleted=return_deleted
            )
        elif key is not None:
            return await super().get(
                pk_value=key,
                pk_field='key',
                for_update=for_update,
                return_none=return_none,
                return_deleted=return_deleted
            )
        else:
            raise TypeError

    async def check_next_avail(
            self,
            email: str,
            min_interval_s: int
    ) -> bool:
        sql = f"""
            SELECT id FROM {self._table} 
            WHERE 
                email = :email AND 
                now() < created_at + :min_interval AND
                NOT verified
            LIMIT 1
        """

        return (
            await self.conn.fetch_one(
                sql, {
                    'email': email,
                    'min_interval': datetime.timedelta(seconds=min_interval_s)
                }
            ) is None
        )

    async def mark_verified(
            self,
            pk: int
    ) -> EmailVerification:
        sql = f"UPDATE {self._table} SET verified = true WHERE id = :pk RETURNING *"
        return self._parse(
            await self.conn.fetch_one(sql, {'pk': pk}),
            return_none=False
        )

    async def remove_attempt(
            self,
            pk: int
    ) -> None:
        await self.conn.fetch_one(
            f"UPDATE {self._table} SET attempts_left = attempts_left - 1 WHERE id = :pk",
            {'pk': pk}
        )
