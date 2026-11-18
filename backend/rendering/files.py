"""Open configured private directories without traversing symlinks."""
from contextlib import contextmanager
import os
from pathlib import Path
import stat


@contextmanager
def directory(path):
    parts = Path(path).parts
    if not parts or parts[0] != '/' or '..' in parts:
        raise ValueError
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open('/', flags)
    try:
        for part in parts[1:]:
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


@contextmanager
def readable(root, parts):
    with directory(Path(root).joinpath(*parts[:-1])) as parent:
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=parent)
        with os.fdopen(fd, 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise ValueError
            yield stream
