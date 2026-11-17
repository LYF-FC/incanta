from dataclasses import replace
import json
from unittest.mock import patch
from companion_helpers import CompanionCase, SETUP

class ImportTests(CompanionCase):
    def setUp(self):
        super().setUp()
        self.source=self.root/'legacy.json'
        event={'timestamp':'synthetic time','user':'synthetic question','celeste':'synthetic reply','unknown_event':7}
        self.document={'timeline':[event,event], 'unknown_top':{'preserve':'synthetic'}}
        self.source.write_text(json.dumps(self.document))
        self.settings=replace(self.settings,import_path=self.source)
        self.restart()

    def preview(self):
        result=self.call('POST','/api/imports/preview',{'selection':'configured','setup':SETUP})
        self.assertEqual(result.status_code,200,result.json)
        return result.json['preview_token']

    def test_explicit_preview_backup_preservation_repeat_and_changed_source(self):
        original=self.source.read_bytes()
        self.assertEqual(self.client.get('/api/conversations').json['conversations'],[])
        token=self.preview()
        self.assertFalse(self.settings.database_path.exists())
        r=self.call('POST','/api/imports/confirm',{'preview_token':token})
        self.assertEqual(r.status_code,201,r.json)
        same=self.call('POST','/api/imports/confirm',{'preview_token':token})
        self.assertEqual(same.status_code,200)
        self.assertEqual(same.json['id'],r.json['id'])
        self.assertEqual(self.source.read_bytes(),original)
        copies=list((self.settings.database_path.parent/'imports').glob('*.json'))
        self.assertEqual(len(copies),1)
        self.assertEqual(copies[0].read_bytes(),original)
        self.assertEqual(len(self.client.get(f"/api/conversations/{r.json['id']}").json['turns']),2)
        self.source.write_text('{}')
        self.assertEqual(self.call('POST','/api/imports/confirm',{'preview_token':token}).status_code,409)

    def test_failed_backup_and_interrupted_commit_preserve_original(self):
        original=self.source.read_bytes();token=self.preview()
        with patch('backend.legacy_import.os.replace',side_effect=OSError('synthetic backup failure')):
            self.assertEqual(self.call('POST','/api/imports/confirm',{'preview_token':token}).status_code,500)
        self.assertEqual(self.source.read_bytes(),original)
        store=self.app.extensions['incanta'].store
        with patch.object(store,'commit',side_effect=OSError('synthetic commit failure')):
            self.assertEqual(self.call('POST','/api/imports/confirm',{'preview_token':token}).status_code,500)
        self.assertEqual(self.client.get('/api/conversations').json['conversations'],[])
        self.assertEqual(self.call('POST','/api/imports/confirm',{'preview_token':token}).status_code,201)
        self.assertEqual(self.source.read_bytes(),original)

    def test_corrupt_input_invalid_token_and_unconfigured_source(self):
        self.source.write_text('{broken')
        self.assertEqual(self.call('POST','/api/imports/preview',{'selection':'configured','setup':SETUP}).status_code,400)
        self.assertEqual(self.call('POST','/api/imports/confirm',{'preview_token':'not-real'}).status_code,400)
        self.assertEqual(self.call('POST','/api/imports/preview',{'selection':'arbitrary/path','setup':SETUP}).status_code,400)
