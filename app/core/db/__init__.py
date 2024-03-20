import time
import traceback
from databases import Database
from databases.core import Connection
from loguru import logger

from core.common.singleton import SingletonMeta
from core.config.external import db_settings, telegram_settings
from core.config.internal import run_state_settings
from core.background import BackgroundTasks

from core.telegram.models import TelegramErrorMessage
from core.telegram.task import send_telegram_message


class DatabaseWithLogging(Database):
    @staticmethod
    def _process_exec_threshold(func_name: str):
        def _outer(func):
            async def wrap(
                    *args,
                    **kwargs
            ):
                if run_state_settings.TELEGRAM_DB_ALARM_EXEC_THRESHOLD:
                    start_time = time.monotonic()

                    try:
                        return await func(*args, **kwargs)
                    finally:
                        exec_time = time.monotonic() - start_time

                        if exec_time * 1000 > run_state_settings.TELEGRAM_DB_ALARM_EXEC_THRESHOLD_MS:
                            query = args[0]

                            logger.warning(f"[Database] ({func_name}) long query execution: {exec_time:.2f}s {query=}")

                            await BackgroundTasks.create(
                                send_telegram_message(
                                    TelegramErrorMessage(f"Long SQL execution {exec_time:.2f}s {query=}"),
                                    telegram_settings.ALARM_GROUP_ID
                                )
                            )
                else:
                    return await func(*args, **kwargs)

            return wrap

        return _outer

    @_process_exec_threshold('fetch_all')
    async def fetch_all(self, *args, **kwargs):
        return await super().fetch_all(*args, **kwargs)

    @_process_exec_threshold('fetch_one')
    async def fetch_one(self, *args, **kwargs):
        return await super().fetch_one(*args, **kwargs)

    @_process_exec_threshold('execute')
    async def execute(self, *args, **kwargs):
        return await super().execute(*args, **kwargs)


class DBConnPool(metaclass=SingletonMeta):
    _db_settings = db_settings
    db_conn = None

    async def init_db(self):
        try:
            logger.info(f"[{self.__class__.__name__}] (init_db) init db {self._db_settings.DB}...")

            self.db_conn = DatabaseWithLogging(
                url=self._db_settings.database_url,
                min_size=self._db_settings.MIN_CONNECTIONS,
                max_size=self._db_settings.MAX_CONNECTIONS,
                server_settings={'jit': 'off'},
                max_inactive_connection_lifetime=0
            )

            await self.db_conn.connect()
        except Exception as e:
            logger.error(
                f"[{self.__class__.__name__}] (init_db) database not available! "
                f"Exception: {repr(e)}, {traceback.format_exc()}"
            )
            raise

    async def get_conn(self) -> Connection:
        if self.db_conn is None:
            raise RuntimeError("Database is not configured yet!")

        async with self.db_conn.connection() as conn:
            yield conn

    async def close_db(self):
        try:
            logger.info(f"[{self.__class__.__name__}] (close_db) Close pool...")
            await self.db_conn.disconnect()
        except Exception as e:
            logger.error(
                f"[{self.__class__.__name__}] (close_db) "
                f"Exception: {repr(e)}, {traceback.format_exc()}"
            )
            raise


async def get_db() -> Connection:
    yield DBConnPool().get_conn()
