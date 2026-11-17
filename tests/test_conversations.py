from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import json
import os
import subprocess
import sys
from threading import Event
from unittest.mock import patch
from uuid import uuid4
from companion_helpers import CompanionCase, SETUP

class ConversationTests(CompanionCase):
    def test_bootstrap_status_and_list_do_not_create_db_or_load_assets(self):
        self.assertFalse(self.settings.database_path.exists())
        self.assertEqual(self.client.get('/api/conversations').json['conversations'],[])
        self.assertTrue(self.client.get('/api/status').json['ready'])
        self.assertEqual(self.fake.calls,0)
        self.assertFalse(self.settings.database_path.exists())

    def test_setup_bounds_and_http_guards(self):
        for key, values in {'title':['','x'*121,42], 'personality':['','x'*2001],
                            'relationship':['x'*1001], 'boundaries':['','x'*2001]}.items():
            for value in values:
                r=self.call('POST','/api/conversations',dict(SETUP,**{key:value}))
                self.assertEqual(r.status_code,400,(key,r.json))
        self.assertEqual(self.client.post('/api/conversations',json=SETUP).status_code,403)
        self.assertEqual(self.client.post('/api/conversations',json=SETUP,headers={'Origin':'https://unrelated.invalid','X-CSRF-Token':self.token}).status_code,403)
        self.assertEqual(self.call('POST','/api/conversations',[]).status_code,400)
        self.assertEqual(self.call('POST','/api/conversations',dict(SETUP,title='x'*120,personality='p'*2000,boundaries='b'*2000,relationship='r'*1000)).status_code,201)
        self.assertEqual(self.client.post('/api/chat',json={'message':'hello'}).json['error']['code'],'conversation_required')
        self.assertEqual(self.call('POST','/api/conversations/not-a-uuid/turns',{}).status_code,400)

    def test_two_chats_settings_turns_state_and_two_process_restarts(self):
        a=self.create(personality='Synthetic astronomy enthusiast')
        b=self.create('Synthetic B',personality='Synthetic gardening enthusiast')
        ra=self.turn(a,'Only A secret').json
        self.assertEqual(self.turn(b,'Only B secret').status_code,200)
        captured=json.dumps(self.fake.prompts[-1])
        self.assertIn('gardening',captured)
        self.assertNotIn('astronomy',captured)
        self.assertNotIn('Only A secret',captured)
        self.assertEqual(self.fake.prompts[-1][0]['role'],'system')
        for _ in range(2):
            env=dict(os.environ,INCANTA_DATABASE_PATH=str(self.settings.database_path),INCANTA_DATA_DIR=str(self.root/'unused'))
            result=subprocess.run([sys.executable,'-c',
                "from backend.config import Settings; from backend.conversation_store import ConversationStore; "
                "s=ConversationStore(Settings.from_env().database_path); "
                "assert len(s.list_conversations())==2; "
                f"a=s.get_conversation('{a['id']}'); assert a['state']['gauges']=={ra['gauges']!r}; "
                "assert len(a['turns'])==1"],env=env,capture_output=True)
            self.assertEqual(result.returncode,0,'Separate-process restoration failed')
        self.restart()
        self.assertEqual(self.client.get(f"/api/conversations/{a['id']}").json['state']['gauges'],ra['gauges'])

    def test_ten_turns_idempotency_validation_failure_and_atomic_rollback(self):
        a=self.create(); rid=str(uuid4())
        first=self.turn(a,request_id=rid)
        self.assertEqual(first.status_code,200,first.json)
        self.assertEqual(self.turn(a,request_id=rid).json,first.json)
        self.assertEqual(self.fake.calls,1)
        self.assertEqual(self.turn(a,'different',rid).status_code,409)
        for _ in range(9):self.assertEqual(self.turn(a).status_code,200)
        detail=self.client.get(f"/api/conversations/{a['id']}").json
        self.assertEqual(len(detail['turns']),10)
        for msg in ['',42,'x'*8001]:self.assertIn(self.turn(a,msg).status_code,[400,413])
        calls=self.fake.calls
        self.fake.failure=RuntimeError('/private/synthetic-path')
        failed=self.turn(a)
        self.assertEqual(failed.status_code,500)
        self.assertNotIn('/private',failed.get_data(as_text=True))
        self.fake.failure=None
        store=self.app.extensions['incanta'].store
        with patch.object(store,'commit',side_effect=OSError('synthetic disk failure')):
            self.assertEqual(self.turn(a).status_code,500)
        after=self.client.get(f"/api/conversations/{a['id']}").json
        self.assertEqual(after['state'],detail['state'])
        self.assertEqual(len(after['turns']),10)
        self.assertEqual(self.fake.calls,calls+2)

    def test_overlap_rejected_and_settings_edit_invalidates_inflight(self):
        a=self.create(); started=Event();finish=Event()
        def delayed(prompt):started.set();finish.wait(5);return 'synthetic delayed'
        self.fake.generate=delayed
        service=self.app.extensions['incanta']
        with ThreadPoolExecutor() as pool:
            pending=pool.submit(service.process,a['id'],'hello',str(uuid4()))
            self.assertTrue(started.wait(2))
            try:
                self.assertEqual(self.turn(a).status_code,409)
                result=self.call('PATCH',f"/api/conversations/{a['id']}/settings",{'settings_revision':1,'personality':'Changed synthetic settings'})
                self.assertEqual(result.status_code,200,result.json)
            finally:finish.set()
            with self.assertRaises(Exception) as error:pending.result()
            self.assertEqual(error.exception.code,'context_changed')
        self.assertEqual(self.client.get(f"/api/conversations/{a['id']}").json['turns'],[])

    def test_bounded_prompt_and_corrupt_or_readonly_storage(self):
        a=self.create()
        self.assertEqual(self.turn(a,'x'*8000).status_code,413)
        self.assertEqual(self.fake.calls,0)
        self.settings.database_path.write_bytes(b'corrupt synthetic database')
        result=self.client.get('/api/status')
        self.assertIn('history_unreadable',result.json['issues'])
        before=self.settings.database_path.read_bytes()
        self.assertEqual(self.turn(a).status_code,500)
        self.assertEqual(self.settings.database_path.read_bytes(),before)

    def test_pagination_and_stale_revision(self):
        a=self.create()
        for n in range(4):self.assertEqual(self.turn(a,str(n)).status_code,200)
        page=self.client.get(f"/api/conversations/{a['id']}?limit=2").json
        self.assertEqual([t['input'] for t in page['turns']],['2','3'])
        older=self.client.get(f"/api/conversations/{a['id']}?limit=2&cursor={page['next_cursor']}").json
        self.assertEqual([t['input'] for t in older['turns']],['0','1'])
        self.assertEqual(self.call('PATCH',f"/api/conversations/{a['id']}/settings",{'settings_revision':99,'boundaries':'synthetic'}).status_code,409)

    def test_readonly_storage_missing_seen_db_and_transport_limits(self):
        a=self.create()
        with patch('backend.conversation_store.os.access',return_value=False):
            self.assertIn('storage_unavailable',self.client.get('/api/status').json['issues'])
            self.assertEqual(self.turn(a).status_code,503)
        self.assertEqual(self.fake.calls,0)
        self.assertEqual(self.client.get(f"/api/conversations/{a['id']}?cursor={'9'*80}").status_code,400)
        self.assertEqual(self.client.post('/api/conversations',data=' '*65537,content_type='application/json',headers={'Origin':'http://localhost','X-CSRF-Token':self.token}).status_code,413)
        original=self.settings.database_path.read_bytes()
        self.settings.database_path.rename(self.root/'detached.sqlite')
        self.assertEqual(self.turn(a).status_code,503)
        self.assertFalse(self.settings.database_path.exists())
        self.assertEqual((self.root/'detached.sqlite').read_bytes(),original)

    def test_irreducible_settings_context_is_rejected_and_old_turns_trim(self):
        a=self.create(personality='p'*2000,boundaries='b'*2000)
        self.assertEqual(self.turn(a).json['error']['code'],'context_too_large')
        self.assertEqual(self.fake.calls,0)
        b=self.create('Synthetic bounded chat')
        self.fake.reply='r'*300
        for index in range(12):self.assertEqual(self.turn(b,f'Old synthetic turn {index}').status_code,200)
        captured=json.dumps(self.fake.prompts[-1])
        self.assertNotIn('Old synthetic turn 0',captured)
        self.assertIn('Old synthetic turn 11',captured)
