from enum import Enum
from typing import Optional
from uuid import uuid4

from databases import Database
from databases.interfaces import Record
from pydantic import BaseModel

from api.account.model import PlatformType
from core.db import tools as db_tools
from core.db.tables import DBTables
from core.faq.exceptions import FaqIsNotExist
from core.models import Pagination


class Role(str, Enum):
    client = 'client'
    manager = 'manager'
    courier = 'courier'


class FaqForm(BaseModel):
    platform: PlatformType
    priority: int
    role: Role
    question: str
    answer: str
    group_uuid: str | None


class Faq(FaqForm):
    id: int

    @classmethod
    def _parse(
            cls,
            record: Record | dict | str,
            return_none: bool = False
    ) -> Optional['Faq']:
        if record:
            return cls.parse_obj(db_tools.get_data(record))
        else:
            if return_none:
                return None
            else:
                raise FaqIsNotExist

    @classmethod
    async def db_get(
            cls, db: Database,
            pk: int = None,
            platform: PlatformType = None,
            priority: int = None,
            role: Role = None,
            return_none: bool = False
    ) -> 'Faq':

        values = {}
        sql = f"""
                SELECT id, platform, priority, role, question, answer, group_uuid 
                FROM {DBTables.faq}
                WHERE true
            """

        if pk:
            sql += " AND id = :id "
            values.update({"id": pk})

        if platform:
            sql += " AND platform = :platform "
            values.update({"platform": platform})

        if priority:
            sql += " AND priority = :priority "
            values.update({"priority": priority})

        if role:
            sql += " AND role = :role "
            values.update({"role": role})
        record = await db.fetch_one(sql, values)

        return cls._parse(record, return_none)

    @classmethod
    async def db_delete(
            cls, db: Database,
            pk: int = None,
            platform: PlatformType = None,
            role: Role = None,
            group_uuid: str = None
    ) -> bool:
        values = {}
        sql = f"""
            DELETE FROM {DBTables.faq}
            WHERE true 
            """
        if pk:
            sql += " AND id = :id "
            values.update({"id": pk})

        if platform:
            sql += " AND platform = :platform "
            values.update({"platform": platform})

        if role:
            sql += " AND role = :role "
            values.update({"role": role})

        if group_uuid:
            sql += " AND group_uuid = :group_uuid "
            values.update({"group_uuid": group_uuid})
        await db.execute(sql, values)
        return True


class FaqList(BaseModel):
    faq: list[Faq]
    pagination: Pagination

    @classmethod
    def _parse(
            cls,
            records: list[Record],
            page_number: int,
            page_size: int
    ) -> Optional['FaqList']:
        total_count = 0
        if records:
            total_count = records[0]._mapping['_total_count']

        return cls(
            faq=[Faq._parse(x) for x in records],
            pagination=Pagination(
                total_items=total_count,
                total_pages=db_tools.calc_total_pages(total_count, page_size),
                page_number=page_number,
                page_size=page_size
            )
        )

    @classmethod
    async def db_get(
            cls, db: Database,
            platform: PlatformType = None,
            role: Role = None,
            group_uuid: str = None,
            page_size: int = 20,
            page_number: int = 1
    ) -> 'FaqList':
        limit, offset = db_tools.calc_limit_offset(page_size, page_number)

        values = {
            'limit': limit,
            'offset': offset
        }
        sql = f"""
            SELECT id, platform, priority, role, question, answer, group_uuid, count(*) over () as _total_count 
            FROM {DBTables.faq}
            WHERE true 
        """

        if platform:
            sql += " AND platform = :platform "
            values.update({"platform": platform})

        if role:
            sql += " AND role = :role "
            values.update({"role": role})

        if group_uuid:
            sql += " AND group_uuid = :group_uuid "
            values.update({"group_uuid": group_uuid})
        sql += " ORDER BY priority ASC LIMIT :limit OFFSET :offset "
        records = await db.fetch_all(sql, values)

        return cls._parse(
            records,
            page_number=page_number,
            page_size=page_size
        )

    @classmethod
    async def db_update(
            cls,
            items: list[FaqForm],
            db: Database
    ) -> bool:
        values = {}
        values_clause = ""
        uuid = str(uuid4())
        for i, item in enumerate(items):
            values_clause += f"(:platform{i}, :priority{i}, :role{i}, :question{i}, :answer{i}, :group_uuid{i}),"
            values.update({
                f"platform{i}": item.platform,
                f"priority{i}": item.priority,
                f"role{i}": item.role,
                f"question{i}": item.question,
                f"answer{i}": item.answer,
                f"group_uuid{i}": item.group_uuid or uuid
            })
        sql = f"""
        INSERT INTO {DBTables.faq} (platform, priority, role, question, answer, group_uuid)
            VALUES 
                {values_clause[:-1]}
            ON CONFLICT (platform, priority, role) DO UPDATE 
                SET question = excluded.question, answer = excluded.answer
            RETURNING *;"""
        await db.execute(sql, values)
        return True
