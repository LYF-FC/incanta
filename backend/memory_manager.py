"""Single-process, append-once JSON memory with atomic file replacement."""
import copy
from datetime import datetime
import json
import os
from pathlib import Path
import re
import tempfile
from backend.errors import AppError


def empty_memory():
    return {'timeline':[], 'milestones':{}, 'emotions':{}, 'beliefs':{},
            'desires':{}, 'reflections':[], 'adaptive_style':{}}


class MemoryManager:
    def __init__(self, character_name, data_dir):
        name = re.sub(r'[^a-z0-9_-]', '_', character_name.lower()) or 'character'
        self.memory_file = Path(data_dir) / f'{name}_memory.json'

    def check_storage(self):
        parent = self.memory_file.parent
        try:
            while not parent.exists():
                if parent.is_symlink():
                    raise OSError
                parent = parent.parent
            if not parent.is_dir() or not os.access(parent, os.W_OK | os.X_OK):
                raise OSError
            if self.memory_file.exists() and not os.access(self.memory_file, os.R_OK | os.W_OK):
                raise OSError
        except OSError:
            raise AppError('storage_unavailable') from None

    def load_memory(self):
        try:
            with self.memory_file.open(encoding='utf-8') as file:
                document = json.load(file)
        except FileNotFoundError:
            return empty_memory()
        except (ValueError, UnicodeError):
            raise AppError('history_unreadable') from None
        except OSError:
            raise AppError('storage_unavailable') from None
        defaults = empty_memory()
        if not isinstance(document, dict) or any(
            key in document and not isinstance(document[key], type(value))
            for key, value in defaults.items()
        ):
            raise AppError('history_unreadable')
        for key, value in defaults.items():
            document.setdefault(key, value)
        return document

    def append_event(self, user_input, response, timestamp):
        document = copy.deepcopy(self.load_memory())
        document['timeline'].append({'timestamp':timestamp, 'user':user_input, 'celeste':response})
        # Historical heuristic retained for compatibility; factual memory is M2.
        if 'brother' in response.lower():
            document['milestones']['has_siblings'] = 'yes'
        temporary = None
        try:
            self.memory_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                             dir=self.memory_file.parent,
                                             prefix='.incanta-', suffix='.tmp', delete=False) as file:
                temporary = Path(file.name)
                json.dump(document, file, ensure_ascii=False, indent=2)
                file.flush()
                os.fsync(file.fileno())
            os.replace(temporary, self.memory_file)
            temporary = None  # os.replace is the commit boundary; no fallible work afterward.
        except (OSError, ValueError, UnicodeError):
            raise AppError('persistence_failed') from None
        finally:
            if temporary is not None:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError:
                    pass

    @staticmethod
    def get_context_snippet(document, max_events=5):
        snippets = []
        for event in document['timeline'][-max_events:]:
            if isinstance(event, dict):
                snippets.append(f"[{event.get('timestamp', '')}] You: {event.get('user', '')}\nCeleste: {event.get('celeste', '')}")
        for key, value in document['milestones'].items():
            snippets.append(f'[FACT] {key}: {value}')
        return '\n'.join(snippets[-max_events:])


def get_time_context():
    now = datetime.now()
    period = 'morning' if 5 <= now.hour < 12 else 'afternoon' if 12 <= now.hour < 17 else 'evening' if 17 <= now.hour < 21 else 'night'
    return f"{now.strftime('%A')} {period}"
