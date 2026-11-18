"""Lazy local SQLite storage. Never replace or reset an unreadable database."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import sqlite3
from threading import RLock
from urllib.parse import quote
from uuid import UUID, uuid4
from backend.errors import AppError
from backend.gauge_engine import get_current_gauges


def identifier(value):
    try:
        if not isinstance(value,str) or str(UUID(value)) != value:
            raise ValueError
    except (ValueError,TypeError,AttributeError):
        raise AppError('invalid_request') from None
    return value


def text(value, minimum, maximum):
    if not isinstance(value,str) or not minimum <= len(value.strip()) <= maximum:
        raise AppError('invalid_request')
    return value.strip()


def revision(value):
    if type(value) is not int or value < 1:
        raise AppError('invalid_request')
    return value


def setup_values(body):
    if not isinstance(body,dict):
        raise AppError('invalid_request')
    return {k:text(body.get(k,''),lo,hi) for k,lo,hi in [
        ('title',1,120),('personality',1,2000),('relationship',0,1000),('boundaries',1,2000)]}


def now():
    return datetime.now(timezone.utc).isoformat()


class ConversationStore:
    def __init__(self,path):
        self.path=Path(path)
        self._initialization=RLock()
        self._seen=False

    def _check_location(self):
        if self.path.is_symlink():
            raise AppError('storage_unavailable')
        # Do not manufacture an absent external-volume mount point.
        parts=self.path.parts
        if len(parts)>2 and parts[1]=='Volumes' and not Path(*parts[:3]).is_dir():
            raise AppError('storage_unavailable')
        parent=self.path.parent
        while not parent.exists():
            parent=parent.parent
        if not parent.is_dir() or not os.access(parent,os.R_OK|os.W_OK|os.X_OK):
            raise AppError('storage_unavailable')
        if self.path.exists() and (not self.path.is_file() or not os.access(self.path,os.R_OK|os.W_OK)):
            raise AppError('storage_unavailable')
        if self._seen and not self.path.exists():
            raise AppError('storage_unavailable')

    def available(self):
        self._check_location()
        if self.path.exists():
            with self.connection() as db:
                if db.execute('PRAGMA quick_check').fetchone()[0]!='ok':
                    raise AppError('history_unreadable')

    @contextmanager
    def connection(self,write=False):
        db=None
        try:
            with self._initialization:
                self._check_location()
                if not self.path.exists():
                    if not write:
                        yield None
                        return
                    self.path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
                    fd=os.open(self.path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
                    created=os.fstat(fd)
                    os.close(fd)
                    try:
                        db=sqlite3.connect(f'file:{quote(str(self.path))}?mode=rw',uri=True,timeout=5)
                        db.executescript((Path(__file__).parent/'migrations/001_companion.sql').read_text())
                    except (sqlite3.DatabaseError,OSError):
                        if db is not None:
                            db.close()
                            db=None
                        # Only undo this call's new, failed database, while the
                        # initialization lock still excludes other local writes.
                        # An existing or replaced file must never be removed.
                        try:
                            current=self.path.lstat()
                            if (current.st_dev,current.st_ino)==(created.st_dev,created.st_ino):
                                self.path.unlink()
                        except OSError:
                            pass
                        raise
                if db is None:
                    db=sqlite3.connect(f'file:{quote(str(self.path))}?mode=rw',uri=True,timeout=5)
                self._seen=True
                db.row_factory=sqlite3.Row
                db.execute('PRAGMA foreign_keys=ON')
                db.execute('PRAGMA synchronous=FULL')
                self._migrate(db)
            if write:db.execute('BEGIN IMMEDIATE')
            else:db.execute('BEGIN')
            yield db
            if write:self.commit(db)
        except AppError:
            raise
        except sqlite3.DatabaseError:
            raise AppError('persistence_failed' if write else 'history_unreadable') from None
        except OSError:
            raise AppError('persistence_failed' if write else 'storage_unavailable') from None
        finally:
            if db is not None:
                db.rollback()
                db.close()

    @staticmethod
    def _migrate(db):
        version = db.execute('PRAGMA user_version').fetchone()[0]
        if version == 2:
            return
        db.execute('BEGIN IMMEDIATE')
        try:
            version = db.execute('PRAGMA user_version').fetchone()[0]
            if version == 1:
                sql = (Path(__file__).parent/'migrations/002_visuals.sql').read_text()
                for statement in sql.split(';'):
                    if statement.strip():
                        db.execute(statement)
            elif version != 2:
                raise AppError('history_unreadable')
            db.commit()
        except BaseException:
            db.rollback()
            raise

    @staticmethod
    def commit(db):
        db.commit()

    @staticmethod
    def row(db,cid):
        result=db.execute('SELECT * FROM conversations WHERE id=?',(identifier(cid),)).fetchone() if db else None
        if result is None:raise AppError('not_found')
        ConversationStore.decode_state(result['gauges'],result['emotion'])
        return dict(result)

    @staticmethod
    def decode_state(encoded,emotion):
        try:
            gauges=json.loads(encoded)
            if (not isinstance(gauges,dict) or set(gauges)!=set(get_current_gauges())
                    or any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=100 for v in gauges.values())
                    or not isinstance(emotion,str) or not emotion.strip()):
                raise ValueError
        except (ValueError,TypeError,OverflowError):
            raise AppError('history_unreadable') from None
        return {'gauges':gauges,'emotion':emotion}

    @staticmethod
    def public(row):
        result=dict(row)
        result['state']=ConversationStore.decode_state(result.pop('gauges'),result.pop('emotion'))
        return result

    def insert_conversation(self,db,values):
        cid=str(uuid4());stamp=now()
        db.execute('INSERT INTO conversations VALUES (?,?,?,?,?,1,1,?,?,?,?)',
                   (cid,values['title'],values['personality'],values['relationship'],values['boundaries'],
                    json.dumps(get_current_gauges()),'Neutral',stamp,stamp))
        return cid

    def create_conversation(self,body):
        values=setup_values(body)
        with self.connection(write=True) as db:cid=self.insert_conversation(db,values)
        return self.get_conversation(cid)

    def list_conversations(self):
        with self.connection() as db:
            if db is None:return []
            return [dict(r) for r in db.execute('SELECT id,title,updated_at FROM conversations ORDER BY updated_at DESC,id')]

    def get_conversation(self,cid,limit=50,cursor=None):
        identifier(cid)
        if type(limit) is not int or not 1<=limit<=100 or (cursor is not None and (type(cursor) is not int or not 1<=cursor<=9223372036854775807)):
            raise AppError('invalid_request')
        with self.connection() as db:
            result=self.public(self.row(db,cid))
            rows=db.execute('SELECT * FROM turns WHERE conversation_id=? AND sequence<? ORDER BY sequence DESC LIMIT ?',
                            (cid,cursor if cursor is not None else 9223372036854775807,limit+1)).fetchall()
            result['next_cursor']=rows[limit-1]['sequence'] if len(rows)>limit else None
            result['turns']=[self.turn_public(r) for r in reversed(rows[:limit])]
            return result

    @staticmethod
    def turn_public(row):
        value=dict(row)
        value['gauges']=ConversationStore.decode_state(value['gauges'],value['emotion'])['gauges']
        return value

    def update_settings(self,cid,body):
        if not isinstance(body,dict):raise AppError('invalid_request')
        expected=revision(body.get('settings_revision'))
        changes={k:v for k,v in body.items() if k in ['title','personality','relationship','boundaries']}
        if not changes:raise AppError('invalid_request')
        with self.connection(write=True) as db:
            current=self.row(db,cid)
            if current['settings_revision']!=expected:raise AppError('revision_conflict')
            values=setup_values(dict(current,**changes))
            db.execute('UPDATE conversations SET title=?,personality=?,relationship=?,boundaries=?,settings_revision=settings_revision+1,context_revision=context_revision+1,updated_at=? WHERE id=?',
                       (values['title'],values['personality'],values['relationship'],values['boundaries'],now(),cid))
        return self.get_conversation(cid)

    @staticmethod
    def insert_turn(db,cid,request_id,message,response,gauges,emotion,settings_rev,context_rev,timestamp=None):
        tid=str(uuid4());stamp=timestamp or now();encoded=json.dumps(gauges)
        db.execute('INSERT INTO turns(id,conversation_id,request_id,input,response,timestamp,settings_revision,context_revision,gauges,emotion) VALUES (?,?,?,?,?,?,?,?,?,?)',
                   (tid,cid,request_id,message,response,stamp,settings_rev,context_rev,encoded,emotion))
        db.execute('UPDATE conversations SET gauges=?,emotion=?,updated_at=? WHERE id=?',(encoded,emotion,now(),cid))
        return ConversationStore.turn_public(db.execute('SELECT * FROM turns WHERE id=?',(tid,)).fetchone())
