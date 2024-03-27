import datetime
from typing import Optional
from uuid import UUID

from core.objects.store import ObjectStore
from core.db.tables import DBTables

from .errors import EmailVerificationNotFound
from .models import EmailVerification, EmailVerificationForm


class EmailVerificationStore(ObjectStore):
    _table = DBTables.email_verifications
    _model = EmailVerification
    _not_found = EmailVerificationNotFound

    async def get(
            self,
            pk: int = None,
            key: UUID = None,
            for_update: bool = False,
            return_none: bool = False
    ) -> Optional[EmailVerification]:
        sql = f"SELECT * FROM {self._table} WHERE "

        if pk:
            sql += " id = :x "
        elif key:
            sql += " key = :x "
        else:
            raise TypeError

        if for_update:
            sql += " FOR UPDATE "

        return self._parse(
            await self.conn.fetch_one(sql, {'x': pk or key}),
            return_none=return_none
        )

    async def create(
            self,
            form: EmailVerificationForm
    ) -> EmailVerification:
        sql = f"""
            INSERT INTO {self._table} (
                email,
                code,
                attempts_left,
                valid_until
            ) VALUES (
                :email,
                :code,
                :attempts_left,
                :valid_until
            )
            RETURNING *; 
        """

        return self._parse(
            await self.conn.fetch_one(sql, form.dict()),
            return_none=False
        )

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
