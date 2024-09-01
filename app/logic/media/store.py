import datetime
from typing import Optional
from uuid import UUID
from asyncpg import UniqueViolationError

from core.objects.store import ObjectStore
from core.db.tables import DBTables, DBIndexes

from .errors import MediaUniqueError, MediaNotFoundError
from .models import MediaForm, Media


class MediaStore(ObjectStore[
        Media,
        MediaForm,
        None,
        None,
        MediaNotFoundError,
    ]
):
    _table = DBTables.media

    _model = Media
    _model_create_form = MediaForm
    _model_put_form = None
    _model_patch_form = None

    _not_found = MediaNotFoundError

    async def create(
            self,
            form: MediaForm
    ) -> Media:
        try:
            return await super().create(form)
        except UniqueViolationError as e:
            if DBIndexes.ui_media in str(e):
                raise MediaUniqueError
