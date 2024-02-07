import datetime
import json
from typing import Union, Optional

import asyncpg
from databases import Database
from databases.interfaces import Record

from core.common.groups_and_roles import GROUP_COURIER, GROUP_CUSTOMER
from core.db import tools as db_tools
from core.db.tables import DBTables
from core.models import Pagination
from core.push.models import AppPlatform
from . import models
from .exceptions import *
from ..db.models import UnInitedData


class NoticeReceiver:
    @staticmethod
    def _parse(
            record: Record,
            return_none: bool = False
    ) -> models.NoticeReceiver | None:
        if record:
            return models.NoticeReceiver.parse_obj(record._mapping)
        else:
            if return_none:
                return None
            else:
                raise NoticeReceiverDoesNotExist()

    @staticmethod
    async def get(
            db: Database,
            pk: int = None,
            user_id: int = None,
            return_none: bool = False,
            for_update: bool = False
    ) -> models.NoticeReceiver:
        assert (pk is None) != (user_id is None), "One of user_id and pk is required"

        sql = f"SELECT * FROM {DBTables.notice_receiver} WHERE "

        if pk:
            sql += f" id = :id "
        elif user_id:
            sql += f" user_id = :id "

        if for_update:
            sql += " FOR UPDATE "
        record = await db.fetch_one(sql, {'id': pk or user_id})

        return NoticeReceiver._parse(record, return_none)

    @staticmethod
    async def create_list(
            db: Database,
            forms: list[models.NoticeReceiverForm]
    ) -> list[models.NoticeReceiver]:
        return [
            NoticeReceiver._parse(x)
            for x in await db_tools.create_many(
                db, table=DBTables.notice_receiver,
                forms=forms
            )
        ]

    @staticmethod
    async def get_list(
            db: Database,
            users_ids: list[int],
            for_update: bool = False
    ) -> list[models.NoticeReceiver]:
        if not users_ids:
            return []

        sql = f"SELECT * FROM {DBTables.notice_receiver} WHERE user_id = any(:ids)" + \
              (" FOR UPDATE " if for_update else "")
        records = await db.fetch_all(sql, {'ids': users_ids})

        return [NoticeReceiver._parse(x) for x in records]

    @staticmethod
    async def get_or_create_list(
            db: Database,
            users_ids: list[int]
    ) -> dict[int, models.NoticeReceiver]:
        async with db.transaction():
            receivers = await NoticeReceiver.get_list(db, users_ids=users_ids, for_update=True)
            receivers += await NoticeReceiver.create_list(
                db, forms=[
                    models.NoticeReceiverForm(user_id=x)
                    for x in set(users_ids).difference([recv.user_id for recv in receivers])
                ]
            )
            return {r.user_id: r for r in receivers}

    @staticmethod
    async def create(
            db: Database,
            form: models.NoticeReceiverForm
    ) -> models.NoticeReceiver:
        return NoticeReceiver._parse(
            await db_tools.create(
                db, table=DBTables.notice_receiver,
                form=form
            )
        )

    @staticmethod
    async def update_notice_receiver(
            db: Database, pk: int,
            app_token: Union[str, None, UnInitedData] = UnInitedData(),
            platform: Union[AppPlatform, None, UnInitedData] = UnInitedData(),
    ) -> models.NoticeReceiver:
        data = {
            k: v for k, v in zip(
                ['app_token', 'platform'],
                [app_token, platform]
            ) if type(v) is not UnInitedData
        }

        up_str = ', '.join([f"{k} = :{k}" for k in data.keys()])
        if data["app_token"]:
            up_str = up_str + ", token_update_time = now()"

        sql = f"""
                    UPDATE {DBTables.notice_receiver} SET
                        {up_str}
                    WHERE id=:id 
                    RETURNING *                
        """

        res = await db.fetch_one(sql, data | {"id": pk})

        return NoticeReceiver._parse(res, return_none=False)


class News:
    @staticmethod
    def _parse(
            record: Record,
            return_none: bool = False
    ) -> models.News | None:
        if record:
            return models.News.parse_obj(record._mapping)
        else:
            if return_none:
                return None
            else:
                raise NewsDoesNotExist()

    @staticmethod
    async def get(
            db: Database,
            pk: int,
            return_none: bool = False
    ) -> models.News:
        sql = f"SELECT * FROM {DBTables.news} WHERE id = :id"
        record = await db.fetch_one(sql, {'id': pk})

        return News._parse(record, return_none)

    @staticmethod
    async def get_list(
            db: Database,
            page_size: int = 20,
            page_number: int = 1,
            after: datetime.datetime = None,
            before: datetime.datetime = None
    ) -> models.NewsList:
        limit, offset = db_tools.calc_limit_offset(page_size, page_number)

        after = after or datetime.datetime(1970, 1, 1)
        before = before or datetime.datetime(2222, 1, 1)

        values = {
            'offset': offset,
            'after': after,
            'before': before
        }

        if limit:
            values['limit'] = limit
        ph_limit = " LIMIT :limit " if limit else ""

        sql = f"SELECT *, count(*) over () as _total_count  FROM {DBTables.news} " \
              f"WHERE ctime > :after AND ctime < :before ORDER BY ctime DESC {ph_limit} OFFSET :offset"

        records = await db.fetch_all(sql, values)

        total_count = 0
        if records:
            total_count = records[0]._mapping['_total_count']

        news = [News._parse(x) for x in records]

        return models.NewsList(
            news=news,
            pagination=Pagination(
                total_items=total_count,
                page_size=page_size,
                page_number=page_number,
                total_pages=db_tools.calc_total_pages(total_count, page_size)
            )
        )

    @staticmethod
    async def create(
            db: Database,
            form: models.NewsForm
    ) -> models.News:
        return News._parse(
            await db_tools.create(
                db, table=DBTables.news,
                form=form,
                exclude_unset=True,
                exclude_none=True
            )
        )


class Notification:
    @staticmethod
    def _parse(
            record: Record,
            return_none: bool = False
    ) -> models.Notification | None:
        if record:
            return models.Notification.parse_obj(record._mapping)
        else:
            if return_none:
                return None
            else:
                raise NotificationDoesNotExist()

    @staticmethod
    async def get(
            db: Database,
            pk: int,
            assert_receiver_id: int = None,
            return_none: bool = False
    ) -> models.Notification:
        sql = f"SELECT * FROM {DBTables.notification} WHERE id = :id"
        record = await db.fetch_one(sql, {'id': pk})

        notification = Notification._parse(record, return_none)

        if assert_receiver_id and notification.receiver_id != assert_receiver_id:
            raise NotificationAccessDenied()

        return notification

    @staticmethod
    async def mark_viewed(
            db: Database,
            pk: int,
            viewed: bool
    ) -> models.Notification:
        sql = f"UPDATE {DBTables.notification} SET viewed = :viewed WHERE id = :id RETURNING *"
        record = await db.fetch_one(sql, {'id': pk, 'viewed': viewed})
        return Notification._parse(record)

    @staticmethod
    async def check_list_access(
            db: Database,
            pks: list[int],
            receiver_id: int
    ):
        sql = f"SELECT * FROM {DBTables.notification} WHERE id IN {db_tools.to_int_list_for_in(pks)}"
        records = await db.fetch_all(sql)

        notifications = [Notification._parse(x) for x in records]

        if len(notifications) != len(pks):
            raise NotificationDoesNotExist()

        for notification in notifications:
            if notification.receiver_id != receiver_id:
                raise NotificationAccessDenied()

    @staticmethod
    async def mark_viewed_list(
            db: Database,
            pks: list[int],
            viewed: bool
    ):
        sql = f"UPDATE {DBTables.notification} SET viewed = :viewed WHERE id IN {db_tools.to_int_list_for_in(pks)}"
        await db.fetch_all(sql, {'viewed': viewed})

    @staticmethod
    async def get_list(
            db: Database,
            receiver_id: int,
            page_size: int = 20,
            page_number: int = 1,
            after: datetime.datetime = None,
            before: datetime.datetime = None,
            viewed: Optional[bool] = None,
            assert_receiver_id: bool = False
    ) -> models.NotificationList:
        limit, offset = db_tools.calc_limit_offset(page_size, page_number)

        values = {
            'limit': limit,
            'offset': offset,
            'receiver_id': receiver_id
        }
        values.update({'after': after}) if after else None
        values.update({'before': before}) if before else None
        ph_viewed = ''
        if isinstance(viewed, bool):
            ph_viewed = ' AND viewed = :viewed '
            values['viewed'] = viewed

        sql = f"SELECT *, count(*) over () as _total_count FROM {DBTables.notification} " \
              f"WHERE receiver_id = :receiver_id {ph_viewed} " \
              + (" AND ctime > :after " if after else "") \
              + (" AND ctime < :before " if before else "") \
              + f"ORDER BY ctime DESC LIMIT :limit OFFSET :offset "

        records = await db.fetch_all(sql, values)

        total_count = 0
        if records:
            total_count = records[0]._mapping['_total_count']

        notifications = [Notification._parse(x) for x in records]

        return models.NotificationList(
            notifications=notifications,
            pagination=Pagination(
                total_items=total_count,
                total_pages=db_tools.calc_total_pages(total_count, page_size),
                page_size=page_size,
                page_number=page_number
            )
        )

    @staticmethod
    async def create(
            db: Database,
            form: models.NotificationForm
    ) -> models.Notification:
        try:
            return Notification._parse(
                await db_tools.create(
                    db, table=DBTables.notification,
                    form=form,
                    exclude_unset=True,
                    exclude_none=True
                )
            )
        except asyncpg.ForeignKeyViolationError as exc:
            if 'fk_receiver_id' in str(exc):
                raise WrongReceiverID()

    @staticmethod
    async def create_multicast(
            db: Database,
            form: models.NotificationMulticastForm
    ) -> list[models.Notification]:
        try:
            return [
                Notification._parse(x)
                for x in await db_tools.create_many(
                    db, table=DBTables.notification,
                    forms=[models.NotificationForm(**form.dict(), receiver_id=x) for x in form.receivers_ids],
                    exclude_unset=True,
                    exclude_none=True
                )
            ]
        except asyncpg.ForeignKeyViolationError as exc:
            if 'fk_receiver_id' in str(exc):
                raise WrongReceiverID()


class BulkNotification:
    _sql_template = f"""
        WITH {{with_clause}}
        courier_view AS (
            SELECT c.user_id,
                   pi.name,
                   pi.surname,
                   pi.middle_name,
                   to_json((array_agg(p.*))[1]) AS avatar
            FROM {DBTables.courier} c
                     LEFT JOIN {DBTables.person_info} pi ON pi.id = c.person_id
                     LEFT JOIN {DBTables.photos} p ON p.id = c.avatar
            WHERE c.user_id = ANY (
                SELECT DISTINCT unnest(bulk.receiver_ids)
                FROM {{bulk_notification_table}} bulk
                WHERE bulk.receiver_group_id = {GROUP_COURIER}
                  AND NOT bulk.to_all
            )
            GROUP BY c.id, pi.name, pi.surname, pi.middle_name
        )
        SELECT bulk.*,
               to_json((array_agg(coop.*))[1]) AS cooperator,
               CASE
                   WHEN NOT bulk.to_all AND bulk.receiver_group_id = {GROUP_CUSTOMER}
                       THEN to_json(array_agg(cust.*))
                   WHEN NOT bulk.to_all AND bulk.receiver_group_id = {GROUP_COURIER}
                       THEN to_json(array_agg(cour.*))
                   ELSE NULL END               AS receivers,
               count(bulk.id) OVER ()          AS _total_count
        FROM {{bulk_notification_table}} bulk
                 LEFT JOIN {DBTables.cooperator} coop ON bulk.cooperator_id = coop.id
                 LEFT JOIN {DBTables.customer} cust ON cust.user_id = ANY (bulk.receiver_ids)
                 LEFT JOIN courier_view cour ON cour.user_id = ANY (bulk.receiver_ids)
        WHERE {{where_clause}}
        GROUP BY bulk.id, bulk.cooperator_id, bulk.ctime, bulk.title, bulk.subtitle, bulk.description, bulk.receiver_group_id,
                 bulk.receiver_ids, bulk.to_all
        ORDER BY bulk.ctime DESC
        {{limit_clause}}
        {{offset_clause}}
    """

    @staticmethod
    def _parse(
            record: Record,
            return_none: bool = False,
    ) -> models.BulkNotification | None:
        if record:
            data = dict(record._mapping)
            data["cooperator"] = json.loads(data["cooperator"])
            data["receivers"] = json.loads(data["receivers"]) if data["receivers"] is not None else None
            return models.BulkNotification.parse_obj(data)
        else:
            if return_none:
                return None
            else:
                raise BulkNotificationDoesNotExist()

    @staticmethod
    async def get(
            db: Database,
            receiver_group_id: int,
            pk: int,
            return_none: bool = False,
    ) -> models.BulkNotification | None:
        sql = BulkNotification._sql_template.format(
            bulk_notification_table=DBTables.bulk_notification,
            with_clause="",
            where_clause="bulk.id = :id AND bulk.receiver_group_id = :receiver_group_id",
            limit_clause="",
            offset_clause="",
        )
        record = await db.fetch_one(sql, {"id": pk, "receiver_group_id": receiver_group_id})
        return BulkNotification._parse(record, return_none)

    @staticmethod
    async def get_list(
            db: Database,
            receiver_group_id: int,
            search: str | None = None,
            receiver_user_id: int | None = None,
            date_from: datetime.date | None = None,
            date_to: datetime.date | None = None,
            page_size: int = 20,
            page_number: int = 1,
    ) -> models.BulkNotificationList:
        where_clause = "bulk.receiver_group_id = :receiver_group_id"
        values = {"receiver_group_id": receiver_group_id}

        if search is not None:
            where_clause += f"""\nAND (
                   position(lower(:search) IN lower(bulk.title)) > 0
                OR position(lower(:search) IN lower(bulk.subtitle)) > 0
                OR position(lower(:search) IN lower(bulk.description)) > 0
                OR position(lower(:search) IN lower(coop.name)) > 0
                OR position(lower(:search) IN lower(coop.surname)) > 0
                OR NOT bulk.to_all AND position(lower(:search) IN lower(cust.name)) > 0
                OR NOT bulk.to_all AND position(lower(:search) IN lower(cust.surname)) > 0
                OR NOT bulk.to_all AND position(lower(:search) IN lower(cust.middle_name)) > 0
                OR NOT bulk.to_all AND position(lower(:search) IN lower(cour.name)) > 0
                OR NOT bulk.to_all AND position(lower(:search) IN lower(cour.surname)) > 0
                OR NOT bulk.to_all AND position(lower(:search) IN lower(cour.middle_name)) > 0
                OR bulk.to_all AND bulk.receiver_group_id = {GROUP_CUSTOMER} AND position(lower(:search) IN 'all customers') > 0
                OR bulk.to_all AND bulk.receiver_group_id = {GROUP_COURIER} AND position(lower(:search) IN 'all drivers') > 0
            )"""
            values["search"] = search
        if receiver_user_id is not None:
            where_clause += "\nAND :receiver_user_id = ANY (bulk.receiver_ids)"
            values["receiver_user_id"] = receiver_user_id
        if date_from is not None:
            where_clause += "\nAND date(bulk.ctime) >= :date_from"
            values["date_from"] = date_from
        if date_to is not None:
            where_clause += "\nAND date(bulk.ctime) <= :date_to"
            values["date_to"] = date_to

        limit, offset = db_tools.calc_limit_offset(page_size, page_number)
        values["offset"] = offset
        if limit:
            values["limit"] = limit

        sql = BulkNotification._sql_template.format(
            bulk_notification_table=DBTables.bulk_notification,
            with_clause="",
            where_clause=where_clause,
            limit_clause="LIMIT :limit" if limit else "",
            offset_clause="OFFSET :offset",
        )

        records = await db.fetch_all(sql, values)

        total_count = 0
        if records:
            total_count = records[0]._mapping["_total_count"]

        bulk_notifications = [BulkNotification._parse(x) for x in records]

        return models.BulkNotificationList(
            pagination=Pagination(
                total_items=total_count,
                page_size=page_size,
                page_number=page_number,
                total_pages=db_tools.calc_total_pages(total_count, page_size),
            ),
            bulk_notifications=bulk_notifications,
        )

    @staticmethod
    async def create(
            db: Database,
            form: models.BulkNotificationDBForm,
    ) -> models.BulkNotification:
        data = form.dict(exclude_unset=True, exclude_none=True)
        key_ph = db_tools.gen_key_holders(data)
        values_ph = db_tools.gen_value_holders(data)
        sql = BulkNotification._sql_template.format(
            bulk_notification_table="bulk_inserted_view",
            with_clause=f"""
                bulk_inserted_view AS
                (
                    INSERT INTO {DBTables.bulk_notification} {key_ph}
                    VALUES {values_ph}
                    RETURNING *
                ),
            """,
            where_clause="TRUE",
            limit_clause="",
            offset_clause="",
        )
        record = await db.fetch_one(sql, data)
        return BulkNotification._parse(record)
