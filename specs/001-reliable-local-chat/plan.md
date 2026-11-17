# Implementation Plan: Reliable local chat

**Branch**: `001-reliable-local-chat` (existing implementation branch) | **Date**: 2026-11-04 | **Spec**: [spec.md](spec.md)

**Status:** design implemented in the working tree. Automated and synthetic browser checks passed on 2026-11-17; explicit native-model/process-restart check also passed; hosted CI/review passed and PR #7 merged on 2026-11-17. See [verification.md](verification.md).

## Summary

Retain Flask/plain JavaScript. Introduce settings, a web-app factory, lazy injected inference and a single state owner. Make one atomic memory writer the completion boundary, correct emotion precedence, and align status/chat/error responses with safe frontend rendering. Test with fake inference and temporary storage; run real inference only as a separate manual gate.

## Technical Context

**Language/Version:** Python 3.13 is the initial app verification target, based on recovered 3.13.5; repository tooling also runs on 3.11. Establish app support from evidence, not this target alone.

**Primary Dependencies:** Flask; optional `llama-cpp-python` for real inference. Preserve historical `requirements.txt`; add `requirements-test.txt` with reviewed minimal test/web dependencies when implementing T001.

**Storage:** existing JSON memory shape, atomic same-directory temporary write plus `os.replace`, one process lock. No schema migration or private-data deduplication.

**Testing:** stdlib unittest plus Flask test client, fake adapter and temporary storage; Node built-in tests for extracted frontend text/request-state helpers where practical, plus browser smoke evidence.

**Target Platform:** macOS local runtime; model-free test execution also on Linux CI.

**Project Type:** local web app; retain current directory layout.

**Performance Goals:** fake-backed readiness test under two seconds, excluding interpreter/process startup. No unsupported real-model throughput claim.

**Constraints:** offline local inference, no import-time asset access/model initialization, one process/active conversation, local binding, 8,000-character input limit, no sensitive logging.

**Scale/Scope:** one owner and conversation; reject overlap rather than add queues/workers.

## Constitution Check

| Principle | Design check |
| --- | --- |
| Private/local data | Synthetic fixtures, configured ignored data paths; no downloads/cloud fallback or content logging |
| Accurate claims | All target behavior is marked proposed; model-backed evidence remains a manual gate |
| Specification first | FR-001–FR-012 map to tasks and contracts |
| Reproducible checks | Fake inference and temporary storage, scoped lightweight test dependencies |
| Recoverable simplicity | Existing stack/schema retained; atomic writes and no destructive migration |

No exceptions requested. Recheck these gates after implementation and before merge. The design review passes; runtime compliance is supported by the recorded synthetic checks; explicit native-model smoke also passes; reviewed delivery completed through PR #7.

## Project Structure

### Documentation

This directory contains spec, research, data model, quickstart, HTTP contract, tasks, requirements checklist and analysis.

### Proposed source changes

```text
backend/config.py           # settings anchored to repository root or explicit paths
backend/llm_interface.py    # lazy injectable local inference; pure prompt builder
backend/chat_engine.py      # one conversation state and processing lock
backend/memory_manager.py  # load/preserve shape, append once, atomic replacement
backend/gauge_engine.py    # documented precedence and injectable variation
frontend_app.py             # app factory, dependency wiring, validation/contracts
frontend/app.js             # safe rendering, busy/error handling
frontend/chat_helpers.js    # small testable text/request-state helpers if needed
requirements-test.txt       # scoped Flask test dependencies, not model packages
tests/test_app.py
tests/test_chat_engine.py
tests/test_memory_manager.py
tests/test_gauge_engine.py
tests/frontend.test.js
```

Keep `core/state.py` as a documented legacy alternative until references and semantics are reviewed; do not route two state owners through the active chat path.

## Configuration design

Read environment settings `INCANTA_MODEL_PATH`, `INCANTA_PERSONALITY_PATH`, `INCANTA_DATA_DIR`, `INCANTA_HOST`, `INCANTA_PORT`, `INCANTA_CONTEXT_LENGTH`, `INCANTA_GPU_LAYERS`, and `INCANTA_THREADS` in the new settings layer. No `.env` parser is required; document shell exports and provide an example only when supported. Default asset paths remain compatible, anchored to repository root rather than current working directory. Resolve writable history under the configured data directory. Permit loopback bind addresses only in this feature. Invalid settings yield a configuration-not-ready state, not private values in errors.

Importing the web module must not load assets. A lazy local adapter validates/rechecks assets on generation, loads once under the processing lock and reports controlled availability errors. The status endpoint reports configured assets versus actual model-loaded state separately. Unit tests inject an adapter and settings with no real weights.

## Turn transaction design

Validate before acquiring state. A nonblocking process lock rejects overlap with 409. Build tentative recent history/gauges/emotion, generate, append exactly one event to a copy of the existing memory document, write and atomically replace it, then publish in-memory committed state. Release the lock in a finally block. On inference or persistence failure, do not publish tentative state. Error responses do not include generated text or paths. Existing malformed history is preserved and produces a controlled error; no silent empty reset.

Move Neutral to the end of the active gauge rule sequence, retain the existing remaining order for this baseline, and document that order. Inject/control random variation in tests. The unrelated generated-sibling heuristic is removed from the commit path only when that memory behavior is addressed in M2; it remains a known limitation, not a verified factual memory system.

## Complexity Tracking

No new server framework, database, background worker, cloud service or migration is introduced. A process lock and atomic file replacement are bounded to the single-process assumption. If multiple workers become required, stop and specify a different persistence/session model rather than claiming this design covers them.
