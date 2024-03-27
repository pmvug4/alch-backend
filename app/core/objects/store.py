from pydantic import BaseModel
from typing import Optional, Type
from databases.core import Record, Database, Connection

from core.exceptions.exception import AppHTTPException


class ObjectStore:
    _table: str
    _model: Type[BaseModel]
    _not_found: Type[AppHTTPException]

    @classmethod
    def _record_to_model(
            cls,
            record: Record
    ) -> '_model':
        return cls._model(**record._mapping)

    @classmethod
    def _parse(
            cls,
            record: Record | None,
            return_none: bool = False
    ) -> Optional['_model']:
        if record is None:
            if return_none:
                return None
            else:
                raise cls._not_found
        else:
            return cls._record_to_model(record)

    def __init__(
            self,
            conn: Database | Connection
    ):
        self.conn: Database | Connection = conn
