"""Read a local character object only when explicitly requested."""
import json
from pathlib import Path
from backend.errors import AppError


def load_personality(path):
    try:
        with Path(path).open(encoding='utf-8') as file:
            value = json.load(file)
        if not isinstance(value, dict):
            raise ValueError
        return value
    except (OSError, ValueError, UnicodeError):
        raise AppError('personality_unavailable') from None
