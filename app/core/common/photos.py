from enum import Enum


class PhotosUploadModes(str, Enum):
    license = "license"
    insurance = "insurance"
    myself = "myself"


class PhotosBaseNames(str, Enum):
    license_photos = "license_photos"
    insurance_photos = "insurance_photos"
    myself_photos = "myself_photos"


all_photos_upload_modes = {
    PhotosUploadModes.license: PhotosBaseNames.license_photos.value,
    PhotosUploadModes.insurance: PhotosBaseNames.insurance_photos.value,
    PhotosUploadModes.myself: PhotosBaseNames.myself_photos.value,
}