"""Canonical facts and explicit grants; no copied shared fact content."""
from uuid import uuid4
from backend.conversation_store import identifier, text, revision, now
from backend.errors import AppError


class FactStore:
    def __init__(self,store):self.store=store

    @staticmethod
    def permitted(db,cid):
        return [dict(r) for r in db.execute('SELECT f.* FROM facts f JOIN fact_grants g ON g.fact_id=f.id WHERE g.conversation_id=? AND f.content IS NOT NULL ORDER BY f.updated_at DESC,f.id',(cid,))]

    @staticmethod
    def record(db,fid):
        result=db.execute('SELECT * FROM facts WHERE id=?',(identifier(fid),)).fetchone()
        if result is None:raise AppError('not_found')
        return dict(result)

    @staticmethod
    def invalidate(db,fid):
        db.execute('UPDATE conversations SET context_revision=context_revision+1 WHERE id IN (SELECT conversation_id FROM fact_grants WHERE fact_id=?)',(fid,))

    @staticmethod
    def public(db,fact):
        result=dict(fact)
        result['shared_recipients']=[r[0] for r in db.execute('SELECT conversation_id FROM fact_grants WHERE fact_id=? AND conversation_id!=? ORDER BY conversation_id',(result['id'],result['source_conversation_id']))]
        return result

    def list(self,cid):
        with self.store.connection() as db:
            self.store.row(db,cid)
            return [self.public(db,f) for f in self.permitted(db,cid)]

    def create(self,cid,body):
        if not isinstance(body,dict):raise AppError('invalid_request')
        content=text(body.get('content'),1,2000);source=body.get('source_turn_id')
        if source is not None:identifier(source)
        with self.store.connection(write=True) as db:
            self.store.row(db,cid)
            if source is not None and db.execute('SELECT id FROM turns WHERE id=? AND conversation_id=?',(source,cid)).fetchone() is None:
                raise AppError('invalid_request')
            fid=str(uuid4());stamp=now()
            db.execute('INSERT INTO facts VALUES (?,?,?,?,1,?,?)',(fid,cid,source,content,stamp,stamp))
            db.execute('INSERT INTO fact_grants VALUES (?,?)',(fid,cid))
            self.invalidate(db,fid)
            result=self.public(db,self.record(db,fid))
        return result

    def edit(self,fid,body,delete=False):
        if not isinstance(body,dict):raise AppError('invalid_request')
        expected=revision(body.get('revision'))
        content=None if delete else text(body.get('content'),1,2000)
        with self.store.connection(write=True) as db:
            fact=self.record(db,fid)
            if fact['content'] is None:
                if delete:return {'id':fid,'revision':fact['revision'],'deleted':True}
                raise AppError('not_found')
            if fact['revision']!=expected:raise AppError('revision_conflict')
            self.invalidate(db,fid)
            db.execute('UPDATE facts SET content=?,revision=revision+1,updated_at=? WHERE id=?',(content,now(),fid))
            if delete:
                db.execute('DELETE FROM fact_grants WHERE fact_id=?',(fid,))
                result={'id':fid,'revision':expected+1,'deleted':True}
            else:result=self.public(db,self.record(db,fid))
        return result

    def grant(self,fid,cid,body,revoke=False):
        identifier(cid)
        if not isinstance(body,dict):raise AppError('invalid_request')
        expected=revision(body.get('revision'))
        with self.store.connection(write=True) as db:
            self.store.row(db,cid);fact=self.record(db,fid)
            if fact['content'] is None:raise AppError('not_found')
            if fact['revision']!=expected:raise AppError('revision_conflict')
            if revoke and cid==fact['source_conversation_id']:raise AppError('invalid_request')
            if revoke:changed=db.execute('DELETE FROM fact_grants WHERE fact_id=? AND conversation_id=?',(fid,cid)).rowcount
            else:changed=db.execute('INSERT OR IGNORE INTO fact_grants VALUES (?,?)',(fid,cid)).rowcount
            if changed:db.execute('UPDATE conversations SET context_revision=context_revision+1 WHERE id=?',(cid,))
            result=self.public(db,self.record(db,fid))
        return result
