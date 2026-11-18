# Tasks: Local Celeste portraits and scenes

**Date:** 2026-11-17. **Status:** Implementation and verification are in progress. See [verification.md](verification.md).

**Input:** [spec](spec.md), [plan](plan.md), [research](research.md), [data model](data-model.md), contracts and [validation](quickstart.md). Tests are explicitly required by the spec; add regression tests before implementation and verify they fail for the missing behavior.

**Format:** `- [ ] Tnnn [P?] [USn?] description with paths`. [P] indicates independent files only; it does not require additional agents.

## Phase 1 — Setup

Require 002 contracts and explicit local asset ownership; no model-backed setup as a side effect of tests.

- [X] T001 Document and inspect authorized existing renderer/reference/LoRA configuration in SETUP.md; record compatibility findings in specs/003-local-character-visuals/verification.md without private paths/assets. (FR-001, FR-009)
- [X] T002 Add loopback renderer/root settings in backend/config.py and job/identity/asset schema in backend/migrations/002_visuals.sql; keep models/render dependencies separate from requirements-test.txt. (FR-001, FR-002, FR-003, FR-004)

## Phase 2 — Foundation

Establish tested workflow export, adapter ownership and one heavy resource lease.

- [X] T003 [P] Add fake HTTP/capability/workflow serialization tests in tests/test_rendering.py, including Photoshoot hidden inputs, bounded responses and unsafe output descriptors. (FR-002, FR-005, FR-010)
- [X] T004 [P] Add resource-handoff/failure/priority tests in tests/test_resources.py using fake LLM/renderer lifecycle. (FR-006, FR-008, FR-010)
- [X] T005 Implement resolved workflow/node binding validation in backend/rendering/workflow.py with synthetic examples/render-workflow.example.json; pin tested ComfyUI/Photoshoot revisions in SETUP.md. (FR-001, FR-002)
- [X] T006 Implement submit/poll/cancel_owned/release_owned_resources in backend/rendering/comfyui_adapter.py; fixed loopback endpoints, owned IDs, finite timeouts, no global interrupt or blind resubmit. (FR-002, FR-004, FR-005)
- [X] T007 Implement single lease and next-idle chat/manual/background priority in backend/resource_manager.py; add explicit native unload to backend/llm_interface.py and reject unsafe shared-renderer resource handoff. (FR-006, FR-008)

## Phase 3 — US1: approved identity

Independent test: fake approved portrait stays scoped/displayable when renderer disappears; owner native face review is separate.

- [X] T008 [US1] Test visual identity ownership, explicit approval and safe asset serving in tests/test_render_jobs.py; media types "image/png|image/jpeg|image/webp", byte count "1–20971520", dimensions "1–8192 pixels per axis". (FR-001, FR-003, FR-010)
- [X] T009 [US1] Implement identity revisions, validated atomic artifact storage and approved portrait selection in backend/rendering/jobs.py; reject path traversal/symlink/type mismatches. (FR-001, FR-003, FR-007)
- [X] T010 [US1] Add identity/status/portrait/asset routes in frontend_app.py and portrait/approval UI in frontend/visuals.js and frontend/index.html; retain last approved image during failures. (FR-001, FR-003, FR-008)
- [ ] T011 [US1] Export resolved Photoshoot API workflow locally and headlessly verify identity/wardrobe/expression inputs; record owner portrait verdict and hashes in specs/003-local-character-visuals/verification.md. (FR-001, FR-002, FR-009, SC-001)

## Phase 4 — US2: manual jobs and recovery

Independent test: one successful result per request through timeout/restart/cancel/stale-context cases.

- [X] T012 [US2] Test duplicate submit, restart reconciliation, unknown ID, cancellation and stale revision in tests/test_render_jobs.py before worker implementation. (FR-004, FR-005, FR-007, FR-010, SC-002, SC-004)
- [X] T013 [US2] Implement durable job transitions/reconciliation and idempotency in backend/rendering/jobs.py; scene description "1–2000 characters", one running render, five pending manual requests globally and total pending limit ten. (FR-002, FR-004, FR-005, FR-007)
- [X] T014 [US2] Add scoped image job/list/cancel routes in frontend_app.py, enforcing request IDs, same-origin/CSRF protection and controlled cancellation status. (FR-003, FR-004, FR-005)
- [X] T015 [P] [US2] Add UI queued/running/error/retry/cancel tests in tests/visuals.test.js. (FR-005, FR-008, FR-010)
- [X] T016 [US2] Implement nonblocking progress/manual request/cancel/retry display in frontend/visuals.js and frontend/style.css; uncertain submission requires reconciliation/explicit resolution. (FR-004, FR-005, FR-008)

## Phase 5 — US3: automatic scenes

Independent test: fake-clock cooldown/coalescing, default off and manual priority at idle boundary.

- [X] T017 [US3] Add default-off/cooldown/coalescing/priority/toggle-off tests in tests/test_render_jobs.py using fake time/resources. (FR-006, FR-007, FR-010, SC-003)
- [X] T018 [US3] Implement policy and bounded structured scene proposal parsing in backend/rendering/jobs.py and backend/conversation_service.py; cooldown_seconds "60–3600", default 300, one pending automatic job per conversation. (FR-006, FR-007)
- [X] T019 [US3] Add per-chat policy route in frontend_app.py and toggle/cooldown UI in frontend/visuals.js; manual request outranks unstarted automatic work without silently interrupting running jobs. (FR-006, FR-008)

## Phase 6 — Cross-cutting verification

Rendering functionality is not face consistency or M2 compatibility evidence.

- [X] T020 Run traversal/type/oversize output, disk failure, stale context, unrelated-job cancellation and renderer-unavailable cases in tests/test_rendering.py and tests/test_render_jobs.py; execute all suites. (FR-003, FR-004, FR-005, FR-007, FR-008, FR-010, SC-002, SC-004)
- [ ] T021 Run explicit native quickstart.md with approved portrait/three scenes, face-match owner verdict, duration/peak memory and LLM/render handoff in specs/003-local-character-visuals/verification.md; record failure rather than adding unapproved training. (FR-008, FR-009, FR-010, SC-001, SC-005)
- [ ] T022 Update SETUP.md, ARCHITECTURE.md and docs/ASSETS.md; review workflow/node licenses, stage only safe files and deliver through reviewed PR, recording gates in specs/003-local-character-visuals/verification.md. (FR-001, FR-009, FR-010)

## Dependencies & Execution Order

Setup → foundation → US1 → remaining stories in their listed order → cross-cutting verification. Tasks touching the same runtime, schema or UI file run sequentially. Each story checkpoint is validated before proceeding. External feature dependencies are named in plan.md; use fake adapters to test boundaries before native acceptance. No native downloads/inference occur in automated checks.

## Parallel Examples

Where marked [P], distinct test files in the same phase may be authored together after prerequisite contracts are understood. Do not run schema mutations, same-file edits or dependent integration tasks in parallel. UI and adapter tests may be independent; their final integration remains sequential.

## Implementation Strategy

Deliver and verify US1 as the first increment, then each remaining story. This is an incremental demonstration, not the complete owner MVP. Native quality/notification/combined release gates remain mandatory. Review settings defaults with their visible controls, preserve private data and record actual outcomes in verification.md. Do not check tasks merely because their design exists.

## Requirement and outcome coverage

| Requirement/outcome | Tasks |
| --- | --- |
| FR-001 | T001, T002, T005, T008, T009, T010, T011, T022 |
| FR-002 | T002, T003, T005, T006, T011, T013 |
| FR-003 | T002, T008, T009, T010, T014, T020 |
| FR-004 | T002, T006, T012, T013, T014, T016, T020 |
| FR-005 | T003, T006, T012, T013, T014, T015, T016, T020 |
| FR-006 | T004, T007, T017, T018, T019 |
| FR-007 | T009, T012, T013, T017, T018, T020 |
| FR-008 | T004, T007, T010, T015, T016, T019, T020, T021 |
| FR-009 | T001, T011, T021, T022 |
| FR-010 | T003, T004, T008, T012, T015, T017, T020, T021, T022 |
| SC-001 | T011, T021 |
| SC-002 | T012, T020 |
| SC-003 | T017 |
| SC-004 | T012, T020 |
| SC-005 | T021 |
