# Reliable local chat validation

Actual results and open gates are in [verification.md](verification.md). Use Python 3.11 or 3.13 and Node; automated checks use fake inference and temporary storage.

## Model-free acceptance

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
node --test tests/frontend.test.js
node --check frontend/app.js
node --check frontend/chat_helpers.js
bash -n run.sh
SPECIFY_FEATURE_DIRECTORY=specs/001-reliable-local-chat bash .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
```

Expected: 32 Python and six frontend tests pass on the current baseline. Counts may change as features are added. Tests cover missing assets, malformed input, concurrency, inference/storage failure and preserved history. Do not install the historical native dependency snapshot just for checks.

## Synthetic browser journey

Create temporary settings with `tests/helpers.py:settings_for`, inject `FakeInference` into `frontend_app.create_app`, and serve on a free loopback port with debug/reloader off. This is a test harness, not a production fake-mode option.

Verify initial readiness without inference/history creation, literal user/model markup, one stored event, delayed-request disabled controls, controlled generation failure with unchanged state/event count, successful retry, gauge toggle and missing-character readiness refresh. Inspect only synthetic history counts. See the recorded T018 outcomes for the completed pass.

## Explicit native-model gate

Set `INCANTA_MODEL_PATH` locally to an already-owned GGUF; never commit the path. Install only the separately scoped native dependency when needed; see [setup](../../SETUP.md). Run explicitly, outside automated discovery:

```sh
python scripts/verify_local_model.py
```

Expected: PASS, one event, new-app reload and a non-sensitive model checksum/environment report. Exit 2 means the configured model is unavailable; exit 1 means verification failed. A native crash also fails verification. This runner reads no private character/history and downloads nothing.

For the process/browser restart check, point `INCANTA_PERSONALITY_PATH` at a temporary synthetic object and `INCANTA_DATA_DIR` at temporary storage, then launch `python frontend_app.py`. Check unloaded readiness, send one synthetic message and verify one event. Stop the process, restart with the same temporary settings, and confirm status does not initialize inference and the memory reader reloads that event. The browser transcript and gauges may reset in M1; this is not the MVP continuity gate.

Record only OS/hardware, runtime version/build settings, model identity/checksum and pass/fail. Do not publish local paths, prompts, responses, weights or histories. The recorded native/separate-process gate passed on 2026-11-17. M1 delivery remains pending until reviewed-delivery gates pass.
