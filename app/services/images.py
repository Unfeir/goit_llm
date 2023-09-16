import hashlib
from typing import BinaryIO

import cloudinary
from cloudinary.uploader import upload

from conf.config import settings


class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    @classmethod
    def generate_avatar_name(cls, email: str, typ: str):
        image_name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]
        return f'{typ.upper()}-AVATARS/{image_name}'

    @classmethod
    def get_url_for_avatar(cls, public_id):
        src_url = cloudinary.CloudinaryImage(public_id).build_url()
        return src_url

    @classmethod
    def avatar_upload(cls, file: BinaryIO, typ: str, email: str, ):
        avatar_id = cls.generate_avatar_name(email, typ)
        cloudinary.uploader.upload(file, public_id=avatar_id, overwrite=True)
        return cls.get_url_for_avatar(avatar_id)
