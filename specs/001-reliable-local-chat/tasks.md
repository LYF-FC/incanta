# Tasks: reliable local chat

**Status:** delivered in merged PR #7; runtime/native/hosted-CI/review gates passed. **Input:** [spec](spec.md), [plan](plan.md), [research](research.md), [data model](data-model.md), [HTTP contract](contracts/http.md). Checked tasks reflect implementation/review status; verification results are in verification.md; reviewed-delivery gate passed when PR #7 merged on 2026-11-17. `[USn]` maps to the spec's user story. Tasks run in order except explicitly independent verification preparation.

## Phase 1 — Foundation

- [X] T001 Add reviewed lightweight test dependencies in `requirements-test.txt` and fake inference/temporary-storage helpers in `tests/helpers.py`; preserve historical `requirements.txt`.
- [X] T002 Add root-anchored, validated settings in `backend/config.py` for model, character, data and loopback runtime/generation settings described in the plan.

## Phase 2 — US1: startup and configuration

- [X] T003 [US1] Add failing import/startup/missing-asset and status-contract tests in `tests/test_app.py`, covering FR-001–FR-003 and the SC-001 fake-backed timing boundary.
- [X] T004 [US1] Refactor `backend/llm_interface.py` into an injected lazy local adapter; separate pure prompt building from model initialization; test no initialization on import/status in `tests/test_llm_interface.py`.
- [X] T005 [US1] Create the app factory/wiring in `frontend_app.py`; keep HTTP/static routes available without configured assets and disable debug/reloader by default.
- [X] T006 [US1] Implement readiness, configuration validation and safe stable errors in `frontend_app.py` and the adapter; align `/api/status` with `contracts/http.md` and initial display in `frontend/app.js`.

**Checkpoint:** interface/status are usable without a model, and injected inference permits subsequent tests. Real generation is not yet claimed ready.

## Phase 3 — US2: one coherent committed turn

- [X] T007 [US2] Add failing tests in `tests/test_memory_manager.py` and `tests/test_chat_engine.py` for ten successful appends, zero failed/busy appends, atomic replacement failure, malformed/read-only history and preservation of unknown existing fields/duplicates.
- [X] T008 [US2] Implement a single append/atomic-replace path in `backend/memory_manager.py`; retain file shape and malformed originals; eliminate duplicate timeline writes in the active path.
- [X] T009 [US2] Refactor `backend/chat_engine.py` to own state once, compute tentative updates and publish only after persistence; rollback on failure and reject overlap under one nonblocking processing lock.
- [X] T010 [US2] Add failing deterministic gauge/precedence tests in `tests/test_gauge_engine.py` reaching three non-neutral emotions and checking bounds; move Neutral to fallback and control variation in `backend/gauge_engine.py`.
- [X] T011 [US2] Align successful/error responses with committed state in `frontend_app.py`; remove inactive duplicate history ownership from the active path and document `core/state.py` as legacy in `ARCHITECTURE.md`.

**Checkpoint:** FR-005–FR-007 and FR-009 hold with fake inference and temporary storage. Existing private files have not been migrated.

## Phase 4 — US3: validation and safe UI recovery

- [X] T012 [US3] Add failing request-validation tests in `tests/test_app.py`: wrong content type, malformed/non-object JSON, missing/non-string/blank message, 8,000-character boundary and 64 KiB transport cap.
- [X] T013 [US3] Implement input/transport limits and structured error mapping in `frontend_app.py`; validate before generation or mutations and keep errors/logs free of raw contents/paths.
- [X] T014 [US3] Add synthetic frontend regression cases in `tests/frontend.test.js` for literal markup rendering, server/network error handling and restoring submit state.
- [X] T015 [US3] Replace raw HTML insertion, lock in-flight submissions, check HTTP status and restore controls in `frontend/app.js`; extract `frontend/chat_helpers.js` only if needed for tests and reference it from `frontend/index.html`.
- [X] T016 [US3] Exercise two concurrent requests and injected adapter/storage failures in `tests/test_chat_engine.py` and `tests/test_app.py`; ensure no duplicate generation, history or published state.

## Phase 5 — Verification and documentation

- [X] T017 Extend `.github/workflows/repository.yml` to run the new lightweight application and frontend suites, retaining no-model/no-private-data guarantees; record relevant results in this feature's verification note.
- [X] T018 Perform the synthetic browser journey and failure checks in `quickstart.md`; record outcomes without conversation contents in `verification.md`.
- [X] T019 Update `SETUP.md`, `README.md`, `ARCHITECTURE.md`, `docs/ASSETS.md` and `docs/REPOSITORY_AUDIT.md` to match implemented settings/contracts/limitations, preserving unresolved M2/M3 findings.
- [X] T020 Perform the explicit manual local-model/restart check in `quickstart.md`; record non-sensitive environment and pass/fail in `verification.md`. If unavailable, leave this task and M1 pending.
- [X] T021 Review requirements/plan/tasks and constitution again; run relevant checks and staged privacy review, open/merge the feature PR, and update `ROADMAP.md` only when all exit gates are met.

## Traceability

| Requirement | Tasks |
| --- | --- |
| FR-001 | T003–T005 |
| FR-002 | T003, T006, T011 |
| FR-003 | T002–T006 |
| FR-004 | T012–T013 |
| FR-005 | T007–T009, T011 |
| FR-006 | T007–T009, T016 |
| FR-007 | T009–T010 |
| FR-008 | T014–T016, T018 |
| FR-009 | T009, T015–T016 |
| FR-010 | T002, T005–T006, T013, T019 |
| FR-011 | T001, T003, T007, T010, T012, T014, T016–T017 |
| FR-012 | T020–T021 |

SC-001 is checked by T003; SC-002 by T007/T016; SC-003 by T010; SC-004 by T014/T016/T018; SC-005 by T020. T019/T021 reconcile shared guidance after behavior is verified.

## Dependencies and execution

T001–T002 underpin all stories. US1 establishes app/adapter wiring needed by the turn and UI integration; US2 can be tested independently using fake adapters, and US3 display helpers can be tested independently with synthetic text. Each later integration depends on the earlier foundation, not on a real model. Do not mark a test-first task complete until its regression fails on old behavior and passes after the corresponding change. No automatic retries, multi-worker support or historical memory deduplication are added by this task list.
