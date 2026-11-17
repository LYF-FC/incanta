# Verification strategy

## Automated acceptance

Install the lightweight web dependency from `requirements-test.txt`, then run:

```sh
python -m unittest discover -s tests -v
node --test tests/frontend.test.js
node --check frontend/app.js
node --check frontend/chat_helpers.js
```

Python tests cover import/startup/readiness without assets, request validation and size boundaries, fake-adapter lifecycle, exactly one append per successful turn, preservation of old/unknown memory fields, failure rollback, corrupt/read-only histories, real threaded overlap rejection, emotion precedence/bounds, and repository privacy safeguards. Frontend Node tests cover literal markup display, HTTP/network/invalid-response failure recovery, duplicate submission and retry state.

No automated test downloads or uses a real model/private character/history. Tests use temporary synthetic files. GitHub Actions runs Python on 3.11/3.13, the frontend suite on Node 24, repository checks and Bash syntax validation. The native inference dependency is deliberately not installed in CI.

## Repository safeguards

`python scripts/check_repository.py` checks index blobs; `--tracked` checks HEAD. It detects private/runtime paths, selected credential patterns, binary/large blobs, unexpected symlinks/submodules, exact JSON exceptions and Python syntax. It never prints credential matches. It does not detect all private prose, inspect historical commits or audit package vulnerabilities; manual staged-content review remains necessary.

## Browser and real-model evidence

See [verification 001](../specs/001-reliable-local-chat/verification.md) for the actual environment/results and remaining gates. Browser verification uses a fake adapter and synthetic data. Native inference is a separate manual check, using an already-owned local model and temporary synthetic character/history, not a side effect of test discovery.

Record only date, runtime/build/hardware context, model identity/checksum and pass/fail. Do not attach prompts/responses, private paths, histories or weights. A native-library crash may terminate the interpreter; a passing fake-backed suite does not prove a particular native binary/model combination is compatible. The 2026-11-17 explicit real-model/separate-process restart gate passed; reviewed delivery remains pending. Re-run native checks when the model/runtime changes.

## Companion regression and acceptance (002)

Run `python3 -m unittest discover -s tests -v` and `node --test tests/*.test.js` using the lightweight environment. New suites cover two-chat prompt/state isolation, two subprocess restarts, idempotent ten-turn commits, conservative context limits, wrong-origin/CSRF guards, corruption/read-only/disconnected storage, revision races, canonical facts/grants/deletion, and explicit import backup/rollback/idempotency. Frontend suites cover CSRF transport, explicit retry request identity, stale-view protection and literal memory text.

Existing M1 HTTP tests use `create_app(legacy=True)` intentionally; new tests exercise the default 002 factory and `/api/conversations/{id}/turns`. `scripts/verify_local_model.py` remains the historical native baseline check. `scripts/verify_companion_model.py` explicitly checks the active structured-message/SQLite path with temporary synthetic state and an already-owned local model; it is never called by test discovery or CI. Neither short smoke proves the owner's 30-minute dialogue-quality acceptance.

See [verification 002](../specs/002-companion-conversations/verification.md) for actual browser/native results, owner acceptance status and the distinction between local checks and GitHub jobs that could not start.
