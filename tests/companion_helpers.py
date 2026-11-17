"""Temporary, synthetic companion API fixtures."""
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4
from helpers import FakeInference, settings_for

SETUP = {'title':'Synthetic A', 'personality':'Curious and precise.',
         'relationship':'A fictional conversation partner.',
         'boundaries':'Respect stated limits; ask when unsure.'}

class CompanionCase(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.settings = replace(settings_for(self.root), database_path=self.root/'state'/'companion.sqlite')
        self.fake = FakeInference()
        self.restart()

    def restart(self):
        from frontend_app import create_app
        self.app = create_app(self.settings, inference=self.fake)
        self.client = self.app.test_client()
        bootstrap = self.client.get('/api/bootstrap')
        self.token = bootstrap.get_json()['csrf_token']

    def call(self, method, path, body=None, **kwargs):
        return self.client.open(path, method=method, json=body,
                                headers={'Origin':'http://localhost','X-CSRF-Token':self.token}, **kwargs)

    def create(self, title='Synthetic A', **changes):
        body = dict(SETUP, title=title, **changes)
        result = self.call('POST','/api/conversations',body)
        self.assertEqual(result.status_code,201,result.get_json())
        return result.get_json()

    def turn(self, conversation, message='Synthetic hello', request_id=None):
        return self.call('POST',f"/api/conversations/{conversation['id']}/turns",
                         {'request_id':request_id or str(uuid4()), 'message':message})
