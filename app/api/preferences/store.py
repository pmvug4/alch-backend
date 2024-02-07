from databases import Database
from databases.interfaces import Record

from api.users.store import link_user_preference, link_users_preferences
from core.db.tables import DBTables
from .exceptions import *
from .models import *


def _parse_preferences(
        record: Record,
        return_none: bool = False
) -> Preferences | None:
    if record:
        return Preferences.parse_obj(record._mapping)
    else:
        if return_none:
            return None
        else:
            raise PreferenceDoesNotExist()


async def get_preference(
        db: Database,
        pk: int = None,
        user_id: int = None,
        return_none: bool = False
) -> Preferences:
    if pk:
        sql = f"SELECT * FROM {DBTables.preferences} WHERE id = :id"
    elif user_id:
        sql = f"SELECT * FROM {DBTables.preferences} WHERE id = " \
              f"(SELECT preferences_id FROM {DBTables.users} WHERE id = :id)"
    else:
        raise RuntimeError

    record = await db.fetch_one(sql, {'id': pk or user_id})

    return _parse_preferences(record, return_none)


async def get_preferences_list(
        db: Database,
        users_ids: list[int],
        for_update: bool = False
) -> dict[int, Preferences]:
    if not users_ids:
        return {}

    sql = f"SELECT {DBTables.preferences}.*, {DBTables.users}.id AS user_id " \
          f"FROM {DBTables.preferences} JOIN {DBTables.users} " \
          f"ON {DBTables.users}.preferences_id = {DBTables.preferences}.id " \
          f"WHERE {DBTables.users}.id = ANY(:ids) " + (" FOR UPDATE " if for_update else "")

    return {
        x._mapping['user_id']: _parse_preferences(x)
        for x in await db.fetch_all(sql, {'ids': users_ids})
    }


async def create_preferences_list(
        db: Database,
        users_ids: list[int]
) -> dict[int, Preferences]:
    if not users_ids:
        return {}

    users_ids = list(map(int, users_ids))

    preferences = await _create_preferences(db, count=len(users_ids))
    pairs = {
        user_id: preferences
        for user_id, preferences in zip(users_ids, preferences)
    }
    await link_users_preferences(db, data=[(user_id, preferences.id) for user_id, preferences in pairs.items()])

    return pairs


async def get_or_create_preferences_list(
        db: Database,
        users_ids: list[int]
) -> dict[int, Preferences]:
    async with db.transaction():
        pairs = await get_preferences_list(db, users_ids=users_ids, for_update=True)
        pairs |= await create_preferences_list(db, users_ids=list(set(users_ids).difference([x for x in pairs])))
        return pairs


async def _create_preferences(db: Database, count: int = 1) -> list[Preferences]:
    values = ', '.join(['(DEFAULT)' for _ in range(count)])
    sql = f"INSERT INTO {DBTables.preferences} (news_enabled) VALUES {values} RETURNING *"
    records = await db.fetch_all(sql)

    return [_parse_preferences(x) for x in records]


async def create_preferences(db: Database, user_id: int) -> Preferences:
    async with db.transaction():
        preferences = (await _create_preferences(db))[0]
        await link_user_preference(db, pk=user_id, preferences_id=preferences.id)

        return preferences


async def update_news_enabled(db: Database, pk: int, value: bool) -> Preferences:
    sql = f"UPDATE {DBTables.preferences} SET news_enabled = :value WHERE id = :id RETURNING *"
    record = await db.fetch_one(sql, {'value': value, 'id': pk})

    return _parse_preferences(record, False)


async def update_push_enabled(db: Database, pk: int, value: bool) -> Preferences:
    sql = f"UPDATE {DBTables.preferences} SET push_enabled = :value WHERE id = :id RETURNING *"
    record = await db.fetch_one(sql, {'value': value, 'id': pk})

    return _parse_preferences(record, False)


async def update_sms_enabled(db: Database, pk: int, value: bool) -> Preferences:
    sql = f"UPDATE {DBTables.preferences} SET sms_enabled = :value WHERE id = :id RETURNING *"
    record = await db.fetch_one(sql, {'value': value, 'id': pk})

    return _parse_preferences(record, False)
