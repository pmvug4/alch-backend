import asyncio
import datetime

from databases import Database

from core import gcs
from core.config.gcs import gcs_settings
from .models import PrivatePhotoInfo
from ..models import Photo


async def refresh_private_photo_info(
        db: Database,
        photo_id: int,
        orig_url: str,
        thumb_url: str
) -> PrivatePhotoInfo:
    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=gcs_settings.PHOTO_CACHE_DAYS)

    return await PrivatePhotoInfo(
        photo_id=photo_id,
        orig_url=await gcs.private_bucket.get_public_url(
            path=orig_url,
            expiration=expiration
        ),
        thumb_url=await gcs.private_bucket.get_public_url(
            path=thumb_url,
            expiration=expiration
        ),
        expiration=expiration
    ).db_save(db)


async def get_private_photo_info(
        db: Database,
        photo_id: int,
        orig_url: str,
        thumb_url: str,
) -> PrivatePhotoInfo:
    data = await PrivatePhotoInfo.db_get(
        db, photo_id=photo_id,
        return_none=True
    )

    if data is None or data.expiration < datetime.datetime.utcnow() + datetime.timedelta(
            minutes=gcs_settings.PHOTO_REALTIME_RECACHE_MINUTES):
        return await refresh_private_photo_info(
            db, photo_id=photo_id,
            orig_url=orig_url,
            thumb_url=thumb_url
        )
    elif data.expiration < datetime.datetime.utcnow() + datetime.timedelta(
            hours=gcs_settings.PHOTO_BACKGROUND_RECACHE_HOURS):
        asyncio.get_event_loop().create_task(  # noqa
            refresh_private_photo_info(
                db, photo_id=photo_id,
                orig_url=orig_url,
                thumb_url=thumb_url
            )
        )
        return data
    else:
        return data


async def refresh_private_photo_info_list(
        db: Database,
        photos: list[Photo],
) -> list[PrivatePhotoInfo]:
    if not photos:
        return []

    expiration = datetime.datetime.utcnow() + datetime.timedelta(days=gcs_settings.PHOTO_CACHE_DAYS)

    return await PrivatePhotoInfo.db_save_list(
        db,
        private_photo_info_list=[
            PrivatePhotoInfo(
                photo_id=photo.id,
                orig_url=await gcs.private_bucket.get_public_url(
                    path=photo.orig_url,
                    expiration=expiration,
                ),
                thumb_url=await gcs.private_bucket.get_public_url(
                    path=photo.thumb_url,
                    expiration=expiration,
                ),
                expiration=expiration,
            ) for photo in photos
        ]
    )


async def get_private_photo_info_list(
        db: Database,
        photos: list[Photo],
) -> list[PrivatePhotoInfo]:
    if not photos:
        return []

    cached_private_photos = await PrivatePhotoInfo.db_get_list(db, photo_ids=[photo.id for photo in photos])
    cached_private_photos_dict = {private_photo.photo_id: private_photo for private_photo in cached_private_photos}

    fresh_private_photos = []
    photos_to_refresh_realtime = []
    photos_to_refresh_background = []

    for photo in photos:
        private_photo = cached_private_photos_dict.get(photo.id)

        if private_photo is None or private_photo.expiration < datetime.datetime.utcnow() + datetime.timedelta(
                minutes=gcs_settings.PHOTO_REALTIME_RECACHE_MINUTES):
            photos_to_refresh_realtime.append(photo)
        elif private_photo.expiration < datetime.datetime.utcnow() + datetime.timedelta(
                hours=gcs_settings.PHOTO_BACKGROUND_RECACHE_HOURS):
            photos_to_refresh_background.append(photo)
            fresh_private_photos.append(private_photo)
        else:
            fresh_private_photos.append(private_photo)

    refreshed_private_photos = await refresh_private_photo_info_list(db, photos_to_refresh_realtime)
    asyncio.get_event_loop().create_task(  # noqa
        refresh_private_photo_info_list(db, photos_to_refresh_background)
    )

    return fresh_private_photos + refreshed_private_photos
