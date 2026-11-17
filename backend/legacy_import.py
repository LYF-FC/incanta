"""Owner-selected import: preview, preserve exact bytes, then commit once."""
import hashlib
import json
import os
from pathlib import Path
import secrets
import tempfile
import time
from uuid import uuid4
from backend.conversation_store import setup_values, now
from backend.errors import AppError
from backend.gauge_engine import get_current_gauges


class LegacyImporter:
    def __init__(self,store,path):
        self.store=store;self.path=Path(path) if path is not None else None
        self.previews={}

    def source(self):
        try:
            if self.path is None or self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_size>16*1024*1024:
                raise ValueError
            content=self.path.read_bytes()
            if len(content)>16*1024*1024:raise ValueError
            document=json.loads(content)
            if not isinstance(document,dict) or not isinstance(document.get('timeline'),list):raise ValueError
            for event in document['timeline']:
                if not isinstance(event,dict) or not isinstance(event.get('user'),str) or not isinstance(event.get('celeste'),str) or not isinstance(event.get('timestamp'),str):raise ValueError
                if not event['user'].strip() or not event['celeste'].strip():raise ValueError
            return content,document,hashlib.sha256(content).hexdigest()
        except (OSError,ValueError,UnicodeError):raise AppError('import_unavailable') from None

    def preview(self,body):
        if not isinstance(body,dict) or body.get('selection')!='configured':raise AppError('invalid_request')
        values=setup_values(body.get('setup'))
        content,document,checksum=self.source()
        stamp=time.monotonic()
        self.previews={k:v for k,v in self.previews.items() if stamp-v['time']<600}
        if len(self.previews)>=20:raise AppError('conversation_busy')
        token=secrets.token_urlsafe(32)
        self.previews[token]={'checksum':checksum,'setup':values,'time':stamp}
        return {'preview_token':token,'turn_count':len(document['timeline']),'setup':values,
                'warnings':['Original bytes and unknown fields will be preserved locally. No legacy milestone is treated as a verified fact.']}

    def preserve(self,content,checksum):
        parent=self.store.path.parent/'imports'
        if parent.is_symlink():raise OSError
        parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        target=parent/(checksum+'.json')
        if target.is_symlink():raise OSError
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest()!=checksum:raise OSError
            return target.name
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(dir=parent,prefix='.incanta-import-',delete=False) as file:
                temporary=Path(file.name);file.write(content);file.flush();os.fsync(file.fileno())
            os.replace(temporary,target);temporary=None
        finally:
            if temporary is not None:temporary.unlink(missing_ok=True)
        return target.name

    def confirm(self,body):
        token=body.get('preview_token') if isinstance(body,dict) else None
        if not isinstance(token,str) or token not in self.previews:raise AppError('invalid_request')
        preview=self.previews[token]
        if time.monotonic()-preview['time']>=600:raise AppError('invalid_request')
        try:content,document,checksum=self.source()
        except AppError:raise AppError('import_changed') from None
        if checksum!=preview['checksum']:raise AppError('import_changed')
        try:preserved=self.preserve(content,checksum)
        except OSError:raise AppError('persistence_failed') from None
        with self.store.connection(write=True) as db:
            previous=db.execute('SELECT conversation_id FROM imports WHERE checksum=?',(checksum,)).fetchone()
            if previous:return self.store.public(self.store.row(db,previous[0])),False
            cid=self.store.insert_conversation(db,preview['setup'])
            for event in document['timeline']:
                self.store.insert_turn(db,cid,str(uuid4()),event['user'],event['celeste'],get_current_gauges(),'Neutral',1,1,event['timestamp'])
            db.execute('INSERT INTO imports VALUES (?,?,1,?,?)',(checksum,cid,now(),preserved))
        return self.store.get_conversation(cid),True
