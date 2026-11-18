"""Process-local scheduling at idle boundaries. A lease never preempts its holder."""
from contextlib import contextmanager
from threading import Condition, Event


class ResourceManager:
    PRIORITY = {'chat': 0, 'manual': 1, 'background': 2}

    def __init__(self):
        self._condition = Condition()
        self.waiting_for_chat = Event()
        self.holder = None
        self._waiters = []

    @contextmanager
    def acquire(self, kind, owner, *, blocking=True):
        ticket = (self.PRIORITY[kind], object())
        with self._condition:
            self._waiters.append(ticket)
            if kind == 'chat':
                self.waiting_for_chat.set()
            def ready():
                return self.holder is None and min(self._waiters, key=lambda waiting: waiting[0]) == ticket
            try:
                acquired = self._condition.wait_for(ready) if blocking else ready()
                if acquired:
                    self.holder = (kind, owner)
            finally:
                self._waiters.remove(ticket)
                if not any(priority == 0 for priority, _ in self._waiters):
                    self.waiting_for_chat.clear()
                self._condition.notify_all()
        try:
            yield acquired
        finally:
            if acquired:
                with self._condition:
                    self.holder = None
                    self._condition.notify_all()
