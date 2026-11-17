# Feature Specification: Celeste conversations and controlled memory

**Feature Branch**: `codex/002-companion-conversations`

**Created**: 2026-11-17

**Status**: Planned; not implemented. Depends on M1's verified runtime and delivery gates.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set up and resume a conversation (Priority: P1)

As the owner, I start separate English-language Celeste conversations using a short personality and relationship/content-boundary form, and resume each after restarting.

**Independent Test**: Create two synthetic conversations with different settings, exchange turns, restart, and verify each transcript, settings, emotion and gauges restore without cross-chat leakage.

**Acceptance Scenarios**:
1. Given a new conversation, when I complete the short form, then I can review the personality and boundaries before the first reply and they influence its instructions.
2. Given conversations A and B with different settings, when I switch or restart, then each restores its own committed transcript, settings and state; neither uses the other's transcript or relationship state.
3. Given invalid setup, concurrent submissions or a failed save, when I attempt a turn, then it is rejected/recoverable without duplicate or partial durable state.

### User Story 2 - Inspect, correct and delete memories (Priority: P1)

As the owner, I control what Celeste remembers and can see the source of each remembered fact.

**Independent Test**: Save a synthetic fact, inspect its source, correct it, delete it and inspect subsequent generation context after restart.

**Acceptance Scenarios**:
1. Given a conversational detail, when I explicitly save it as a fact, then its text and source are visible; generated dialogue is not automatically treated as verified fact.
2. Given a correction or deletion, when I next generate or resume, then current fact content is used and deleted content is excluded.
3. Given generation already using an old memory/settings snapshot, when I change that snapshot, then its obsolete result is not committed or presented as current.

### User Story 3 - Explicitly share selected facts (Priority: P2)

As the owner, I choose which facts are available in another conversation without sharing its transcript.

**Independent Test**: Use two conversations, share exactly one of two facts, then correct/delete/revoke the shared fact and verify both contexts.

**Acceptance Scenarios**:
1. Given two private facts in A, when I share only one with B, then B sees that fact and its provenance but no other fact, transcript, personality or relationship state from A.
2. Given a fact shared with multiple chats, when corrected/deleted, then every sharing chat sees the correction or loses access to the deleted fact, including after restart.
3. Given a revoked sharing grant, when B generates again, then the fact is unavailable in its future memory context.

### Edge Cases

Corrupt or read-only legacy history; interrupted import; duplicate historical events; unknown legacy fields; oversized forms/facts; missing conversations; conflicting revisions; deletion during active generation; accidental repeated sharing; unavailable native model; read-only database; original source text retained in a transcript after its memory fact is deleted.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Support creating/listing/selecting separate Celeste conversations, with a short English setup form containing personality, relationship description and content boundaries. Display effective settings and allow explicit edits.
- **FR-002**: Persist each conversation's committed turns, settings, seven bounded gauges and emotion, and restore them after process restart without generating a new turn.
- **FR-003**: Build replies from only the selected conversation's settings, committed dialogue and permitted current facts. Character settings must replace the hard-coded persona; the interface must not promise perfect model obedience.
- **FR-004**: Validate bounded input before inference; serialize turns and commit transcript/state atomically. Repeated request identifiers must not create duplicate turns; failure must preserve prior durable state.
- **FR-005**: Let the owner explicitly create, inspect, correct and delete facts, showing their source. No inferred family milestone or generated claim becomes a verified fact automatically.
- **FR-006**: Share selected canonical facts only through explicit grants to named conversations; no transcript, personality or relationship-state sharing is implied.
- **FR-007**: Corrections/deletions must affect all current sharing contexts and survive restart. Revocation removes a recipient's future access. Memory deletion removes fact content from active retrieval, not historical transcript text or existing backups; explain this distinction in the memory controls.
- **FR-008**: Version conversation settings and accessible memory context; discard any pending reply generated against a superseded version before publication/commit, allowing an explicit retry.
- **FR-009**: Import legacy history only through owner-initiated preview, backup and transactional confirmation. Preserve original files, duplicates and unknown fields; interrupted/repeated import must neither destroy data nor duplicate an import.
- **FR-010**: Keep all private state local, preserve missing/corrupt storage, and expose no content or full paths in logs/errors. No automatic downloads, external inference or background contact.
- **FR-011**: Provide automated acceptance with fake inference, two isolated synthetic conversations, temporary persistence, restart, stale-generation and failure-injection tests, plus a separate owner-reviewed native dialogue check.

### Key Entities *(include if feature involves data)*

Conversation, settings revision, committed turn, canonical fact with source/revision, sharing grant, context revision and legacy import record. Operational locks are not conversation memory.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Two distinct conversations retain their settings, transcripts, gauges and emotion after two process restarts, with zero unintended cross-chat items in synthetic reply contexts.
- **SC-002**: Ten successful turns create exactly ten durable turns; validation, busy, stale-context and injected failures create zero additional turns.
- **SC-003**: Of two source facts, only the explicitly shared one reaches the recipient; correction, revocation and deletion each affect the next context in every applicable chat, including after restart.
- **SC-004**: Interrupted and repeated synthetic legacy import preserves the original byte-for-byte and produces at most one imported copy, preserving unknown fields and duplicates.
- **SC-005**: Owner reviews a 30-minute English conversation for configured personality/boundaries, continuity and absence of unsupported remembered facts; failures are recorded as failures, without publishing dialogue.

## Assumptions

One local owner/process; English; existing browser interface. No multi-user authentication, hosted access, automatic fact extraction, semantic search, export UI, image generation or notifications in this increment. Explicit fact saving is the bounded memory MVP. Shared-memory deletion does not rewrite old turns or backups. Resource coordination with rendering is added by feature 003. Planning may proceed while M1's native gate is pending; native acceptance/release cannot.
