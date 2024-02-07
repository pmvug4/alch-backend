from typing import Any, Iterable, Sequence

from databases import Database
from databases.interfaces import Record

from core import gcs
from core.db import tools as db_tools
from core.db.tables import DBTables
from .exceptions import *
from .models import *
from .private_info.services import get_private_photo_info, get_private_photo_info_list


def _parse_photo(
        record: Record,
        return_none: bool = False,
) -> Photo | None:
    if record:
        return Photo.parse_obj(record._mapping)
    else:
        if return_none:
            return None
        else:
            raise PhotoDoesNotExist


async def reveal_private_photo(
        db: Database,
        photo: Photo,
        forever: bool = False
) -> Photo:
    if photo.is_private:
        photo = photo.copy()

        if not forever:
            private_info = await get_private_photo_info(
                db, photo_id=photo.id,
                orig_url=photo.orig_url,
                thumb_url=photo.thumb_url
            )

            photo.apply_private_info(private_info)
        else:
            public_orig_url = await gcs.private_bucket.get_public_url(
                path=photo.orig_url,
                expiration=None
            )
            public_thumb_url = await gcs.private_bucket.get_public_url(
                path=photo.thumb_url,
                expiration=None
            )

            photo.apply_signed_info(
                orig_url=public_orig_url,
                thumb_url=public_thumb_url,
                expiration=None
            )

    return photo


async def reveal_private_photo_list(
        db: Database,
        photos: list[Photo],
        forever: bool = False,
) -> list[Photo]:
    if not forever:
        photos_to_get_private_info = [p for p in photos if p.is_private and not p.is_signed]
        private_photo_info_list = await get_private_photo_info_list(db, photos_to_get_private_info)
        private_photo_info_dict = {p.photo_id: p for p in private_photo_info_list}

        for photo in photos:
            if photo.id in private_photo_info_dict:
                photo.apply_private_info(private_photo_info_dict[photo.id])
    else:
        for photo in photos:
            public_orig_url = await gcs.private_bucket.get_public_url(
                path=photo.orig_url,
                expiration=None,
            )
            public_thumb_url = await gcs.private_bucket.get_public_url(
                path=photo.thumb_url,
                expiration=None,
            )

            photo.apply_signed_info(
                orig_url=public_orig_url,
                thumb_url=public_thumb_url,
                expiration=None
            )

    return photos


async def reveal_all_photos_for_object(
        db: Database,
        obj: Any,
) -> Any:
    photos_to_get_private_info = []

    def check_object(obj: Any) -> None:
        if type(obj) is Photo and obj.is_private and not obj.is_signed:
            photos_to_get_private_info.append(obj)
        elif isinstance(obj, Iterable) and not isinstance(obj, str):
            if isinstance(obj, Sequence):
                for v in obj.__iter__():
                    check_object(v)
            else:
                for k, v in obj.__iter__():
                    check_object(v)

    check_object(obj)

    private_photo_info_list = await get_private_photo_info_list(db, photos_to_get_private_info)
    private_photo_info_dict = {p.photo_id: p for p in private_photo_info_list}

    def update_object(obj: Any) -> None:
        if type(obj) is Photo and obj.id in private_photo_info_dict:
            obj.apply_private_info(private_photo_info_dict[obj.id])
        elif isinstance(obj, Iterable) and not isinstance(obj, str):
            if isinstance(obj, Sequence):
                for v in obj.__iter__():
                    update_object(v)
            else:
                for k, v in obj.__iter__():
                    update_object(v)

    update_object(obj)

    return obj


async def get_photo(
        db: Database,
        pk: int | Photo,
        return_none: bool = False,
        reveal_private: bool = True,
        reveal_forever: bool = False
) -> Photo | None:
    if pk is None and return_none:
        return None

    if isinstance(pk, Photo):
        pk = pk.id

    photo = _parse_photo(
        await db_tools.get(
            db, table=DBTables.photos,
            pk_value=pk
        )
    )

    if photo is not None and reveal_private:
        return await reveal_private_photo(db, photo=photo, forever=reveal_forever)
    else:
        return photo


async def delete_photo(
        db: Database,
        pk: int,
        reveal_private: bool = True
) -> Photo:
    photo: Photo = _parse_photo(
        await db_tools.update_by_id(
            db, table=DBTables.photos,
            pk=pk,
            data={'deleted': True},
            with_atime=False
        ),
        return_none=False
    )

    if reveal_private:
        return await reveal_private_photo(db, photo=photo)
    else:
        return photo


async def get_photo_list(
        db: Database,
        pks: list[int | Photo],
        reveal_private: bool = True,
        reveal_forever: bool = False
) -> list[Photo]:
    photo_list = []
    pks = [x.id if isinstance(x, Photo) else x for x in pks]

    if pks:
        sql = f"SELECT * FROM {DBTables.photos} WHERE id IN {db_tools.to_int_list_for_in(pks)} "
        for photo in [_parse_photo(x, return_none=False) for x in await db.fetch_all(sql)]:
            if photo is not None and reveal_private:
                photo_list.append(await reveal_private_photo(db, photo=photo, forever=reveal_forever))
            else:
                photo_list.append(photo)
    return photo_list


async def create_photo(
        db: Database,
        form: PhotoForm
) -> Photo:
    photo = _parse_photo(
        await db_tools.create(
            db, table=DBTables.photos,
            form=form,
            exclude={'id', 'deleted', 'expiration'}
        ),
        return_none=False
    )
    return await reveal_private_photo(db, photo=photo)


async def create_photos(
        db: Database,
        forms: list[PhotoForm]
) -> list[Photo]:
    return [
        _parse_photo(x) for x in await db_tools.create_many(
            db, table=DBTables.photos,
            forms=forms,
            exclude={'id', 'deleted', 'expiration'}
        )
    ]
