#!/usr/bin/env python3
"""Explicit M1 native smoke check; synthetic inputs and temporary history only.

Run manually with INCANTA_MODEL_PATH set to an already-owned local GGUF.
No downloads or private personality/history reads. Native diagnostics are kept
in a temporary file and never printed. A native crash still fails this process.
"""
import contextlib
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.config import Settings
from frontend_app import create_app


def main():
    settings = Settings.from_env()
    if not settings.valid or not settings.model_path.is_file():
        print('PENDING: configure an accessible, already-owned local GGUF model.')
        return 2
    checksum = hashlib.sha256()
    try:
        with settings.model_path.open('rb') as model:
            for block in iter(lambda: model.read(1024 * 1024), b''):
                checksum.update(block)
    except OSError:
        print('PENDING: the configured local model is not readable.')
        return 2
    with tempfile.TemporaryDirectory(prefix='incanta-native-check-') as directory:
        root = Path(directory)
        character = root / 'synthetic.json'
        character.write_text('{"name":"Synthetic"}', encoding='utf-8')
        settings = replace(settings, personality_path=character,
                           data_dir=root / 'histories')
        # Redirect file descriptors as well as Python streams: native libraries
        # can write below Python's logging/redirect_stderr layer.
        with tempfile.TemporaryFile(mode='w+') as diagnostics:
            stdout_copy, stderr_copy = os.dup(1), os.dup(2)
            try:
                sys.stdout.flush()
                sys.stderr.flush()
                os.dup2(diagnostics.fileno(), 1)
                os.dup2(diagnostics.fileno(), 2)
                with contextlib.redirect_stdout(diagnostics), contextlib.redirect_stderr(diagnostics):
                    phase = 'startup'
                    app = create_app(settings, legacy=True)
                    client = app.test_client()
                    status = client.get('/api/status').get_json()
                    assert status['ready'] and status['model_state'] == 'unloaded'
                    assert not settings.data_dir.exists()
                    phase = 'generation'
                    reply = client.post('/api/chat', json={'message':'Say hello in one short sentence.'})
                    error_code = reply.get_json().get('error', {}).get('code', 'none')
                    assert reply.status_code == 200
                    assert reply.get_json()['response'].strip()
                    assert client.get('/api/status').get_json()['model_state'] == 'loaded'
                    phase = 'persistence'
                    document = app.extensions['incanta'].memory.load_memory()
                    assert len(document['timeline']) == 1
                    # New app state and memory reader, same durable storage.
                    phase = 'reload'
                    restarted = create_app(settings, legacy=True)
                    reloaded = restarted.extensions['incanta'].memory.load_memory()
                    assert len(reloaded['timeline']) == 1 and reloaded == document
                    assert not restarted.extensions['incanta'].history
                    phase = 'process_restart'
                    child_env = dict(os.environ, INCANTA_PERSONALITY_PATH=str(character),
                                     INCANTA_DATA_DIR=str(settings.data_dir))
                    check = subprocess.run(
                        [sys.executable, '-c',
                         "from frontend_app import create_app; "
                         "a=create_app(legacy=True); e=a.extensions['incanta']; "
                         "assert len(e.memory.load_memory()['timeline']) == 1; "
                         "assert e.inference._model is None; "
                         "assert a.test_client().get('/api/status').get_json()['model_state'] == 'unloaded'"],
                        cwd=str(Path(__file__).resolve().parents[1]), env=child_env,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
                    )
                    assert check.returncode == 0
            except Exception:
                outcome = False
            else:
                outcome = True
            finally:
                os.dup2(stdout_copy, 1)
                os.dup2(stderr_copy, 2)
                os.close(stdout_copy)
                os.close(stderr_copy)
    print('PASS: native exchange, exactly one event, and separate-process history reload.' if outcome
          else 'FAIL: native exchange or persistence check failed; private diagnostics withheld.')
    if not outcome:
        print('Failed phase:', phase, 'controlled error:', locals().get('error_code', 'none'))
    print(json.dumps({'python':platform.python_version(), 'os':platform.system(),
                      'os_version':platform.mac_ver()[0], 'architecture':platform.machine(),
                      'model_sha256':checksum.hexdigest(), 'gpu_layers':settings.gpu_layers,
                      'context_length':settings.context_length}))
    return 0 if outcome else 1


if __name__ == '__main__':
    raise SystemExit(main())
