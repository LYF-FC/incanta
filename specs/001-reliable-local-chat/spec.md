# Feature Specification: Reliable local chat

**Feature Branch**: `001-reliable-local-chat` (reserved; create when implementation starts)

**Created**: 2026-11-04

**Status**: Ready for implementation review; application work not started

**Input**: Restart the recovered local conversation project with predictable startup, truthful status, working emotional state, reliable memory and a usable chat interface before adding proactive behavior.

## User Scenarios & Testing

### User Story 1 — Open and configure the local app (Priority: P1)

As the local owner, I can open the interface and understand what is ready even when a model or character file is missing or my model SSD is disconnected.

**Why this priority**: A fresh checkout currently fails before the interface opens.

**Independent Test**: Start with synthetic configuration and no model, then with a fake inference adapter. Observe initial status and recovery guidance without generating a real response.

**Acceptance Scenarios**:

1. **Given** no model or character file, **When** I open the app, **Then** its interface/status are available, gauges and emotion are defined, and missing configuration is explained without private contents or full filesystem paths.
2. **Given** valid configured assets and fake inference, **When** I open the interface, **Then** it displays initial state without generating a response or initializing the model.
3. **Given** a model on disconnected external storage, **When** I try to chat, **Then** I receive an actionable unavailable message, no automatic download/cloud request occurs, and no memory is changed.

### User Story 2 — Complete one coherent conversation turn (Priority: P1)

As the owner, I receive a response with updated gauges/emotion and exactly one stored record of the successful exchange.

**Why this priority**: Duplicate writes and unreachable emotions break continuity.

**Independent Test**: Submit synthetic turns through fake inference to temporary storage, restart the app and inspect the resulting state without private data.

**Acceptance Scenarios**:

1. **Given** a successful generated response, **When** the turn finishes, **Then** one timeline event is added and UI state agrees with the server's returned state.
2. **Given** a controlled emotional input and controlled variation, **When** a non-neutral rule applies, **Then** that rule can be selected and every gauge remains between 0 and 100.
3. **Given** an interrupted/failed storage write, **When** completion is attempted, **Then** the existing history remains readable and the user is not told the turn was saved successfully.
4. **Given** overlapping submissions, **When** one is already processing, **Then** an additional request is rejected as busy without extra inference or memory writes.
5. **Given** pre-existing synthetic history with repeated entries and unknown fields, **When** a new successful turn is stored, **Then** old entries/fields are preserved and only one new entry is appended.

### User Story 3 — Recover from input and display failures (Priority: P2)

As the owner, I can submit normal text safely and retry after a rejected request or temporary failure.

**Why this priority**: Text currently becomes executable markup and failures can break the interface.

**Independent Test**: Use malformed requests, markup-shaped synthetic text and injected inference/storage failures. Verify literal display and a usable retry state.

**Acceptance Scenarios**:

1. **Given** malformed, empty, non-text or oversized input, **When** it is submitted, **Then** it is rejected consistently and produces no stored event or inference request.
2. **Given** user or generated text containing markup, **When** displayed, **Then** it is shown as text and cannot run code.
3. **Given** a server/network failure, **When** the request ends, **Then** I see a useful error and can submit again without an endless loading state.

### Edge Cases

- Read-only storage, invalid character configuration, malformed history and a missing model after startup.
- A fake adapter returning empty text or failing during initial loading; partial state must not be presented as committed.
- Two browser tabs submit concurrently; frontend locking alone is insufficient.
- Existing histories may contain duplicates; this feature must not silently deduplicate or migrate private data.
- A working directory different from the repository root must not redirect writes into an unintended folder.

## Requirements

### Functional Requirements

- **FR-001**: Opening the interface or querying status MUST NOT load a model, invoke inference or require private asset files.
- **FR-002**: Initial and post-turn views MUST provide the same seven gauge names, a defined emotion and truthful readiness information.
- **FR-003**: The owner MUST be able to configure model, character and writable history locations, including external storage, without editing source. Missing assets MUST NOT trigger downloads or remote inference.
- **FR-004**: Input MUST be a nonempty text message after trimming, at most 8,000 characters. Invalid input MUST be rejected before inference or mutation.
- **FR-005**: A successful turn MUST durably append exactly one record with timestamp, input and response. Existing records and unknown stored fields MUST remain intact.
- **FR-006**: Inference or storage failure MUST leave previously durable history intact and MUST NOT advance committed conversation state or report a saved turn.
- **FR-007**: Emotional rules MUST have a documented deterministic precedence, with Neutral as fallback; gauges MUST stay within 0–100.
- **FR-008**: User/model text MUST be rendered literally. The interface MUST show errors and leave submission usable after every completed or failed request.
- **FR-009**: A processing conversation MUST reject overlapping requests without another generation or memory append. No automatic retry may create a second turn.
- **FR-010**: Default operation MUST remain local-only with debug/reloader disabled. Logs/errors MUST NOT expose conversations, character contents, credentials or full asset paths.
- **FR-011**: Automated acceptance/regression checks MUST use fake inference, synthetic configuration and temporary storage, without model downloads or private files.
- **FR-012**: A manual local-model check MUST verify one successful exchange, one stored event and successful history reload before M1 is called complete; record only non-sensitive environment/result evidence.

### Key Entities

- **Runtime settings**: model/character/history locations, local bind address/port and generation parameters; private paths are not shared fixtures.
- **Conversation state**: seven bounded gauges, current emotion and recent committed turns, owned once per app session.
- **Memory event**: one durable timestamped input/response pair, preserving the existing history shape.
- **Readiness/error state**: available, not configured, unavailable or busy; describes recovery without private details.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A fresh checkout with no private assets can open its interface and show a useful initial state; the automated fake-backed readiness journey completes within two seconds, excluding process startup.
- **SC-002**: Ten sequential successful synthetic exchanges add exactly ten events; rejected, busy and injected-failure requests add zero events.
- **SC-003**: Controlled examples reach at least three distinct non-neutral emotions; all resulting gauges stay within bounds.
- **SC-004**: Markup-shaped text remains literal; after every tested validation/network/server failure the owner can retry, and overlapping requests produce at most one committed turn.
- **SC-005**: The manual local-model exchange and restart checklist passes with one persisted event and no private/model assets added to Git.

## Assumptions

One local owner, one local process and one active conversation are in scope. Multi-user hosting, robust session isolation, persona prompt redesign, proactive triggers, model changes and image generation are deferred. Single-process coordination is sufficient for this milestone; multiple worker processes are unsupported. Existing memory fields are retained; historical duplication is not automatically repaired. Automated repository checks can run without installing the heavyweight app environment, while application tests will install an explicitly scoped lightweight test dependency set.
