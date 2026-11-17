import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from helpers import FakeInference, settings_for


class ChatTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        from backend.chat_engine import ChatEngine
        self.settings = settings_for(self.tmp.name)
        self.fake = FakeInference('I am curious about that?')
        self.engine = ChatEngine(self.settings, inference=self.fake)

    def test_ten_successes_add_ten_events_and_restart_can_read_them(self):
        for n in range(10):
            result = self.engine.process('synthetic question?')
            self.assertIn('response', result)
            self.assertEqual(result['gauges'], self.engine.status()['gauges'])
        self.assertEqual(len(self.engine.memory.load_memory()['timeline']), 10)
        from backend.chat_engine import ChatEngine
        fresh = ChatEngine(self.settings, inference=FakeInference())
        self.assertEqual(len(fresh.memory.load_memory()['timeline']), 10)

    def test_generation_and_persistence_failure_do_not_publish_state(self):
        from backend.errors import AppError
        state = self.engine.status()['gauges']
        self.fake.failure = RuntimeError('/private/synthetic input')
        with self.assertRaises(AppError): self.engine.process('question?')
        self.assertEqual(self.engine.status()['gauges'], state)
        self.assertFalse(self.settings.data_dir.exists())
        self.fake.failure = None
        self.engine.process('first?')
        previous = self.engine.status()['gauges']
        original = self.engine.memory.memory_file.read_bytes()
        with patch('backend.memory_manager.os.replace', side_effect=OSError('synthetic')):
            with self.assertRaises(AppError): self.engine.process('second?')
        self.assertEqual(self.engine.status()['gauges'], previous)
        self.assertEqual(self.engine.memory.memory_file.read_bytes(), original)
        self.assertEqual(len(self.engine.history), 1)
        self.engine.process('retry?')
        self.assertEqual(len(self.engine.memory.load_memory()['timeline']), 2)

    def test_busy_request_does_not_generate_and_status_remains_responsive(self):
        from backend.errors import AppError
        started, release = threading.Event(), threading.Event()
        original = self.fake.generate
        def slow(prompt):
            started.set()
            if not release.wait(5): raise RuntimeError('test timed out')
            return original(prompt)
        self.fake.generate = slow
        failures = []
        def turn():
            try: self.engine.process('first?')
            except Exception as error: failures.append(error)
        thread = threading.Thread(target=turn)
        thread.start()
        self.addCleanup(release.set)
        try:
            self.assertTrue(started.wait(2))
            with self.assertRaises(AppError) as caught: self.engine.process('overlap?')
            self.assertEqual(caught.exception.code, 'conversation_busy')
            self.assertEqual(len(self.engine.status()['gauges']), 7)
        finally:
            release.set(); thread.join(5)
        self.assertFalse(thread.is_alive())
        self.assertEqual(failures, [])
        self.assertEqual(self.fake.calls, 1)
        self.assertEqual(len(self.engine.memory.load_memory()['timeline']), 1)

    def test_bad_character_and_corrupt_history_never_call_inference(self):
        from backend.errors import AppError
        self.settings.personality_path.write_text('[]')
        with self.assertRaises(AppError) as caught: self.engine.process('synthetic')
        self.assertEqual(caught.exception.code, 'personality_unavailable')
        self.settings.personality_path.write_text('{}')
        self.engine.memory.memory_file.parent.mkdir()
        self.engine.memory.memory_file.write_text('{broken')
        with self.assertRaises(AppError) as caught: self.engine.process('synthetic')
        self.assertEqual(caught.exception.code, 'history_unreadable')
        self.assertEqual(self.fake.calls, 0)
