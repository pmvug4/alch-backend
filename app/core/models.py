import datetime
from enum import Enum

from pydantic import BaseModel, root_validator


class FormattedDict:
    def __init__(self, dictionary: dict[..., str | None]):
        self._dict = dictionary

    def format(self, **kwargs) -> dict:
        return {k: (v.format(**kwargs) if isinstance(v, str) else v) for k, v in self._dict.items()}


class Pagination(BaseModel):
    total_items: int
    total_pages: int
    page_number: int
    page_size: int


class FilterTime(BaseModel):
    from_time: datetime.datetime = None
    to_time: datetime.datetime = None

    @root_validator(skip_on_failure=True)
    def _convert_to_utc(cls, values: dict):
        if values['from_time']:
            values['from_time'] = values['from_time'].astimezone(tz=datetime.timezone.utc).replace(tzinfo=None)

        if values['to_time']:
            values['to_time'] = values['to_time'].astimezone(tz=datetime.timezone.utc).replace(tzinfo=None)

        return values

    def to_interval_tuple(self) -> tuple[datetime.datetime, datetime.datetime]:
        return self.from_time, self.to_time


class SortMethod(str, Enum):
    ASC = 'ASC'
    DESC = 'DESC'
