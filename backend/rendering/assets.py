"""Validate actual image bytes and publish them atomically under an opaque key."""
from hashlib import sha256
from io import BytesIO
import os
from uuid import uuid4

from PIL import Image

from backend.conversation_store import identifier
from backend.errors import AppError
from backend.rendering.comfyui_adapter import MAX_IMAGE
from backend.rendering.files import directory, readable

MEDIA_TYPES = {'PNG': 'image/png', 'JPEG': 'image/jpeg', 'WEBP': 'image/webp'}


def decode(data, media_type):
    if not 1 <= len(data) <= MAX_IMAGE or media_type not in MEDIA_TYPES.values():
        raise AppError('asset_invalid')
    try:
        with Image.open(BytesIO(data), formats=list(MEDIA_TYPES)) as image:
            width, height = image.size
            if (MEDIA_TYPES[image.format] != media_type or not (1 <= width <= 8192 and 1 <= height <= 8192)
                    or image.n_frames != 1):
                raise ValueError
            image.verify()
        with Image.open(BytesIO(data), formats=list(MEDIA_TYPES)) as image:
            image.load()
        return width, height
    except (OSError, SyntaxError, ValueError, Image.DecompressionBombError):
        raise AppError('asset_invalid') from None


class Assets:
    def __init__(self, root):
        self.root = root

    def ready(self):
        try:
            with directory(self.root) as fd:
                if not os.access(self.root, os.W_OK) or os.fstat(fd).st_mode & 0o077:
                    raise ValueError
        except (OSError, TypeError, ValueError):
            raise AppError('asset_unavailable') from None

    def save(self, data, media_type):
        width, height = decode(data, media_type)
        key = str(uuid4())
        self.ready()
        try:
            with directory(self.root) as parent:
                temporary = f'.{key}.tmp'
                try:
                    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o600, dir_fd=parent)
                    with os.fdopen(fd, 'wb') as stream:
                        stream.write(data)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.replace(temporary, key, src_dir_fd=parent, dst_dir_fd=parent)
                    os.fsync(parent)
                except OSError:
                    self._unlink(parent, temporary)
                    self._unlink(parent, key)
                    raise
        except (OSError, TypeError, ValueError):
            raise AppError('asset_unavailable') from None
        return key, media_type, len(data), width, height, sha256(data).hexdigest()

    @staticmethod
    def _unlink(parent, key):
        try:
            os.unlink(key, dir_fd=parent)
        except OSError:
            pass

    def discard(self, key):
        try:
            with directory(self.root) as parent:
                self._unlink(parent, identifier(key))
        except (OSError, TypeError, ValueError):
            pass

    def read(self, asset):
        try:
            with readable(self.root, [identifier(asset['id'])]) as stream:
                data = stream.read(MAX_IMAGE + 1)
            if len(data) != asset['bytes'] or sha256(data).hexdigest() != asset['checksum']:
                raise ValueError
            return data, asset['media_type']
        except (OSError, TypeError, ValueError):
            raise AppError('asset_unavailable') from None
