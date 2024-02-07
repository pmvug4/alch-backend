from typing import Optional, Union
from uuid import uuid4, UUID

from databases import Database
from databases.interfaces import Record
from asyncpg import UniqueViolationError
from loguru import logger

from core.common.groups_and_roles import all_group_map, BaseUserGroups, GROUP_COURIER, GROUP_CUSTOMER
from core.db.models import UnInitedData
from core.db.tables import DBTables
from core.db import tools as db_tools
from core.exception import IncorrectCredentials

from .model import User, AccessServer, UserForm
from .errors import UserBulkCreationUniqueIndexError


def parse_user_data(
        record: Record,
        return_none: bool = False
) -> User | None:
    if record:
        data = dict(record._mapping)
        return User(user_id=data.pop('id'), **data)
    else:
        if return_none:
            return None
        else:
            raise IncorrectCredentials


async def get_user(
        db: Database,
        pk: int = None,
        uuid: UUID | str = None,
        username: str = None,
        group: BaseUserGroups = None,
        return_none: bool = True,
        assert_not_deactivated: bool = False,
        assert_refresh_token: str = False
) -> Optional[User]:
    params = {}
    sql = f""" SELECT * FROM {DBTables.users} WHERE """

    if uuid is not None:
        sql += " uuid = :uuid "
        params['uuid'] = uuid
    elif pk is not None:
        sql += " id = :pk "
        params['pk'] = pk
    elif username is not None and group is not None:
        sql += " username = :username AND group_id = :group "
        params['username'] = username
        params['group'] = all_group_map[group]
    else:
        raise TypeError

    user = parse_user_data(await db.fetch_one(sql, params), return_none=return_none)

    if user is not None:
        if assert_not_deactivated and user.deactivated:
            raise IncorrectCredentials
        if assert_refresh_token and assert_refresh_token != user.refresh_token:
            raise IncorrectCredentials

    return user


async def multibase_get_user(
        main_db: Database,
        demo_db: Database,
        pk: int = None,
        uuid: UUID = None,
        username: str = None,
        group: BaseUserGroups = None,
        return_none: bool = True,
        assert_not_deactivated: bool = False,
        assert_refresh_token: str = None
) -> Optional[User]:
    user_main = await get_user(
        main_db, pk=pk,
        uuid=uuid,
        username=username,
        group=group,
        return_none=True,
        assert_not_deactivated=assert_not_deactivated,
        assert_refresh_token=assert_refresh_token
    )

    user_demo = await get_user(
        demo_db, pk=pk,
        uuid=uuid,
        username=username,
        group=group,
        return_none=True,
        assert_not_deactivated=assert_not_deactivated,
        assert_refresh_token=assert_refresh_token
    )

    if user_main is not None and user_demo is not None:
        logger.warning("Multibase user existence")
        return user_demo
    elif user_main is None and user_demo is None:
        if return_none:
            return None
        else:
            raise IncorrectCredentials
    else:
        if user_main is not None:
            user_main.access_server = AccessServer.main
            return user_main
        elif user_demo is not None:
            user_demo.access_server = AccessServer.demo
            return user_demo
        else:
            raise RuntimeError


async def update_user(db: Database, user_id: int,
                      refresh_token: Union[str, None, UnInitedData] = UnInitedData()
                      ) -> User:
    data = {
        k: v for k, v in zip(
            ['refresh_token', ],
            [refresh_token, ]
        ) if type(v) is not UnInitedData
    }

    up_str = ', '.join([f"{k} = :{k}" for k in data.keys()])

    sql = f"""
                UPDATE users SET
                    {up_str}
                WHERE id=:user_id 
                RETURNING *                
    """

    res = await db.fetch_one(sql, data | {"user_id": user_id})

    return parse_user_data(res, return_none=False)


async def create_user_in_db(
        db: Database,
        username: str,
        group_id: int,
        app_zone: str = None
):
    sql = f"""
                INSERT INTO users (
                    username,
                    group_id,
                    app_zone
                ) VALUES (
                    :username,
                    :group_id,
                    :app_zone
                ) RETURNING id                          
           """
    try:
        res = await db.execute(
            sql, {
                "username": username,
                "group_id": group_id,
                "app_zone": app_zone
            }
        )
    except Exception as e:
        logger.exception(f"{repr(e)}")
        return None

    return res


async def create_users(
        db: Database,
        forms: list[UserForm]
) -> list[int]:
    try:
        records = await db_tools.create_many(
            db, table='users',
            forms=forms,
            returning='id'
        )
    except UniqueViolationError as exc:
        raise UserBulkCreationUniqueIndexError.build(['...'])  # todo parse exc
    else:
        return [r['id'] for r in records]


async def link_user_preference(db: Database, pk: int, preferences_id: int) -> None:
    sql = f"UPDATE users SET preferences_id = :preferences_id WHERE id = :id"
    await db.execute(sql, {'preferences_id': preferences_id, 'id': pk})


async def link_users_preferences(db: Database, data: list[(int, int)]) -> None:
    """
        data: [(user_id, preferences_id)]
    """
    holders = ', '.join(
        [f"({user_id}::integer, {preferences_id}::integer)" for i, (user_id, preferences_id) in enumerate(data)])
    sql = f"""
        UPDATE {DBTables.users} SET 
            preferences_id = temp.preferences_id
        FROM (values {holders} ) as temp(user_id, preferences_id)
        WHERE id = temp.user_id
    """

    await db.execute(sql)


async def deactivate_user(db: Database, pk: int) -> str:
    sql = (
        f"UPDATE users SET "
        f"username = concat_ws('_', 'DELETED', '{uuid4()}', username), deactivated = true "
        f"WHERE id = :id RETURNING username"
    )

    record = await db.fetch_one(sql, {'id': pk})
    return record._mapping['username']


async def deactivate_app_zone_users(
        db: Database,
        app_zone: str
) -> list[(int, int)]:
    sql = f"""
        UPDATE users SET 
            username = CONCAT_WS('_', 'DELETED', uuid_generate_v4()::varchar, username),
            deactivated = true
        WHERE app_zone = :app_zone
        RETURNING id, group_id
    """

    return [
        (x._mapping['id'], x._mapping['group_id'])
        for x in await db.fetch_all(sql, {'app_zone': app_zone})
    ]


async def get_user_ids_list_by_newsletter(db: Database, enabled: bool = True) -> list[int]:
    sql = f"SELECT id FROM users WHERE " \
          f"preferences_id in (SELECT id FROM {DBTables.preferences} WHERE news_enabled = :enabled)"
    return [x._mapping['id'] for x in await db.fetch_all(sql, {'enabled': enabled})]


async def get_all_users_ids(db: Database) -> list[int]:
    sql = f"SELECT id FROM users"
    return [x._mapping['id'] for x in await db.fetch_all(sql)]


async def get_courier_user_ids(db: Database, only_not_deactivated: bool = True) -> list[int]:
    sql = "SELECT id FROM users WHERE group_id = :group_id"
    if only_not_deactivated:
        sql += " AND deactivated = false"
    return [x._mapping["id"] for x in await db.fetch_all(sql, {"group_id": GROUP_COURIER})]


async def get_customer_user_ids(db: Database, only_not_deactivated: bool = True) -> list[int]:
    sql = "SELECT id FROM users WHERE group_id = :group_id"
    if only_not_deactivated:
        sql += " AND deactivated = false"
    return [x._mapping["id"] for x in await db.fetch_all(sql, {"group_id": GROUP_CUSTOMER})]
