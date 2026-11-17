# Feature Specification: Local proactive follow-ups

**Feature Branch**: `codex/004-proactive-followups`

**Created**: 2026-11-17

**Status**: Planned; not implemented. Depends on 002 context/store and 003 resource arbitration.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enable and control follow-ups (Priority: P1)

As the owner, I opt into Celeste initiating grounded follow-ups for a conversation and can pause them or set limits.

**Independent Test**: Configure two chats and a fake clock; only the opted-in idle chat generates eligible follow-ups within its limits.

**Acceptance Scenarios**:
1. Given a new chat, when I have not opted in, then Celeste creates no unsolicited follow-up or notification.
2. Given opt-in and an eligible due time, when the app runs awake and I am not actively messaging, then Celeste may create a relevant follow-up using only that chat's current settings and permitted memories.
3. Given pause, quiet hours, new user activity or changed/deleted source memory, when work is due or in progress, then work is deferred/cancelled or its obsolete result is discarded.

### User Story 2 - Receive a Mac notification (Priority: P1)

As the owner, I receive a generic Mac notification for a saved follow-up while Incanta runs, even if its browser is closed.

**Independent Test**: Fake notifier covers success/denied/failed/uncertain delivery; a separate native check with the browser closed verifies actual Mac delivery.

**Acceptance Scenarios**:
1. Given granted local notification permission, when a follow-up is durably saved, then Incanta attempts a generic notification with no private conversation content.
2. Given permission denied, unavailable helper or delivery failure, when follow-up generation succeeds, then the saved message remains available in the inbox without repeated permission prompts or duplicate message creation.
3. Given repeated scheduler ticks/restart, when the same due item is encountered, then no duplicate durable follow-up appears; uncertain OS display is not claimed as exactly-once delivery.

### User Story 3 - Return after absence or sleep (Priority: P2)

As the owner, I see missed follow-ups when returning, without a burst of notifications after sleep/restart.

**Independent Test**: Advance a fake clock across quiet hours, sleep and restart; overdue schedules coalesce and unread inbox entries remain available.

**Acceptance Scenarios**:
1. Given the app/Mac was unavailable, when it resumes, then relevant overdue work is coalesced rather than replayed for every missed interval.
2. Given unread follow-ups, when I return, then I can open the owning conversation, mark them read and see their actual generation time.
3. Given no current relevant source, when overdue work is reconsidered, then it is skipped rather than inventing a remembered event or pretending it was sent while asleep.

### Edge Cases

Clock/timezone changes, daylight saving, Mac sleep, process crash, multiple scheduler startup attempts, inference failure, notification permission revoked, native helper missing, focus changes in multiple tabs, generated follow-up racing user input, same due item claimed twice, stale memory/settings or deleted conversation, resource lease unavailable and ambiguous OS delivery.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Offer per-chat opt-in, pause, quiet hours, minimum idle interval, cooldown and daily cap with visible effective values; default off. Changing settings persists across restart.
- **FR-002**: Generate only from the selected chat's current settings, committed history and permitted facts. Preserve provenance; never invent source events or access other transcripts. Ineligible contexts may be skipped.
- **FR-003**: Check opt-in, user activity, quiet hours, rate limits and context revisions before generation and again before commit; foreground chat/manual images take priority over unstarted proactive work.
- **FR-004**: Persist a uniquely identified due item and follow-up/inbox entry before notification. Duplicate ticks/restarts must not create duplicate committed follow-ups. Failure preserves existing state and uses bounded retries.
- **FR-005**: Deliver generic Mac notifications while the app runs with the Mac awake, independent of browser presence. Ask for notification permission only through an explicit owner action; permission denial/helper failure preserves the inbox.
- **FR-006**: Keep notification previews free of generated text, character settings, remembered facts and private paths. Notification identifiers contain opaque IDs only; OS acknowledgement is not proof the owner saw it.
- **FR-007**: Show unread/missed follow-ups on return in the owning chat, with actual generation time/read state and a route back to pause controls.
- **FR-008**: Coalesce wake/restart backlog into at most one eligible new follow-up per opted-in chat, re-evaluated against current context/limits. Never generate while asleep/stopped or imply historical delivery.
- **FR-009**: Use one local scheduler under process ownership with durable claims/recovery, no cloud push, email/SMS service, automatic login item or always-on service installation.
- **FR-010**: Automate acceptance using fake clock/inference/notifier and temporary persistence; verify actual native permissions/delivery and browser-closed behavior separately on the target Mac.

### Key Entities *(include if feature involves data)*

Follow-up policy, user activity heartbeat, due item/claim, generated follow-up, inbox read state, notification attempt and application process ownership.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Disabled, paused, active-user and quiet-hour cases produce zero follow-ups/notification attempts in deterministic tests.
- **SC-002**: One hundred repeated ticks for one due item across restart commit at most one follow-up; failed/denied notification attempts never duplicate it.
- **SC-003**: A simulated 24-hour absence creates at most one eligible catch-up per conversation and respects the remaining daily/global limits; no notification burst.
- **SC-004**: Memory/settings change during generation prevents obsolete publication; inspecting both test conversations finds zero cross-chat facts or transcripts.
- **SC-005**: With explicit permission on the target Mac and browser closed, a saved follow-up triggers a generic notification; with permission denied the same follow-up remains readable on return. Record observed outcomes, not promised OS display guarantees.

## Assumptions

Single owner/app process; English. Incanta must run and the Mac must be awake for generation. No cloud/mobile delivery or automatic background launch. Owner approved Mac notifications and missed follow-ups on return; numeric timing defaults are reversible engineering choices, documented in the plan. In-app memory deletion excludes old transcripts/backups as specified in 002. Native notification packaging is part of this increment, not an assumed installed capability.
