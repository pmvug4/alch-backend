import json
from typing import Optional
from uuid import UUID

import databases.backends.postgres
from asyncpg import Record
from databases.core import Database, Connection
from pydantic import BaseModel


async def create(
        db: Database | Connection,
        table: str,
        form: BaseModel,
        exclude: set = None,
        exclude_none: bool = True,
        exclude_unset: bool = True,
        extra_data: dict = None
) -> Record:
    data: dict = form.model_dump(
        exclude=exclude,
        exclude_none=exclude_none,
        exclude_unset=exclude_unset
    )

    if extra_data:
        data.update(extra_data)

    key_ph = gen_key_holders(data)
    values_ph = gen_value_holders(data)

    sql = f"INSERT INTO {table} {key_ph} " \
          f"VALUES {values_ph} RETURNING *"

    return await db.fetch_one(sql, data)


async def create_many(
        db: Database | Connection,
        table: str,
        forms: list[BaseModel] | tuple[BaseModel],
        exclude: set = None,
        exclude_none: bool = True,
        exclude_unset: bool = True,
        returning: str = '*'
) -> list[Record]:
    if not forms:
        return []

    datas = [
        form.model_dump(
            exclude=exclude,
            exclude_none=exclude_none,
            exclude_unset=exclude_unset
        )
        for form in forms
    ]

    key_ph = gen_key_holders(datas[0])
    values_ph = ','.join([gen_value_holders(data, suffix=f'_{i}') for i, data in enumerate(datas)])

    sql = f"INSERT INTO {table} {key_ph} VALUES {values_ph} RETURNING {returning}"

    values = {}
    for i, data in enumerate(datas):
        for key, value in data.items():
            values[key + f'_{i}'] = value

    return await db.fetch_all(sql, values)


async def get(
        db: Database | Connection,
        table: str,
        pk_value,
        pk_field: str = 'id',
        returning: str = '*',
        for_update: bool = False,
        return_deleted: bool = False
) -> Record | None:
    sql = (
            f"SELECT {returning} FROM {table} WHERE {pk_field} = :id " +
            ("FOR UPDATE" if for_update else "")
    )

    record = await db.fetch_one(sql, {'id': pk_value})
    if record is not None:
        if (not return_deleted) and (record._mapping.get('deleted_at', None) is not None):
            return None

    return record


class FetchRelated:
    def __init__(
            self,
            table: str,
            join_on: str,
            join_to: str,
            returning_as: Optional[str] = None,
            inner_join: bool = True
    ):
        self.table = table
        self.join_on = join_on
        self.join_to = join_to
        self.returning_as = returning_as or table
        self.inner_join = inner_join


async def get_list(
        db: Database | Connection,
        table: str,
        pk_value: Optional[
            int | str | UUID |
            list[int] |
            list[str] |
            list[UUID]
        ] = None,
        pk_field: Optional[str] = 'id',
        returning: str = '*',
        extra_filter: Optional[str] = None,
        fetch_related: list[FetchRelated] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
) -> list[Record]:
    values = {}
    fetch_related = fetch_related or []

    _related_selection = [returning]
    _related_join = []
    for x in fetch_related:
        if x.inner_join:
            j = ' INNER JOIN '
        else:
            j = ' LEFT JOIN '

        j = f' {j} {x.table} ON {x.join_on} = {x.join_to} '
        s = f" to_json({x.table}.*) AS {x.returning_as} "

        _related_join.append(j)
        _related_selection.append(s)

    sql = f"""
        SELECT
            COUNT(*) OVER () AS _total_items,
            {returning} {',' + ','.join(_related_selection) if len(_related_selection) else ''} 
        FROM 
            {table} {' '.join(_related_join)} 
        WHERE TRUE 
            {f'AND {pk_field} = ANY(:pk_value)' if pk_field is not None else ''}
            {f'AND {extra_filter}' if extra_filter else ''}
        {f'ORDER BY {order_by}' if order_by is not None else ''}
    """

    if limit:
        sql += f" LIMIT :limit "
        values |= {'limit': limit}
    if offset:
        sql += f" OFFSET :offset "
        values |= {'offset': offset}

    if pk_field:
        if isinstance(pk_value, list):
            values['pk_value'] = pk_value
        else:
            values['pk_value'] = [pk_value]

    records = await db.fetch_all(sql, values)
    return records


async def update_by_id(
        db: Database | Connection,
        table: str,
        data: dict,
        pk_value: int | str,
        pk_field: str = 'id',
        with_updated_at: bool = True,
        returning: str = '*'
) -> Record:
    atime_string = ", updated_at = now() " if with_updated_at else " "
    holders = gen_update_holders(data)

    sql = f"UPDATE {table} SET {holders}{atime_string} WHERE {pk_field} = :pk RETURNING {returning}"

    return await db.fetch_one(sql, data | {'pk': pk_value})


async def delete_by_id(
        db: Database | Connection,
        table: str,
        pk_value: int | str,
        pk_field: str = 'id',
        returning: str = '*'
) -> Record:
    sql = f"UPDATE {table} SET deleted_at = now() WHERE {pk_field} = :pk RETURNING {returning}"
    return await db.fetch_one(sql, {'pk': pk_value})


def gen_key_holders(data: dict, with_brackets: bool = True) -> str:
    s = ','.join([f"{k}" for k in data.keys()])
    if with_brackets:
        s = '(' + s + ')'
    return s


def gen_value_holders(data: dict, with_brackets: bool = True, suffix: str = '') -> str:
    s = ','.join([f":{k}{suffix}" for k in data.keys()])
    if with_brackets:
        s = '(' + s + ')'
    return s


def gen_update_holders(data: dict) -> str:
    return ','.join([f"{k} = :{k}" for k in data.keys()])


class Filters:
    def __init__(self):
        self._filters = []
        self._count = 0

    def add(self, key: str, action: str, value, bind: bool = True):
        self._filters.append({
            'key': str(key),
            'holder': f"{key}_{self._count}",
            'value': value,
            'action': action,
            'bind': bind
        })
        self._count += 1

    def build_sql(self, with_where: bool = True) -> (str, dict):
        s = " WHERE " if with_where else " "

        sql_filters = []
        bindings = {}
        for filter in self._filters:
            key = filter['key']
            value = filter['value']
            action = filter['action']
            bind = filter['bind']
            holder = filter['holder']

            if bind:
                sql_filters.append(f" {key} {action} :{holder} ")
                bindings[holder] = value
            else:
                sql_filters.append(f" {key} {action} {value} ")

        return s + " AND ".join(sql_filters), bindings


def to_int_list_for_in(array: list[int]) -> str:
    s = ','.join(map(str, array))
    return "(" + s + ")"


def get_data(record: Record | str | dict | None) -> dict | None:
    if isinstance(record, Record) or isinstance(record, databases.backends.postgres.Record):
        data = dict(record._mapping)
    elif isinstance(record, dict):
        data = record
    elif isinstance(record, str):
        data = json.loads(record)
    elif record is None:
        data = None
    else:
        raise RuntimeError

    return data
