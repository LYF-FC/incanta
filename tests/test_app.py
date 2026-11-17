import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from dataclasses import replace
from helpers import FakeInference, settings_for
from backend.config import ROOT, Settings


class AppCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.settings = settings_for(self.tmp.name)
        self.fake = FakeInference()

    def make_app(self, settings=None):
        module = importlib.import_module("frontend_app")
        return module.create_app(settings=settings or self.settings, inference=self.fake)


class StartupTests(AppCase):
    def test_import_never_imports_native_model_or_reads_personality(self):
        code = '''
import builtins, sys
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name == 'llama_cpp': raise AssertionError('native import')
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
import frontend_app
assert 'llama_cpp' not in sys.modules
'''
        env = os.environ | {"INCANTA_MODEL_PATH": "/missing/synthetic.gguf",
                           "INCANTA_PERSONALITY_PATH": "/missing/synthetic.json"}
        r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr.decode())

    def test_no_assets_still_serves_interface_and_complete_status(self):
        settings = replace(self.settings, model_path=Path(self.tmp.name)/"absent.gguf",
                           personality_path=Path(self.tmp.name)/"absent.json")
        from frontend_app import create_app
        app = create_app(settings=settings)
        client = app.test_client()
        self.assertEqual(client.get('/').status_code, 200)
        state = client.get('/api/status').json
        self.assertFalse(state['ready'])
        self.assertEqual(state['emotion'], 'Neutral')
        self.assertEqual(len(state['gauges']), 7)
        self.assertIn('model_unavailable', state['issues'])
        self.assertIn('personality_unavailable', state['issues'])
        self.assertNotIn(self.tmp.name, json.dumps(state))
        self.assertFalse(settings.data_dir.exists())
        self.assertFalse(app.debug)

    def test_fake_readiness_is_fast_and_does_not_generate_or_write(self):
        app = self.make_app()
        start = time.monotonic()
        result = app.test_client().get('/api/status')
        self.assertLess(time.monotonic()-start, 2)
        self.assertTrue(result.json['ready'])
        self.assertEqual(result.json['model_state'], 'unloaded')
        self.assertEqual(self.fake.calls, 0)
        self.assertFalse(self.settings.data_dir.exists())

    def test_invalid_config_is_controlled_and_missing_ssd_does_not_mutate(self):
        app = self.make_app(replace(self.settings, host='0.0.0.0'))
        self.assertIn('invalid_configuration', app.test_client().get('/api/status').json['issues'])
        self.assertEqual(app.test_client().post('/api/chat', json={'message':'hello'}).status_code, 503)
        from frontend_app import create_app
        app = create_app(settings=replace(self.settings, model_path=Path('/missing/model.gguf')))
        self.assertEqual(app.test_client().post('/api/chat', json={'message':'hello'}).json['error']['code'], 'model_unavailable')
        self.assertFalse(self.settings.data_dir.exists())

    def test_configuration_is_root_anchored_and_bad_numbers_are_not_echoed(self):
        settings = Settings.from_env({'INCANTA_DATA_DIR':'relative', 'INCANTA_PORT':'private-invalid-value'})
        self.assertEqual(settings.data_dir, ROOT/'relative')
        self.assertFalse(settings.valid)
        for env in [{'INCANTA_HOST':'0.0.0.0'}, {'INCANTA_PORT':'0'}, {'INCANTA_THREADS':'0'}]:
            self.assertFalse(Settings.from_env(env).valid)


class RequestTests(AppCase):
    def setUp(self):
        super().setUp()
        self.app = self.make_app()
        self.client = self.app.test_client()

    def test_rejected_inputs_never_generate_or_write(self):
        cases = [({},400), ({'message':None},400), ({'message':42},400),
                 ({'message':True},400), ({'message':'  '},400), ([],400),
                 ({'message':'a'*8001},413)]
        for body, code in cases:
            with self.subTest(body_type=type(body).__name__):
                result = self.client.post('/api/chat', json=body)
                self.assertEqual(result.status_code, code)
                self.assertIn('code', result.json['error'])
        for raw, content_type, code in [('{broken','application/json',400),
                                        ('null','application/json',400),
                                        ('text','text/plain',415),
                                        (' '*65537,'application/json',413)]:
            result = self.client.post('/api/chat', data=raw, content_type=content_type)
            self.assertEqual(result.status_code, code)
            self.assertIn('error', result.json)
        self.assertEqual(self.fake.calls, 0)
        self.assertFalse(self.settings.data_dir.exists())

    def test_8000_unicode_characters_and_trimmed_text_are_accepted(self):
        result = self.client.post('/api/chat', data=json.dumps({'message':'🙂'*8000},ensure_ascii=False), content_type='application/json')
        self.assertEqual(result.status_code, 200)
        result = self.client.post('/api/chat', json={'message':'  synthetic question?  '})
        self.assertEqual(result.status_code, 200)
        engine = self.app.extensions['incanta']
        self.assertEqual(engine.memory.load_memory()['timeline'][-1]['user'], 'synthetic question?')
        self.assertEqual(result.json['gauges'], self.client.get('/api/status').json['gauges'])

    def test_private_exception_does_not_escape_response_or_logs_and_retry_works(self):
        self.fake.failure = RuntimeError('/private/synthetic-path synthetic-private-prompt')
        import io
        import logging
        output = io.StringIO()
        handler = logging.StreamHandler(output)
        self.app.logger.addHandler(handler)
        try:
            result = self.client.post('/api/chat', json={'message':'synthetic-private-prompt'})
        finally:
            self.app.logger.removeHandler(handler)
        self.assertEqual(result.status_code, 500)
        self.assertEqual(result.json['error']['code'], 'generation_failed')
        self.assertNotIn('/private', result.get_data(as_text=True)+output.getvalue())
        self.assertNotIn('synthetic-private-prompt', result.get_data(as_text=True)+output.getvalue())
        self.fake.failure = None
        self.assertEqual(self.client.post('/api/chat', json={'message':'retry'}).status_code, 200)
        self.assertEqual(len(self.app.extensions['incanta'].memory.load_memory()['timeline']), 1)

    def test_busy_and_storage_failure_use_the_http_contract(self):
        from unittest.mock import patch
        engine = self.app.extensions['incanta']
        engine._processing.acquire()
        try:
            result = self.client.post('/api/chat', json={'message':'overlap'})
            self.assertEqual(result.status_code, 409)
            self.assertEqual(self.fake.calls, 0)
        finally:
            engine._processing.release()
        with patch('backend.memory_manager.os.replace', side_effect=OSError('/private/synthetic')):
            result = self.client.post('/api/chat', json={'message':'synthetic'})
        self.assertEqual(result.status_code, 500)
        self.assertEqual(result.json['error']['code'], 'persistence_failed')
        self.assertEqual(engine.history, [])

    def test_status_rechecks_character_and_storage(self):
        self.settings.personality_path.write_text('invalid')
        self.assertIn('personality_unavailable', self.client.get('/api/status').json['issues'])
        self.settings.personality_path.write_text('{}')
        self.settings.data_dir.write_text('synthetic blocking file')
        self.assertIn('storage_unavailable', self.client.get('/api/status').json['issues'])

    def test_read_only_storage_is_not_ready_and_never_generates(self):
        from unittest.mock import patch
        with patch('backend.memory_manager.os.access', return_value=False):
            self.assertIn('storage_unavailable', self.client.get('/api/status').json['issues'])
            result = self.client.post('/api/chat',json={'message':'synthetic'})
            self.assertEqual(result.status_code, 503)
        self.assertEqual(self.fake.calls, 0)
        self.assertFalse(self.settings.data_dir.exists())
