import uuid
from contextvars import ContextVar

from core.localization import Language


class AppRequest:
    _id: ContextVar[str] = ContextVar("request_id", default="--INTERNAL--")
    ip: ContextVar[str] = ContextVar("request_ip", default="--INTERNAL--")
    api_name: ContextVar[str] = ContextVar("request_api_name", default="--INTERNAL--")
    lang: ContextVar[str | Language] = ContextVar("request_lang", default=Language.en)

    @classmethod
    def gen_id(cls) -> None:
        cls._id.set(str(uuid.uuid4()))

    @classmethod
    @property
    def id(cls) -> str:
        return cls._id.get()
