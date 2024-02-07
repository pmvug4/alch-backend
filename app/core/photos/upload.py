import os.path
from io import BytesIO
from uuid import uuid4

from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile
from starlette.concurrency import run_in_threadpool

from core.gcs import public_bucket, private_bucket
from .exceptions import UnexpectedPhotoExtension
from .models import PhotoType


async def upload_photo(
        file: UploadFile,
        type: PhotoType,
        is_private: bool = False,
        prefix: str = ''
) -> (int, str, str):
    try:
        ext = _get_extension(file.content_type, file.filename)

        orig_size, img_buffer = await _read_to_buffer(file=file)
        destination = _get_destination_no_ext(file=file, type=type, prefix=prefix)

        (orig_img, thumb_img) = await run_in_threadpool(
            _handle_image,
            ext=ext,
            img_buffer=img_buffer,
            shrink=False,
            make_thumbnail=True
        )

        url = await _push_to_gcs(
            destination=destination + f'.{ext}',
            img=orig_img,
            is_private=is_private
        )

        thumb_url = await _push_to_gcs(
            destination=destination + f'_thumb.{ext}',
            img=thumb_img,
            is_private=is_private
        )

        return orig_size, url, thumb_url
    except UnidentifiedImageError:
        raise UnexpectedPhotoExtension


async def _push_to_gcs(
        destination: str,
        img: BytesIO,
        is_private: bool
) -> str:
    img.seek(0)

    if is_private:
        bucket = private_bucket
    else:
        bucket = public_bucket

    return await bucket.upload_blob(
        destination,
        data=img.read()
    )


def _get_extension(content_type: str, filename: str) -> str:
    ext: str

    match content_type:
        case "image/png":
            ext = "png"
        case "image/jpeg":
            ext = "jpg"
        case "image/svg+xml":
            ext = "svg"
        case "image/webp":
            ext = "webp"
        case _:
            _, ext = os.path.splitext(filename)

    if not ext:
        raise UnexpectedPhotoExtension

    return ext


def _handle_image(
        img_buffer: bytes,
        ext: str,
        shrink: bool = True,
        make_thumbnail: bool = False
) -> (BytesIO, BytesIO | None):
    orig_save_img = BytesIO()
    thumb_save_img = BytesIO()
    orig_save_img.name = f'temp.{ext}'
    thumb_save_img.name = f'temp.{ext}'

    _jpeg_cri_bytes = 3 / 8
    _thumbnail_high_size = 512
    _4mb = 4 * 1024 * 1024

    img = Image.open(BytesIO(img_buffer))
    img = img.convert('RGB')
    exif = img.info.get('exif', b'')

    if shrink:
        area = img.height * img.width
        cri_bytes = _jpeg_cri_bytes
        scale = min(
            (_4mb / (area * cri_bytes)) ** 0.5,
            1
        )
        img.thumbnail((int(scale * img.height), int(scale * img.width)), Image.ANTIALIAS)

    img.save(orig_save_img, exif=exif)

    if make_thumbnail:
        scale = min([*[_thumbnail_high_size / s for s in img.size], 1])
        img.thumbnail((int(scale * img.height), int(scale * img.width)), Image.ANTIALIAS)
        img.save(thumb_save_img, exif=exif)

        return orig_save_img, thumb_save_img

    return orig_save_img, None


async def _read_to_buffer(
        file: UploadFile
) -> (int, bytes):
    chunk = 2048
    ready = 0
    data = bytes()

    while True:
        buffer = await file.read(chunk)
        data += buffer
        ready += len(buffer)
        if not buffer:
            break

    return ready, data


def _get_destination_no_ext(
        file: UploadFile,
        type: PhotoType,
        prefix: str = ''
) -> str:
    directory = f"/static/photos/{type}/{prefix}"
    return f"{directory}{uuid4()}"
