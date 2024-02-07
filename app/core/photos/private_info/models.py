import datetime
from typing import Optional

from asyncpg import Record
from databases import Database
from pydantic import BaseModel

from core.db import tools as db_tools
from core.db.tables import DBTables
from .exceptions import PrivatePhotoInfoDoesNotExist

TABLE = DBTables.private_photos


class PrivatePhotoInfo(BaseModel):
    photo_id: int
    orig_url: str
    thumb_url: str
    expiration: datetime.datetime

    @classmethod
    def _parse(
            cls,
            record: Record | dict | str,
            return_none: bool = False
    ) -> Optional['PrivatePhotoInfo']:
        if record:
            return PrivatePhotoInfo.parse_obj(db_tools.get_data(record))
        else:
            if return_none:
                return None
            else:
                raise PrivatePhotoInfoDoesNotExist

    @classmethod
    async def db_get(
            cls,
            db: Database,
            photo_id: int,
            return_none: bool = False,
            for_update: bool = False
    ) -> Optional['PrivatePhotoInfo']:
        return cls._parse(
            await db_tools.get(
                db, table=TABLE,
                pk_value=photo_id,
                pk_field='photo_id',
                for_update=for_update
            ),
            return_none=return_none
        )

    async def db_save(self, db: Database) -> 'PrivatePhotoInfo':
        data = self.dict()
        _data_temp = data.copy()
        _data_temp.pop('photo_id')

        key_ph = db_tools.gen_key_holders(data)
        values_ph = db_tools.gen_value_holders(data)
        update_ph = db_tools.gen_update_holders(_data_temp)

        sql = f"INSERT INTO {TABLE} {key_ph} VALUES {values_ph} " \
              f"ON CONFLICT (photo_id) DO UPDATE SET {update_ph} " \
              f"RETURNING *"
        record = await db.fetch_one(sql, data)
        self._parse(record, return_none=False)

        return self

    @classmethod
    async def db_get_list(
            cls,
            db: Database,
            photo_ids: list[int],
            for_update: bool = False,
    ) -> list["PrivatePhotoInfo"]:
        return [
            cls._parse(record)
            for record in await db_tools.get_for_list(
                db,
                table=TABLE,
                filters=f"photo_id IN {db_tools.to_int_list_for_in(photo_ids)}",
                ending=db_tools.for_update(for_update),
                data={},
                returning="*",
            )
        ]

    @classmethod
    async def db_save_list(
            cls,
            db: Database,
            private_photo_info_list: list["PrivatePhotoInfo"],
    ) -> list["PrivatePhotoInfo"]:
        data_list = [private_photo.dict() for private_photo in private_photo_info_list]

        update_keys = [k for k in data_list[0].keys() if k != "photo_id"]

        key_ph = db_tools.gen_key_holders(data_list[0])
        values_ph = ",".join([db_tools.gen_value_holders(data, suffix=f"_{i}") for i, data in enumerate(data_list)])
        update_ph = f"({','.join(update_keys)}) = ({','.join(['EXCLUDED.' + k for k in update_keys])})"

        sql = f"INSERT INTO {TABLE} {key_ph} VALUES {values_ph} " \
              f"ON CONFLICT (photo_id) DO UPDATE SET {update_ph} " \
              f"RETURNING *"

        values = {}
        for i, data in enumerate(data_list):
            for key, value in data.items():
                values[key + f"_{i}"] = value

        records = await db.fetch_all(sql, values)

        return [cls._parse(record) for record in records]
