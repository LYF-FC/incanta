import json
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from uuid import uuid4
from companion_helpers import CompanionCase

class FactTests(CompanionCase):
    def fact(self,chat,content='Synthetic shared fact',**extra):
        r=self.call('POST',f"/api/conversations/{chat['id']}/facts",dict(content=content,**extra))
        self.assertEqual(r.status_code,201,r.json)
        return r.json

    def test_selected_fact_sharing_correction_revocation_deletion_and_restart(self):
        a=self.create();b=self.create('Synthetic B');c=self.create('Synthetic C')
        shared=self.fact(a);self.fact(a,'Synthetic unshared fact')
        url=f"/api/facts/{shared['id']}"
        for recipient in [b,c]:
            self.assertEqual(self.call('PUT',url+f"/grants/{recipient['id']}",{'revision':1}).status_code,200)
        self.turn(b)
        prompt=json.dumps(self.fake.prompts[-1]);self.assertIn('Synthetic shared fact',prompt);self.assertNotIn('Synthetic unshared fact',prompt)
        fixed=self.call('PATCH',url,{'revision':1,'content':'Synthetic corrected fact'})
        self.assertEqual(fixed.status_code,200,fixed.json)
        self.assertEqual(self.call('PATCH',url,{'revision':1,'content':'stale'}).status_code,409)
        self.restart()
        for recipient in [b,c]:
            facts=self.client.get(f"/api/conversations/{recipient['id']}/facts").json['facts']
            self.assertEqual([f['content'] for f in facts],['Synthetic corrected fact'])
        self.assertEqual(self.call('DELETE',url+f"/grants/{b['id']}",{'revision':2}).status_code,200)
        self.assertEqual(self.client.get(f"/api/conversations/{b['id']}/facts").json['facts'],[])
        self.assertEqual(self.call('DELETE',url,{'revision':2}).status_code,200)
        self.assertEqual(self.call('DELETE',url,{'revision':2}).status_code,200)
        self.restart()
        for recipient in [b,c]:self.assertEqual(self.client.get(f"/api/conversations/{recipient['id']}/facts").json['facts'],[])
        self.assertEqual([f['content'] for f in self.client.get(f"/api/conversations/{a['id']}/facts").json['facts']],['Synthetic unshared fact'])
        self.turn(c)
        self.assertNotIn('Synthetic corrected fact',json.dumps(self.fake.prompts[-1]))
        with self.app.extensions['incanta'].store.connection() as db:
            self.assertIsNone(db.execute('SELECT content FROM facts WHERE id=?',(shared['id'],)).fetchone()[0])

    def test_provenance_bounds_and_no_generated_fact_heuristic(self):
        a=self.create();b=self.create('Synthetic B')
        self.fake.reply='A synthetic brother mentioned by the model.'
        turn=self.turn(a).json['turn']
        self.assertEqual(self.client.get(f"/api/conversations/{a['id']}/facts").json['facts'],[])
        r=self.call('POST',f"/api/conversations/{b['id']}/facts",{'content':'Synthetic', 'source_turn_id':turn['id']})
        self.assertEqual(r.status_code,400)
        fact=self.fact(a,source_turn_id=turn['id'])
        self.assertEqual(fact['source_turn_id'],turn['id'])
        for text in ['',42,'x'*2001]:
            self.assertEqual(self.call('POST',f"/api/conversations/{a['id']}/facts",{'content':text}).status_code,400)
        self.assertEqual(self.call('DELETE',f"/api/facts/{fact['id']}/grants/{a['id']}",{'revision':1}).status_code,400)

    def test_deletion_during_generation_rejects_obsolete_result(self):
        a=self.create();fact=self.fact(a);started=Event();finish=Event()
        def delayed(prompt):started.set();finish.wait(5);return 'obsolete synthetic'
        self.fake.generate=delayed
        service=self.app.extensions['incanta']
        with ThreadPoolExecutor() as pool:
            pending=pool.submit(service.process,a['id'],'hello',str(uuid4()))
            self.assertTrue(started.wait(2))
            try:self.assertEqual(self.call('DELETE',f"/api/facts/{fact['id']}",{'revision':1}).status_code,200)
            finally:finish.set()
            with self.assertRaises(Exception) as caught:pending.result()
            self.assertEqual(caught.exception.code,'context_changed')
        self.assertEqual(self.client.get(f"/api/conversations/{a['id']}").json['turns'],[])
