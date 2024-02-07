import datetime
from enum import Enum

import pytz
from pydantic import BaseModel, constr, root_validator


class FormattedDict:
    def __init__(self, dictionary: dict[..., str | None]):
        self._dict = dictionary

    def format(self, **kwargs) -> dict:
        return {k: (v.format(**kwargs) if isinstance(v, str) else v) for k, v in self._dict.items()}


class GeographyPoint(BaseModel):
    lat: float
    lon: float

    def to_tuple(self) -> tuple:
        return (self.lat, self.lon)


class Pagination(BaseModel):
    total_items: int
    total_pages: int
    page_number: int
    page_size: int


phone_regex = r"^\d{10,15}$"
phone_type = constr(regex=phone_regex)

ssn_type = constr(regex=r"\d{3}-\d{2}-\d{4}")
restrict_ssn_type = constr(regex=r"XXX-XX-XXXX")


class FilterTime(BaseModel):
    from_time: datetime.datetime = None
    to_time: datetime.datetime = None

    @root_validator(skip_on_failure=True)
    def _check_tz(cls, values: dict):
        from_time: datetime.datetime = values['from_time']
        to_time: datetime.datetime = values['to_time']

        if from_time:
            if from_time.tzinfo is None:
                values['from_time'] = from_time.replace(tzinfo=pytz.UTC) + datetime.timedelta(hours=7)
                # raise ValueError("Times must be with tzinfo")
        if to_time:
            if to_time.tzinfo is None:
                values['to_time'] = to_time.replace(tzinfo=pytz.UTC) + datetime.timedelta(hours=7)
                # raise ValueError("Times must be with tzinfo")

        if from_time and to_time:
            if from_time.tzinfo != to_time.tzinfo:
                raise ValueError("Tzinfos must be the same")

        return values

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
