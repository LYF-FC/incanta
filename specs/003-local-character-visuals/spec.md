# Feature Specification: Local Celeste portraits and scenes

**Feature Branch**: `codex/003-local-character-visuals`

**Created**: 2026-11-17

**Status**: Implementation and verification in progress. Owner face-match acceptance is tracked in [verification.md](verification.md).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Establish Celeste's visual identity (Priority: P1)

As the owner, I configure Celeste's photorealistic identity using local references and an available character adapter, then approve a portrait that closely matches her face.

**Independent Test**: With a fake renderer verify configuration/readiness and approved-portrait display; separately have the owner assess actual local renders against private references.

**Acceptance Scenarios**:
1. Given local references and a configured rendering workflow, when I request a portrait, then I can inspect and explicitly approve/reject it without changing the conversation's personality.
2. Given missing assets or an unavailable renderer, when I open chat, then the last approved portrait remains visible if available and text conversation/history remain usable.
3. Given a different chat, when its visual settings change, then no image appears in the wrong conversation and private references are not exposed in logs or shared files.

### User Story 2 - Request a scene and keep control (Priority: P1)

As the owner, I request scenes during conversation, see progress, cancel queued work and recover from failures while retaining previous images and chat.

**Independent Test**: Submit, poll, cancel and retry fake jobs, including unknown submission outcome and process restart, with exactly one committed result per request.

**Acceptance Scenarios**:
1. Given an image request, when work is queued/running, then I see its state and can continue using the interface; heavy computation may serialize and must be explained visibly.
2. Given cancellation or a failed/uncertain renderer request, when I return/restart, then the app reconciles the owned job without blind duplicate submission or false success.
3. Given settings/memory changed during rendering, when a result arrives, then obsolete output is discarded from current display and can never attach to another chat.

### User Story 3 - Generate automatic scene changes (Priority: P2)

As the owner, I enable automatic scene changes for a chat, choose a cooldown, and retain priority for my manual requests.

**Independent Test**: Use a fake clock and renderer; rapid triggers coalesce, manual requests take priority and toggling off prevents further automatic work.

**Acceptance Scenarios**:
1. Given automatic scenes are disabled, when dialogue changes scene, then no automatic render starts.
2. Given automatic scenes enabled and cooldown elapsed, when a committed turn contains an eligible scene change, then at most one bounded automatic request is queued.
3. Given pending automatic work, when I submit a manual request, then it moves ahead of unstarted automatic work; currently running jobs are not silently interrupted.

### Edge Cases

Offline renderer; missing model/nodes; mismatched workflow schema; private file traversal; malicious output filenames; model memory exhaustion; app crash after submission; timeout with unknown prompt ID; cancellation of work owned by another client; repeated triggers; deleted conversation; settings/facts changed mid-render; failed artifact save; unavailable original reference/LoRA; no approved portrait yet.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Configure local visual identity and an optional existing character adapter, with explicit portrait approval and no automatic download or training. Actual reference files remain local and are never committed or logged.
- **FR-002**: Submit and track local rendering jobs through a validated, versioned workflow; retain the originating conversation, settings/memory revisions and request identifier.
- **FR-003**: Display the approved portrait and scene history only within their owning conversation. Serve private output through bounded local asset identifiers, never arbitrary filesystem paths.
- **FR-004**: Persist queued/running/succeeded/failed/cancelled/uncertain job states and reconcile after restart. At most one successful displayed result per request; an ambiguous submission is not automatically retried.
- **FR-005**: Provide manual scene requests, visible progress/error/retry and cancellation. Cancel only Incanta-owned jobs; report cancellation pending/unsupported honestly and never interrupt unrelated rendering.
- **FR-006**: Automatic scenes are off by default per chat, explicitly enabled, cooldown-controlled and coalesced. Manual requests outrank unstarted automatic jobs; foreground chat outranks unstarted background generation.
- **FR-007**: Reject stale result publication after settings/fact revision changes or conversation removal. Toggling automatic generation off cancels unstarted automatic requests.
- **FR-008**: Keep text/history and the interface recoverable when visuals fail or resources are busy; retain last approved images. Serialize heavy local model work by default, expose waiting, and measure fit on the M2/16 GB instead of assuming simultaneous residency.
- **FR-009**: Render photorealistic scenes with a face closely matching owner references. Several minutes per scene are acceptable. A setup that fails face-match review does not pass the POC; retraining is not silently added to this feature.
- **FR-010**: Verify scheduling, failure, isolation, stale context, asset access and restart through fake rendering and synthetic files; require separate local owner visual/performance acceptance.

### Key Entities *(include if feature involves data)*

Visual identity revision, approved portrait, render request/job, owned renderer handle, private output asset, automatic-scene policy and resource lease.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Owner approves a portrait and three distinct scenes as recognisably the same reference-matching face, with correct conversation attachment; actual references/images stay local.
- **SC-002**: Ten duplicate submissions of one request create at most one displayed result; injected failure/uncertainty/restart never silently duplicates a job.
- **SC-003**: Fake-clock tests show no automatic generation while disabled, at most one queued automatic job per chat, cooldown enforcement and manual priority at the next idle slot.
- **SC-004**: Missing renderer/assets, cancellation, stale context and failed output writes preserve all committed conversation history and last approved images, with a usable recovery control.
- **SC-005**: The M2/16 GB validation records elapsed render time, model/workflow revisions and peak memory for three scenes with no unrecovered process failure. No scene-time upper bound is claimed until measured.

## Assumptions

One local owner, English, still images only; no voice/video/avatar animation, model downloads, LoRA training, cloud rendering or automatic background service installation. Text completion and rendering may serialize. Face acceptance is an owner decision; automatic similarity scoring is not proof. The existing ComfyUI installation and LoRA are unverified inputs to assess, not working dependencies. No public API exposure.
