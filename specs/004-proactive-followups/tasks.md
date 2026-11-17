# Tasks: Local proactive follow-ups

**Date:** 2026-11-17. **Status:** planned; every implementation task is intentionally unchecked.

**Input:** [spec](spec.md), [plan](plan.md), [research](research.md), [data model](data-model.md), contracts and [validation](quickstart.md). Tests are explicitly required by the spec; add regression tests before implementation and verify they fail for the missing behavior.

**Format:** `- [ ] Tnnn [P?] [USn?] description with paths`. [P] indicates independent files only; it does not require additional agents.

## Phase 1 — Setup

Require 002 store/context and 003 resource interfaces; fake adapters avoid native installs in CI.

- [ ] T001 Add policy/due/inbox/attempt schema in backend/migrations/003_proactive.sql and safe configuration in backend/config.py; default opt-out and explicit timezone. (FR-001, FR-004, FR-009)
- [ ] T002 Specify native bundle build/install and browser-closed validation in SETUP.md; no launch agent/login item installation. (FR-005, FR-009, FR-010)

## Phase 2 — Foundation

One durable scheduler owner and independent notifier interface precede background generation.

- [ ] T003 Add fake clock/resource/inference/notifier helpers and transactional claim/restart tests in tests/test_proactive.py. (FR-003, FR-004, FR-008, FR-010, SC-002)
- [ ] T004 Implement due claims, process-singleton startup/shutdown and safe recovery in backend/proactive/scheduler.py; unique due key and attempt_count "0–2" with one delayed retry after 15 minutes. (FR-004, FR-008, FR-009)
- [ ] T005 Define safe notifier result/status interfaces and fake implementation in backend/proactive/notifier.py; do not prompt/request permission on app startup. (FR-005, FR-006, FR-010)

## Phase 3 — US1: controlled grounded initiative

Independent test: disabled/paused/active/quiet contexts generate nothing; edits during generation prevent publication.

- [ ] T006 [US1] Test opt-in, active-user, quiet hours, stale context and grounded-source isolation in tests/test_proactive.py. (FR-001, FR-002, FR-003, FR-010, SC-001, SC-004)
- [ ] T007 [US1] Implement policy rules in backend/proactive/policy.py: min_idle_minutes "5–240", cooldown_minutes "15–1440", daily_cap "0–10", global cap "0–20"; defaults 15/60/2/4, quiet 22:00–08:00 Europe/Paris. (FR-001, FR-003, FR-008)
- [ ] T008 [US1] Implement resource-aware generation, precommit eligibility/revision rechecks, provenance and transactional cap reservation in backend/proactive/scheduler.py and backend/proactive/inbox.py; no generated facts or fake user turns. (FR-002, FR-003, FR-004)
- [ ] T009 [US1] Add policy/activity routes in frontend_app.py; heartbeat interval 30 seconds and expiry 90 seconds, server timestamps authoritative. (FR-001, FR-003)
- [ ] T010 [US1] Add policy controls/heartbeat tests in tests/followups.test.js, then visible settings/opt-in/pause in frontend/followups.js and frontend/index.html. (FR-001, FR-003, FR-010)

## Phase 4 — US2: Mac notification

Independent test: fake denial/failure/uncertainty keeps one inbox message; native Mac test separately proves browser-closed delivery.

- [ ] T011 [P] [US2] Test fixed generic previews, permission states, attempted-before-dispatch and ambiguous notification recovery in tests/test_notifications.py. (FR-004, FR-005, FR-006, FR-010, SC-002)
- [ ] T012 [US2] Implement stable-identity UserNotifications bundle in native/notifications/IncantaNotifications.swift and native/notifications/Info.plist plus scripts/build-notifications.sh; explicit install/authorize only. (FR-005, FR-006, FR-009)
- [ ] T013 [US2] Implement fixed executable argument-array invocation/timeout/status in backend/proactive/notifier.py, generic text/opaque ID only and no private output logging. (FR-005, FR-006)
- [ ] T014 [US2] Wire saved inbox notification attempts and global 15-minute notification spacing in backend/proactive/scheduler.py; uncertain attempts do not automatically re-alert or regenerate text. (FR-004, FR-005, FR-006, FR-008)
- [ ] T015 [US2] Add status/explicit authorization routes in frontend_app.py and permission/recovery UI in frontend/followups.js; preserve inbox under denied permission. (FR-005, FR-006)

## Phase 5 — US3: absence and return

Independent test: 24-hour absence coalesces backlog and preserves actual timestamps/read state without notification bursts.

- [ ] T016 [US3] Test 24-hour absence, daylight-saving/clock changes, repeated startup and existing unread inbox in tests/test_proactive.py and tests/followups.test.js. (FR-007, FR-008, FR-010, SC-003)
- [ ] T017 [US3] Implement at-most-one eligible wake candidate per chat, quiet/cap rechecks and actual generation timestamps in backend/proactive/scheduler.py. (FR-003, FR-008)
- [ ] T018 [US3] Implement scoped paginated inbox/read routes in frontend_app.py and return-to-chat/unread controls in frontend/followups.js; read state persists via backend/proactive/inbox.py. (FR-007, FR-008)

## Phase 6 — Cross-cutting verification

Do not treat OS acceptance as proof of delivery seen by owner.

- [ ] T019 Run all fake-clock/race/restart/denial/error suites; verify 100 ticks give at most one durable follow-up in tests/test_proactive.py and tests/test_notifications.py. (FR-002, FR-003, FR-004, FR-010, SC-001, SC-002, SC-003, SC-004)
- [ ] T020 Run explicit Mac authorized/browser-closed and denied-permission inbox checks plus sleep/restart quickstart.md; record real helper/OS outcomes in specs/004-proactive-followups/verification.md without private content. (FR-005, FR-006, FR-007, FR-008, FR-010, SC-005)
- [ ] T021 Update OPERATIONS.md, SETUP.md and docs/TESTING.md; check Swift build and Bash syntax, staged privacy/checks and reviewed PR delivery in specs/004-proactive-followups/verification.md. (FR-009, FR-010)

## Dependencies & Execution Order

Setup → foundation → US1 → remaining stories in their listed order → cross-cutting verification. Tasks touching the same runtime, schema or UI file run sequentially. Each story checkpoint is validated before proceeding. External feature dependencies are named in plan.md; use fake adapters to test boundaries before native acceptance. No native downloads/inference occur in automated checks.

## Parallel Examples

Where marked [P], distinct test files in the same phase may be authored together after prerequisite contracts are understood. Do not run schema mutations, same-file edits or dependent integration tasks in parallel. UI and adapter tests may be independent; their final integration remains sequential.

## Implementation Strategy

Deliver and verify US1 as the first increment, then each remaining story. This is an incremental demonstration, not the complete owner MVP. Native quality/notification/combined release gates remain mandatory. Review settings defaults with their visible controls, preserve private data and record actual outcomes in verification.md. Do not check tasks merely because their design exists.

## Requirement and outcome coverage

| Requirement/outcome | Tasks |
| --- | --- |
| FR-001 | T001, T006, T007, T009, T010 |
| FR-002 | T006, T008, T019 |
| FR-003 | T003, T006, T007, T008, T009, T010, T017, T019 |
| FR-004 | T001, T003, T004, T008, T011, T014, T019 |
| FR-005 | T002, T005, T011, T012, T013, T014, T015, T020 |
| FR-006 | T005, T011, T012, T013, T014, T015, T020 |
| FR-007 | T016, T018, T020 |
| FR-008 | T003, T004, T007, T014, T016, T017, T018, T020 |
| FR-009 | T001, T002, T004, T012, T021 |
| FR-010 | T002, T003, T005, T006, T010, T011, T016, T019, T020, T021 |
| SC-001 | T006, T019 |
| SC-002 | T003, T011, T019 |
| SC-003 | T016, T019 |
| SC-004 | T006, T019 |
| SC-005 | T020 |
