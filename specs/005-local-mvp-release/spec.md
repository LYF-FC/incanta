# Feature Specification: Reproducible local companion MVP

**Feature Branch**: `codex/005-local-mvp-release`

**Created**: 2026-11-17

**Status**: Planned; not implemented. Release depends on accepted features 001–004.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install and diagnose the local app (Priority: P1)

As the owner, I can reproduce Incanta's setup on the POC Mac, configure existing local assets and understand unavailable components without exposing private paths.

**Independent Test**: Rehearse a clean software environment using synthetic configuration/fake adapters, then explicitly validate the selected native runtime/workflow on the target Mac.

**Acceptance Scenarios**:
1. Given a clean environment, when I follow reviewed setup instructions, then software dependencies are reproducible and no model/private data is downloaded or copied automatically.
2. Given disconnected storage or unavailable renderer/helper/model, when I launch/check readiness, then I receive specific safe recovery guidance with no data reset/cloud fallback.
3. Given compatible owned assets, when setup is complete, then I can run the accepted conversation, visual and notification journeys locally.

### User Story 2 - Back up and restore (Priority: P1)

As the owner, I can back up conversations, shared memories, settings and generated assets and restore them into a separate local destination without overwriting originals.

**Independent Test**: Restore synthetic state with shared facts/images/unread follow-ups into a new directory, verify consistency, and fail safely on corruption or missing assets.

**Acceptance Scenarios**:
1. Given active local state, when I explicitly back it up, then the backup is consistent, private and has integrity/schema information; weights may be referenced rather than duplicated.
2. Given a valid backup and empty destination, when I restore, then per-chat settings/state, sharing changes, portrait/scene references and unread inbox remain consistent after restart.
3. Given corrupt backup, unsupported schema or nonempty destination, when I restore, then it refuses safely without modifying the source or existing destination.

### User Story 3 - Accept the agreed MVP (Priority: P1)

As the owner, I evaluate a 30-minute Celeste conversation, restart continuity and three reference-matching scenes, with memory controls and follow-ups functioning locally.

**Independent Test**: Complete and record the combined owner journey on the M2/16 GB, with real models only through explicit manual execution.

**Acceptance Scenarios**:
1. Given accepted component checks, when I run a 30-minute English conversation and restart, then I judge personality/boundary adherence, useful memory and continuity satisfactory.
2. Given approved private references, when I generate three different scenes during chat, then I approve consistent face resemblance and can recover from one unavailable-renderer case without losing history.
3. Given opt-in follow-ups and notification permission, when I close the browser/return, then generic Mac delivery and the missed inbox behave as specified; denial preserves inbox access.

### Edge Cases

Missing external drive, incomplete backups, disk full/read-only destination, backup during a memory edit, active inference during backup, missing model/workflow/asset, dependency build incompatibility, unsupported schema, interrupted restore, corrupted checksum, app left open during restore and unreviewed runtime changes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Provide reproducible reviewed setup separating web/tests, native language inference, rendering and notification helper; retain the historical dependency snapshot unchanged. No automatic model download, external inference or private-asset migration.
- **FR-002**: Record supported runtime/build/platform and chosen model/workflow/node revisions from actual evidence; provide actionable readiness and disconnected-storage recovery without private path/content logging.
- **FR-003**: Provide explicit consistent local backup of DB, settings and owned generated assets with schema/integrity manifest; explain that backups contain private data and deleted historical content may remain in older backups. Do not upload/share automatically.
- **FR-004**: Restore only into an empty separately selected destination, validating integrity, schema and contained paths before changes. Preserve source/current state and fail safely on corruption/interruption; restore must not dispatch historical notifications or replay jobs.
- **FR-005**: Run automated end-to-end acceptance with fake adapters/temporary storage, and explicit local native/model/render/notification checks for the real POC. Synthetic success cannot substitute for owner face/dialogue acceptance.
- **FR-006**: Require a recorded owner-approved 30-minute English conversation, restart continuity and three reference-matching consistent scenes, plus per-chat setup/isolation, memory controls/sharing and proactive-notification checks before MVP release.
- **FR-007**: Record measured chat/image timing, memory footprint and resource-handoff outcomes on M2/16 GB, including errors/recovery; do not invent throughput or infer compatibility of future Mac mini/Nomad machines.
- **FR-008**: Deliver through reviewed commits/PRs and checks, with unresolved failures visible. No release tag while mandatory gates fail; no production Butler dependency, public hosting or permanent service installation.

### Key Entities *(include if feature involves data)*

Runtime compatibility record, private backup manifest, restore validation report, acceptance gate and non-sensitive release evidence record.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: One clean-environment setup rehearsal passes with no native/model install required for automated acceptance; the explicit target-Mac native setup is separately recorded.
- **SC-002**: A synthetic backup/restore round trip preserves two conversation states, one corrected shared fact, one deleted fact's exclusion, approved portrait/three scene references and unread inbox; integrity/path/schema failure leaves originals untouched.
- **SC-003**: Owner signs off a 30-minute conversation, continuity after process restart and three face-consistent scenes against private references on M2/16 GB; partial success remains partial.
- **SC-004**: All mandatory component, privacy, backup/restore and reviewed-delivery gates pass with environment/results recorded and no private model/personality/history/media in Git or CI artifacts.

## Assumptions

Private local POC; English; one owner; no target date. Weights/reference images are existing owner-controlled assets. Backup is a private local directory, not a cloud archive. No model redistribution, public installer, commercial launch, new Incanta license selection or future Butler-machine certification. A feature-complete demonstration is not a production service certification.
