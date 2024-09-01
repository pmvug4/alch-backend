from pydantic import BaseModel
from typing import Optional, Type
from databases.core import Record, Database, Connection
from uuid import UUID

from core.db import tools as db_tools
from core.exceptions.exception import AppHTTPException
from core.common.pagination import PaginationRequest, PaginatedObjects


class ObjectStore[
    Model: BaseModel,
    ModelCreateForm: BaseModel,
    ModelPutForm: BaseModel,
    ModelPatchForm: BaseModel,
    NotFoundError: AppHTTPException | Exception
]:
    _table: str

    _model: Type[Model]
    _model_create_form: Type[ModelCreateForm]
    _model_put_form: Optional[Type[ModelPutForm]] = None
    _model_patch_form: Optional[Type[ModelPatchForm]] = None

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

    async def put(
            self,
            pk: int,
            form: ModelPutForm
    ) -> Model:
        if self._model_put_form is None:
            raise NotImplementedError

        return self._parse(
            await db_tools.update_by_id(
                self.conn,
                table=self._table,
                pk_value=pk,
                data=form.model_dump()
            )
        )

    async def patch(
            self,
            pk: int,
            form: ModelPatchForm
    ) -> Model:
        if self._model_patch_form is None:
            raise NotImplementedError

        return self._parse(
            await db_tools.update_by_id(
                self.conn,
                table=self._table,
                pk_value=pk,
                data=form.model_dump(exclude_unset=True, exclude_defaults=True)
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


class ObjectFullStore[
    Model: BaseModel,
    NotFoundError: AppHTTPException | Exception
]:
    _table: str
    _returning: str
    _fetch_related: list[db_tools.FetchRelated]

    _model: Type[Model]
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
            records: list[Record],
            return_none: bool = False
    ) -> Optional[Model]:
        if not len(records):
            if return_none:
                return None
            else:
                raise cls._not_found
        else:
            return cls._record_to_model(records[0])

    @classmethod
    def _parse_list(
            cls,
            records: list[Record],
            pagination: Optional[PaginationRequest]
    ) -> PaginatedObjects[Type[Model]]:
        return PaginatedObjects[Type[Model]].build(
            items=[cls._record_to_model(r) for r in records],
            total_items=records[0]['_total_items'] if len(records) else 0,
            request=pagination
        )

    def __init__(
        self,
        conn: Connection | Database
    ):
        self.conn: Connection | Database = conn

    async def _get(
            self,
            pk_field: str,
            pk_value: int | str | UUID,
            return_deleted: bool = False,
            return_none: bool = False
    ) -> Optional[Model]:
        extra_filter = ''
        if not return_deleted:
            extra_filter += f" {self._table}.deleted_at IS NULL "

        return self._parse(
            await db_tools.get_list(
                db=self.conn,
                table=self._table,
                pk_value=pk_value,
                pk_field=pk_field,
                returning=self._returning,
                extra_filter=extra_filter,
                fetch_related=self._fetch_related
            ),
            return_none=return_none
        )

    async def _get_list(
            self,
            pk_field: Optional[str] = None,
            pk_value: Optional[list[int] | list[str] | list[UUID]] = None,
            return_deleted: bool = False,
            order_by: Optional[str] = None,
            pagination: Optional[PaginationRequest] = None
    ) -> PaginatedObjects[Type[Model]]:
        extra_filter = ''
        if not return_deleted:
            extra_filter += f" {self._table}.deleted_at IS NULL "

        return self._parse_list(
            await db_tools.get_list(
                db=self.conn,
                table=self._table,
                pk_value=pk_value,
                pk_field=pk_field,
                returning=self._returning,
                extra_filter=extra_filter,
                fetch_related=self._fetch_related,
                order_by=order_by,
                limit=pagination.limit if pagination is not None else None,
                offset=pagination.offset if pagination is not None else None,
            ),
            pagination=pagination
        )
