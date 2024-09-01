import datetime as dt
from pydantic import BaseModel, constr, Field
from uuid import UUID
from typing import Optional


class MediaType(BaseModel):
    id: int
    name: constr(max_length=31)


AvatarMediaType = MediaType(id=1, name='avatar')
ElementMediaType = MediaType(id=5, name='element')


class MediaForm(BaseModel):
    owner_uuid: Optional[UUID] = Field(None, description="UUID владельца медиа")
    type_id: int = Field(..., description="ID типа медиа")
    internal_path: constr(max_length=511) = Field(..., description="Внутренний путь до медиа")
    public_url: constr(max_length=511) = Field(..., description="Публичный url до медиа")


class Media(MediaForm):
    id: int
    uuid: UUID
    created_at: dt.datetime
    deleted_at: Optional[dt.datetime]
