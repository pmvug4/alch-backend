from pydantic import BaseModel
from typing import Optional, Type
from databases.core import Record, Database, Connection
from uuid import UUID

from core.db import tools as db_tools
from core.exceptions.exception import AppHTTPException


class ObjectStore[
    Model: BaseModel,
    ModelCreateForm: BaseModel,
    ModelUpdateForm: BaseModel,
    NotFoundError: AppHTTPException | Exception
]:
    _table: str

    _model: Type[Model]
    _model_create_form: Type[ModelCreateForm]
    _model_update_form: Optional[Type[ModelUpdateForm]] = None

    _not_found: Type[NotFoundError]

    @classmethod
    def _record_to_model(
            cls,
            record: Record
    ) -> Model:
        return cls._model.model_validate(db_tools.get_data(record))

    @classmethod
    def _parse(
            cls,
            record: Record | None,
            return_none: bool = False
    ) -> Optional[Model]:
        if record is None:
            if return_none:
                return None
            else:
                raise cls._not_found
        else:
            return cls._record_to_model(record)

    def __init__(
            self,
            conn: Connection | Database
    ):
        self.conn: Connection | Database = conn

    async def create(
            self,
            form: ModelCreateForm
    ) -> Model:
        return self._parse(
            await db_tools.create(
                self.conn,
                table=self._table,
                form=form
            ),
            return_none=False
        )

    async def get(
            self,
            pk_value: int | str | UUID,
            pk_field: str = 'id',
            for_update: bool = False,
            return_none: bool = False,
            return_deleted: bool = False,
    ) -> Optional[Model]:
        return self._parse(
            await db_tools.get(
                self.conn,
                table=self._table,
                pk_field=pk_field,
                pk_value=pk_value,
                for_update=for_update,
                return_deleted=return_deleted
            ),
            return_none=return_none
        )

    async def update(
            self,
            pk: int,
            form: ModelUpdateForm
    ) -> Model:
        if self._model_update_form is None:
            raise NotImplementedError

        return self._parse(
            await db_tools.update_by_id(
                self.conn,
                table=self._table,
                pk_value=pk,
                data=form.model_dump()
            )
        )

    async def delete(
            self,
            pk: int
    ) -> Model:
        return self._parse(
            await db_tools.delete_by_id(
                self.conn,
                table=self._table,
                pk_value=pk,
            )
        )

#
# class ObjectListStore[
#     Model: BaseModel
# ]:
#     _table: str
#
#     _model: Type[Model]
#
#     @classmethod
#     def _record_to_model(
#             cls,
#             record: Record
#     ) -> Model:
#         return db_tools.record_to_model(
#             model_cls=cls._model,
#             record=record
#         )
#
#     @classmethod
#     def _parse_list(
#             cls,
#             records: list[Record],
#             return_none: bool = False
#     ) -> PaginationSchema[Model]:
#         return [
#             cls._record_to_model(r)
#             for r in records
#         ]
#
#     def __init__(
#             self,
#             conn: Connection
#     ):
#         self.conn: Connection = conn
#
#     async def get(self) -> PaginationSchema[Model]:
#         await db_tools.get_list(
#             conn=self.conn
#         )
