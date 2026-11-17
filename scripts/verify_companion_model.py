#!/usr/bin/env python3
"""Explicit native 002 smoke check, separate from model-free test discovery.

Uses an already-owned configured GGUF, synthetic settings and temporary SQLite.
It cannot substitute for the owner's 30-minute dialogue-quality acceptance.
"""
from dataclasses import replace
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from uuid import uuid4

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.config import Settings
from backend.conversation_service import ConversationService


def main():
    settings=Settings.from_env()
    if not settings.valid or not settings.model_path.is_file():
        print('PENDING: configure an already-owned local model for this explicit check.')
        return 2
    outcome=False
    with tempfile.TemporaryDirectory(prefix='incanta-companion-native-') as directory:
        settings=replace(settings,data_dir=Path(directory),database_path=Path(directory)/'companion.sqlite')
        with tempfile.TemporaryFile(mode='w+') as diagnostics:
            saved_out,saved_err=os.dup(1),os.dup(2)
            try:
                sys.stdout.flush();sys.stderr.flush()
                os.dup2(diagnostics.fileno(),1);os.dup2(diagnostics.fileno(),2)
                service=ConversationService(settings)
                assert service.status()['model_state']=='unloaded'
                a=service.store.create_conversation({'title':'Synthetic native conversation',
                    'personality':'Speak clearly and concisely.', 'relationship':'A fictional conversation partner.',
                    'boundaries':'Use only explicitly saved facts; ask when unsure.'})
                result=service.process(a['id'],'Please greet me in one short English sentence.',str(uuid4()))
                assert result['response'].strip()
                assert len(service.store.get_conversation(a['id'])['turns'])==1
                env=dict(os.environ,INCANTA_DATABASE_PATH=str(settings.database_path))
                child=subprocess.run([sys.executable,'-c',
                    'from backend.config import Settings; from backend.conversation_service import ConversationService; '
                    's=ConversationService(Settings.from_env()); '
                    f"a=s.store.get_conversation('{a['id']}'); assert len(a['turns'])==1; "
                    'assert s.inference._model is None'],cwd=str(Path(__file__).resolve().parents[1]),
                    env=env,capture_output=True,timeout=30)
                assert child.returncode==0
                outcome=True
            except Exception:
                pass
            finally:
                sys.stdout.flush();sys.stderr.flush()
                os.dup2(saved_out,1);os.dup2(saved_err,2);os.close(saved_out);os.close(saved_err)
    print('PASS: native structured conversation, one SQLite turn and separate-process reload.' if outcome
          else 'FAIL: companion native check did not pass; private diagnostics withheld.')
    print('Owner-reviewed 30-minute conversation acceptance remains separate.')
    return 0 if outcome else 1


if __name__=='__main__':
    raise SystemExit(main())
