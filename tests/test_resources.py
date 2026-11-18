from threading import Event, Thread
import unittest

from backend.resource_manager import ResourceManager


class ResourceTests(unittest.TestCase):
    def test_waiting_chat_takes_next_idle_slot(self):
        manager = ResourceManager()
        chat_ready = Event()
        chat_done = Event()

        def chat():
            with manager.acquire('chat', 'turn'):
                chat_ready.set()
                chat_done.wait(2)

        with manager.acquire('manual', 'image'):
            thread = Thread(target=chat)
            thread.start()
            self.assertTrue(manager.waiting_for_chat.wait(2))
            with manager.acquire('manual', 'other', blocking=False) as acquired:
                self.assertFalse(acquired)
        try:
            self.assertTrue(chat_ready.wait(2))
            with manager.acquire('manual', 'other', blocking=False) as acquired:
                self.assertFalse(acquired)
        finally:
            chat_done.set()
            thread.join(2)
