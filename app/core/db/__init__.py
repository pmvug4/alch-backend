import asyncio
import time
import traceback
from functools import partial

from databases import Database
from loguru import logger

from core.common.singleton import SingletonMeta
from core.config.db_settings import db_settings, demo_db_settings, PLDBSettings
from core.config.telegram import telegram_settings
from core.telegram_notification.models import TelegramErrorMessage
from core.telegram_notification.task import send_telegram_message

MUTE_ALARM_QUERY_LIST = [
    """
            SELECT id, order_id, url, employee_id 
            FROM invoice
            WHERE true
         AND employee_id = :employee_id  AND order_id = :order_id """,
    "invoice (order_id,url,employee_id) VALUES (:order_id,:url,:employee_id) RETURNING *"
]


# seconds

class DatabaseWithLogging(Database):
    # todo rewrite with decorators

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def _process_treshold_alarm(self, func_name, exec_time, query):
        if query not in MUTE_ALARM_QUERY_LIST:
            logger.warning(f"[Database] ({func_name}) long query execution {exec_time}sec {query}")
            loop = asyncio.get_event_loop()
            loop.create_task(  # noqa
                send_telegram_message(
                    TelegramErrorMessage(f"Long time SQL query execution {exec_time}sec: {query}"),
                    telegram_settings.ALARM_GROUP_ID
                )
            )

    async def fetch_all(self, *args, **kwargs):
        start_time = time.monotonic()
        try:
            return await super().fetch_all(*args, **kwargs)
        except Exception:
            raise
        finally:
            exec_time = time.monotonic() - start_time

            if exec_time > db_settings.DB_ALARM_THRESHOLD:
                try:
                    query = args[0]
                except KeyError:
                    query = "Undef"
                await self._process_treshold_alarm("fetch_all", exec_time, query)
            elif db_settings.DB_LOG_EXEC_TIME:
                try:
                    query = args[0]
                except KeyError:
                    query = "Undef"
                logger.debug(f"[Database] (fetch_all)  {query} query execution {exec_time} sec")

    async def fetch_one(self, *args, **kwargs):
        start_time = time.monotonic()
        try:
            return await super().fetch_one(*args, **kwargs)
        except Exception:
            raise
        finally:
            exec_time = time.monotonic() - start_time
            if exec_time > db_settings.DB_ALARM_THRESHOLD:
                try:
                    query = args[0]
                except KeyError:
                    query = "Undef"
                await self._process_treshold_alarm("fetch_one", exec_time, query)
            elif db_settings.DB_LOG_EXEC_TIME:
                try:
                    query = args[0]
                except KeyError:
                    query = "Undef"
                logger.debug(f"[Database] (fetch_one)  {query} query execution {exec_time} sec")

    async def execute(self, *args, **kwargs):
        start_time = time.monotonic()
        try:
            return await super().execute(*args, **kwargs)
        except Exception:
            raise
        finally:
            exec_time = time.monotonic() - start_time
            if exec_time > db_settings.DB_ALARM_THRESHOLD:
                try:
                    query = args[0]
                except KeyError:
                    query = "Undef"
                await self._process_treshold_alarm("execute", exec_time, query)
            elif db_settings.DB_LOG_EXEC_TIME:
                try:
                    query = args[0]
                except KeyError:
                    query = "Undef"
                logger.debug(f"[Database] (execute)  {query} query execution {exec_time} sec")


db_class = DatabaseWithLogging


class _DBConnPool:
    # ABC. Implementation must set meta=Singleton
    _db_settings: PLDBSettings = NotImplemented
    db_conn = None

    async def init_db(self):
        try:
            logger.info(f"[{self.__class__.__name__}] (init_db) init db {self._db_settings.DB}...")
            db = partial(db_class,
                         self._db_settings.DATABASE_URL,
                         )

            if hasattr(db_settings, "MAX_CONNECTIONS") and hasattr(self._db_settings, "MIN_CONNECTIONS"):
                db = partial(db,
                             min_size=self._db_settings.MIN_CONNECTIONS,
                             max_size=self._db_settings.MAX_CONNECTIONS,
                             server_settings={'jit': 'off'},
                             max_inactive_connection_lifetime=0
                             )

            self.db_conn = db()
            await self.db_conn.connect()
            await self.init_extra_data_for_connection()
        except Exception as e:
            logger.error(
                f"[{self.__class__.__name__}] (init_db) database not available! Exception: {repr(e)}, {traceback.format_exc()}")
            raise

    async def init_extra_data_for_connection(self):
        # В связи с использованием пользовательских типов на стороне postgres первая загрузка занимает много времени
        # Для этого в каждом соединении выполнеяется один запрос который подтянет эти данные и они закешируются в соединении
        # Если будет открыто соединение более чем self._db_settings.MIN_CONNECTIONS это приведет к тому, что в этом соединении будет долгим первый запрос
        async def get_something():
            sql = "SELECT * from delivery_order LIMIT 1"
            data = await self.database.fetch_one(sql)
            from core.orders.store.orders import _parse_order
            order = _parse_order(data, True)
            logger.debug(f"get order: {order}")

        await asyncio.gather(*[get_something() for x in range(self._db_settings.MIN_CONNECTIONS)])

    async def get_db(self):
        if not self.db_conn:
            await self.init_db()
        return self.db_conn

    @property
    def database(self):
        return self.db_conn

    async def close_db(self):
        try:
            logger.info(f"[{self.__class__.__name__}] (close_db) Close pool...")
            await self.db_conn.disconnect()
        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] (close_db) Exception: {repr(e)}, {traceback.format_exc()}")
            raise


class DBConnPool(_DBConnPool, metaclass=SingletonMeta):
    _db_settings = db_settings


class DBDemoConnPool(_DBConnPool, metaclass=SingletonMeta):
    _db_settings = demo_db_settings


def get_main_db():
    try:
        db = DBConnPool().database
        yield db
    finally:
        pass


def get_demo_db():
    try:
        yield DBDemoConnPool().database
    finally:
        pass
