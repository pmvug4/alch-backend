import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from core.schemas import BaseFileOK
from .private_info.models import PrivatePhotoInfo


class PhotoType(str, Enum):
    signature = 'signature'
    document = 'document'
    avatar = 'avatar'
    car = 'car'
    order_customer = 'order_customer'
    order_courier = 'order_courier'
    draft = 'draft'
    any = 'any'


class PhotoForm(BaseModel):
    orig_url: Optional[str] = None
    thumb_url: Optional[str] = None
    type: PhotoType
    owner_id: int | None
    is_private: bool = False


class Photo(PhotoForm):
    id: int
    deleted: bool
    expiration: Optional[datetime.datetime]
    is_signed: bool = False

    def apply_private_info(
            self,
            private_photo_info: PrivatePhotoInfo
    ):
        self.apply_signed_info(
            orig_url=private_photo_info.orig_url,
            thumb_url=private_photo_info.thumb_url,
            expiration=private_photo_info.expiration,
        )

    def apply_signed_info(
            self,
            orig_url: str,
            thumb_url: str,
            expiration: Optional[datetime.datetime]
    ):
        self.orig_url = orig_url
        self.thumb_url = thumb_url
        self.expiration = expiration
        self.is_signed = True

    def get_data_for_diff(self) -> dict:
        return self.dict(include={'id', 'deleted', 'type'})


class UploadPhotoResponse(BaseFileOK):
    photo: Photo
