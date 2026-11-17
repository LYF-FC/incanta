import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        from backend.memory_manager import MemoryManager
        self.memory = MemoryManager('synthetic', data_dir=Path(self.tmp.name)/'history')

    def test_construction_and_load_do_not_create_directories(self):
        self.assertEqual(self.memory.load_memory()['timeline'], [])
        self.assertFalse(self.memory.memory_file.parent.exists())

    def test_one_append_preserves_duplicates_unknown_fields_and_reload(self):
        old = {'timeline':[{'synthetic':1},{'synthetic':1}], 'custom':{'keep':True}}
        self.memory.memory_file.parent.mkdir()
        self.memory.memory_file.write_text(json.dumps(old))
        self.memory.append_event('synthetic input','synthetic reply','2026-11-04 12:00')
        document = self.memory.load_memory()
        self.assertEqual(document['timeline'][:2], old['timeline'])
        self.assertEqual(document['custom'], old['custom'])
        self.assertEqual(len(document['timeline']), 3)
        self.assertEqual(document['timeline'][-1]['user'], 'synthetic input')
        self.assertEqual(len(list(self.memory.memory_file.parent.iterdir())), 1)

    def test_replace_and_flush_failures_preserve_original_and_clean_temp(self):
        from backend.errors import AppError
        self.memory.append_event('first','first reply','time')
        original = self.memory.memory_file.read_bytes()
        for target in ['backend.memory_manager.os.replace','backend.memory_manager.os.fsync']:
            with self.subTest(target=target), patch(target, side_effect=OSError('synthetic failure')):
                with self.assertRaises(AppError) as caught:
                    self.memory.append_event('next','next reply','time')
                self.assertEqual(caught.exception.code, 'persistence_failed')
            self.assertEqual(self.memory.memory_file.read_bytes(), original)
            self.assertEqual(len(list(self.memory.memory_file.parent.iterdir())), 1)

    def test_malformed_history_is_preserved_and_permission_error_is_controlled(self):
        from backend.errors import AppError
        self.memory.memory_file.parent.mkdir()
        for broken in ['{broken', '[]', '{"timeline": {}}']:
            self.memory.memory_file.write_text(broken)
            with self.assertRaises(AppError) as caught: self.memory.load_memory()
            self.assertEqual(caught.exception.code, 'history_unreadable')
            self.assertEqual(self.memory.memory_file.read_text(), broken)
        with patch('pathlib.Path.open', side_effect=PermissionError('synthetic')):
            with self.assertRaises(AppError) as caught: self.memory.load_memory()
            self.assertEqual(caught.exception.code, 'storage_unavailable')
