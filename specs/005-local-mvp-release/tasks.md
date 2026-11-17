# Tasks: Reproducible local companion MVP

**Date:** 2026-11-17. **Status:** planned; every implementation task is intentionally unchecked.

**Input:** [spec](spec.md), [plan](plan.md), [research](research.md), [data model](data-model.md), contracts and [validation](quickstart.md). Tests are explicitly required by the spec; add regression tests before implementation and verify they fail for the missing behavior.

**Format:** `- [ ] Tnnn [P?] [USn?] description with paths`. [P] indicates independent files only; it does not require additional agents.

## Phase 1 — Setup

Component 001–004 acceptance is prerequisite to release, while documentation/test scaffolding can be prepared earlier.

- [ ] T001 Create evidence-gate checklist in docs/MVP_ACCEPTANCE.md tracing every 001–004 native/owner/manual prerequisite; leave all unverified gates pending. (FR-005, FR-006, FR-008)
- [ ] T002 Document runtime/build/model/workflow/helper compatibility evidence format in docs/RUNTIME_COMPATIBILITY.md without private paths/media. (FR-001, FR-002, FR-007)

## Phase 2 — Foundation

Maintenance must prevent mutable asset/DB state from drifting while taking a consistent backup.

- [ ] T003 Add schema/integrity/path checks and maintenance gate interfaces in backend/backup.py, integrated with backend/conversation_service.py and backend/rendering/jobs.py. (FR-003, FR-004)
- [ ] T004 [P] Create combined synthetic state fixtures in tests/test_mvp_journey.py using temporary DB, fake inference/renderer/notifier and no private assets. (FR-005, SC-002)

## Phase 3 — US1: reproducible setup

Independent test: clean lightweight setup plus separate native target-Mac installation evidence.

- [ ] T005 [US1] Review direct/native dependencies and licenses in requirements-test.txt, requirements-inference.txt and SETUP.md; preserve requirements.txt historical snapshot; pin selected runtime/build instructions from measured evidence. (FR-001, FR-002)
- [ ] T006 [US1] Rehearse clean-environment model-free setup and missing/disconnected-asset readiness; record actual versions/results in specs/005-local-mvp-release/verification.md. (FR-001, FR-002, FR-005, SC-001)
- [ ] T007 [US1] Document separately installed renderer/Photoshoot/notification helper and owned asset configuration in SETUP.md and docs/RUNTIME_COMPATIBILITY.md; no implicit model downloads or future-machine compatibility claim. (FR-001, FR-002, FR-007)

## Phase 4 — US2: backup and restore

Independent test: restore two chats/shared memories/assets/unread inbox into new empty root, refusing corruption/overwrite.

- [ ] T008 [US2] Add round-trip, corruption, schema, traversal/symlink, disk failure, missing asset and nonempty-destination tests in tests/test_backup_restore.py before CLI implementation. (FR-003, FR-004, FR-005, SC-002)
- [ ] T009 [US2] Implement maintenance drain/gate, sqlite3 backup, immutable asset snapshot, hashes/private manifest and atomic publication in backend/backup.py and scripts/backup_incanta.py; refuse existing target. (FR-003, FR-004)
- [ ] T010 [US2] Implement verify-only restore and validated staged publication in scripts/restore_incanta.py and backend/backup.py; reject live/nonempty target, preserve originals and neutralize old claims/notification replay. (FR-004)
- [ ] T011 [US2] Rehearse synthetic restoration and restart, including corrected/deleted shared facts and portrait/three scene/inbox references; record outcome in specs/005-local-mvp-release/verification.md. (FR-003, FR-004, FR-005, SC-002)
- [ ] T012 [US2] Document private backup handling, old deleted-content retention and explicit restore/recovery in OPERATIONS.md and docs/ASSETS.md; no cloud upload. (FR-003, FR-004)

## Phase 5 — US3: owner MVP acceptance

Independent test: actual 30-minute conversation, process restart and three owner-approved reference-matching scenes on M2/16 GB.

- [ ] T013 [US3] Add combined fake journey and failure recovery regression cases in tests/test_mvp_journey.py, retaining isolated setup/shared-fact/memory controls and proactive inbox checks. (FR-005, FR-006, SC-004)
- [ ] T014 [US3] Run real owner acceptance from quickstart.md and docs/MVP_ACCEPTANCE.md: 30-minute English dialogue, restart continuity, three distinct face-consistent scenes, memory controls and browser-closed/denied-permission notification checks. (FR-005, FR-006, SC-003)
- [ ] T015 [US3] Record OS/chip/RAM, runtime/model/workflow/helper revisions, measured chat/image durations, peak memory, handoff errors/recovery and explicit owner verdict in specs/005-local-mvp-release/verification.md; no private dialogue/images. (FR-002, FR-006, FR-007, SC-003)

## Phase 6 — Cross-cutting release review

Release is gated by evidence and review, not checked planning boxes.

- [ ] T016 Run all Python/Node suites, modified JS/Bash checks, staged repository checker and git diff --cached --check; review private artifacts and recorded gates in docs/MVP_ACCEPTANCE.md. (FR-005, FR-008, SC-004)
- [ ] T017 Prepare reviewed commits/PRs and release notes in CHANGELOG.md; update ROADMAP.md only from actual gates, and tag only after every mandatory pass plus owner acceptance. (FR-008, SC-004)

## Dependencies & Execution Order

Setup → foundation → US1 → remaining stories in their listed order → cross-cutting verification. Tasks touching the same runtime, schema or UI file run sequentially. Each story checkpoint is validated before proceeding. External feature dependencies are named in plan.md; use fake adapters to test boundaries before native acceptance. No native downloads/inference occur in automated checks.

## Parallel Examples

Where marked [P], distinct test files in the same phase may be authored together after prerequisite contracts are understood. Do not run schema mutations, same-file edits or dependent integration tasks in parallel. UI and adapter tests may be independent; their final integration remains sequential.

## Implementation Strategy

Deliver and verify US1 as the first increment, then each remaining story. This is an incremental demonstration, not the complete owner MVP. Native quality/notification/combined release gates remain mandatory. Review settings defaults with their visible controls, preserve private data and record actual outcomes in verification.md. Do not check tasks merely because their design exists.

## Requirement and outcome coverage

| Requirement/outcome | Tasks |
| --- | --- |
| FR-001 | T002, T005, T006, T007 |
| FR-002 | T002, T005, T006, T007, T015 |
| FR-003 | T003, T008, T009, T011, T012 |
| FR-004 | T003, T008, T009, T010, T011, T012 |
| FR-005 | T001, T004, T006, T008, T011, T013, T014, T016 |
| FR-006 | T001, T013, T014, T015 |
| FR-007 | T002, T007, T015 |
| FR-008 | T001, T016, T017 |
| SC-001 | T006 |
| SC-002 | T004, T008, T011 |
| SC-003 | T014, T015 |
| SC-004 | T013, T016, T017 |
