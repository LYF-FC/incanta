# Tasks: Celeste conversations and controlled memory

**Date:** 2026-11-17. **Status:** implementation/automated/browser/short-native verification complete; T022 owner acceptance and T023 reviewed delivery remain open. See [verification.md](verification.md).

**Input:** [spec](spec.md), [plan](plan.md), [research](research.md), [data model](data-model.md), contracts and [validation](quickstart.md). Tests are explicitly required by the spec; add regression tests before implementation and verify they fail for the missing behavior.

**Format:** `- [ ] Tnnn [P?] [USn?] description with paths`. [P] indicates independent files only; it does not require additional agents.

## Phase 1 — Setup

Establish isolated storage/configuration and an explicit transition from M1.

- [X] T001 Document 001 acceptance dependency and local DB configuration in SETUP.md; retain historical requirements.txt and defaults in backend/config.py. (FR-009, FR-010)
- [X] T002 Create migration/connection lifecycle and integrity checks in backend/conversation_store.py and backend/migrations/001_companion.sql; enable foreign keys per connection and preserve existing stores. (FR-002, FR-004, FR-010)

## Phase 2 — Foundation

No inference inside a write transaction; bounded context and local mutation protection precede new routes.

- [X] T003 Add request UUID/idempotency, revision compare-and-commit and failure regression cases in tests/test_conversations.py using temporary DB/fake inference. (FR-004, FR-008, FR-011, SC-002)
- [X] T004 Implement process generation ownership, context snapshots and atomic state commit in backend/conversation_service.py; keep backend/chat_engine.py compatible with 001 reliability invariants. (FR-002, FR-004, FR-008)
- [X] T005 Implement same-origin/CSRF session bootstrap and bounded safe errors in frontend_app.py; validate UUIDs and keep transport limit 64 KiB. (FR-004, FR-010)

## Phase 3 — US1: setup and restart continuity

Independent test: two distinct synthetic chats retain isolated settings, transcript, emotion and gauges across two subprocess restarts.

- [X] T006 [US1] Test setup validation, prompt influence, isolation and subprocess restoration in tests/test_conversations.py; title "1–120 characters", personality "1–2000 characters", relationship "0–1000 characters", boundaries "1–2000 characters", gauges "0–100". (FR-001, FR-002, FR-003, FR-011, SC-001)
- [X] T007 [US1] Implement conversation CRUD/read pagination and durable settings/state in backend/conversation_store.py and backend/conversation_service.py; enforce positive settings/context revisions and Turn input "1–8000 characters after trimming". (FR-001, FR-002, FR-004)
- [X] T008 [US1] Replace hard-coded persona with structured settings, permitted facts and bounded recent dialogue in backend/llm_interface.py; reserve output space, trim oldest turns and reject irreducibly oversized context. (FR-003, FR-008)
- [X] T009 [US1] Add conversation/settings/turn routes in frontend_app.py per contracts/http.md, including request replay/conflict and explicit conversation_required for legacy chat. (FR-001, FR-002, FR-004)
- [X] T010 [P] [US1] Add setup, switch/resume and literal transcript UI tests in tests/conversations.test.js. (FR-001, FR-002, FR-011)
- [X] T011 [US1] Implement short form, conversation selector, restored state and error recovery in frontend/index.html, frontend/app.js and frontend/style.css. (FR-001, FR-002, FR-003)

## Phase 4 — US2: controlled facts

Independent test: inspect/save/correct/delete with provenance and reject stale in-flight reply publication.

- [X] T012 [P] [US2] Add provenance, correction/deletion, stale-generation and malformed-fact tests in tests/test_facts.py using fake inference and restart. (FR-005, FR-007, FR-008, FR-011, SC-003)
- [X] T013 [US2] Implement canonical fact revisions/content-free tombstones and transactional context invalidation in backend/fact_store.py; content "1–2000 characters", positive revision, source_turn_id limited to source conversation. (FR-005, FR-007, FR-008)
- [X] T014 [US2] Remove generated-sibling verified-fact heuristic from backend/memory_manager.py active path and route retrieval through permitted current facts in backend/conversation_service.py. (FR-003, FR-005, FR-007)
- [X] T015 [US2] Implement fact mutation/read routes in frontend_app.py and memory inspect/correct/delete controls in frontend/memory_controls.js and frontend/index.html; explain transcript/backup retention. (FR-005, FR-007, FR-008)

## Phase 5 — US3: selected fact sharing

Independent test: share one of two facts; correct/revoke/delete and inspect both contexts after restart.

- [X] T016 [US3] Add two-chat grant/revocation/leakage and correction/delete propagation cases in tests/test_facts.py. (FR-006, FR-007, FR-008, FR-011, SC-003)
- [X] T017 [US3] Implement unique (fact_id, conversation_id) grants and recipient revision updates in backend/fact_store.py; no copied fact content or transcript sharing. (FR-006, FR-007, FR-008)
- [X] T018 [US3] Add grant routes in frontend_app.py and explicit recipient selection/revocation in frontend/memory_controls.js; reject cross-chat source references. (FR-006, FR-007)

## Phase 6 — Cross-cutting verification and legacy preservation

Prove preservation before enabling any owner-selected private import.

- [X] T019 [P] Add interrupted/repeated import, original-byte preservation, duplicates/unknown fields and failed-backup tests in tests/test_legacy_import.py. (FR-009, FR-011, SC-004)
- [X] T020 Implement preview token, checksum-idempotent transactional import and local original preservation in backend/legacy_import.py and frontend_app.py; no auto-scanning or destructive rewrite. (FR-009, FR-010)
- [X] T021 Exercise wrong-origin/CSRF, corrupt/read-only DB, concurrent/repeated requests and settings edit during generation in tests/test_conversations.py; run all Python and Node suites. (FR-004, FR-008, FR-010, FR-011, SC-001, SC-002)
- [ ] T022 Run quickstart.md browser and explicit native 30-minute/restart journey; record owner verdict/timing without content in specs/002-companion-conversations/verification.md. (FR-011, SC-001, SC-005)
- [ ] T023 Update ARCHITECTURE.md, SETUP.md and docs/ASSETS.md; perform staged privacy/checks and reviewed PR delivery, recording failures in specs/002-companion-conversations/verification.md. (FR-009, FR-010, FR-011)

## Dependencies & Execution Order

Setup → foundation → US1 → remaining stories in their listed order → cross-cutting verification. Tasks touching the same runtime, schema or UI file run sequentially. Each story checkpoint is validated before proceeding. External feature dependencies are named in plan.md; use fake adapters to test boundaries before native acceptance. No native downloads/inference occur in automated checks.

## Parallel Examples

Where marked [P], distinct test files in the same phase may be authored together after prerequisite contracts are understood. Do not run schema mutations, same-file edits or dependent integration tasks in parallel. UI and adapter tests may be independent; their final integration remains sequential.

## Implementation Strategy

Deliver and verify US1 as the first increment, then each remaining story. This is an incremental demonstration, not the complete owner MVP. Native quality/notification/combined release gates remain mandatory. Review settings defaults with their visible controls, preserve private data and record actual outcomes in verification.md. Do not check tasks merely because their design exists. T022 has browser and short native evidence but remains unchecked until the owner-reviewed 30-minute criterion passes. T023 has documentation/checks/PR preparation but remains unchecked until reviewed delivery is complete.

## Requirement and outcome coverage

| Requirement/outcome | Tasks |
| --- | --- |
| FR-001 | T006, T007, T009, T010, T011 |
| FR-002 | T002, T004, T006, T007, T009, T010, T011 |
| FR-003 | T006, T008, T011, T014 |
| FR-004 | T002, T003, T004, T005, T007, T009, T021 |
| FR-005 | T012, T013, T014, T015 |
| FR-006 | T016, T017, T018 |
| FR-007 | T012, T013, T014, T015, T016, T017, T018 |
| FR-008 | T003, T004, T008, T012, T013, T015, T016, T017, T021 |
| FR-009 | T001, T019, T020, T023 |
| FR-010 | T001, T002, T005, T020, T021, T023 |
| FR-011 | T003, T006, T010, T012, T016, T019, T021, T022, T023 |
| SC-001 | T006, T021, T022 |
| SC-002 | T003, T021 |
| SC-003 | T012, T016 |
| SC-004 | T019 |
| SC-005 | T022 |
