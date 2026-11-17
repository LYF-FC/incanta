# Incanta roadmap

Updated 2026-11-17. Priorities are ordered by dependency, not calendar promises. This roadmap covers Incanta as a local character/conversation project, with Butler remaining a separate production platform.

**Current focus:** complete owner dialogue acceptance (#9) after merged M1/002 PRs #7/#8; proceed through planned local visuals/proactive/release work. M0/CI do not make the app production-ready.

| Milestone | Status | Outcome | Exit gate |
| --- | --- | --- | --- |
| M0 — Development foundation | Complete | Recovered source, audit, Spec Kit, documentation, CI and contribution workflow | Repository checks pass and first implementation has a coherent specification/plan/task list |
| M1 — Reliable local chat | Complete; merged PR #7, issue #1 closed | Predictable startup, working status/chat UI, one memory event per successful turn, meaningful emotions | All [001 acceptance criteria](specs/001-reliable-local-chat/spec.md) pass with a fake inference adapter; one documented manual local-model smoke test passes |
| M2 — Memory and proactive dialogue | Memory controls implemented for review in 002; proactive work still planned | Relevant callbacks, natural follow-ups, explicit memory controls | Synthetic retrieval tests, callback provenance, no fabricated memories, inspect/delete/export and no background messages by default |
| M3 — Personality and session coherence | Mechanical scope delivered in PR #8; owner dialogue acceptance #9 pending | Validated character configuration and isolated sessions | Character values affect prompts; invalid configuration is handled; two test sessions cannot leak history or state |
| M4 — Optional visuals | Planned; depends on M1 and M3 | Optional local ComfyUI adapter and expression-aware display | Chat remains usable with visuals off/unavailable; private output stays local; adapter contract and fake integration tests pass |
| M5 — Reproducible local release | Planned; depends on selected M2–M4 scope | Documented, repeatable Mac setup and tested backup/restore | Fresh-machine setup, external-SSD model path, dependency review and restore rehearsal documented before tagging a release |

## Owner-defined companion MVP

The following product decisions were confirmed by the owner on 2026-11-17. They define the intended POC/MVP, not implemented behavior or amendments to feature 001. New behavior still needs the installed Spec Kit specification, clarification, plan, tasks and verification workflow. Resume 001 in its existing directory and branch; do not recreate it to cover this broader scope.

| Area | Agreed scope |
| --- | --- |
| Audience and execution | One private owner; chat and image inference entirely on the owner's Mac. No cloud inference or automatic cloud fallback. |
| POC platform | MacBook Pro M2 with 16 GB RAM, English only. Phone access has not been requested; use the existing local browser interface for the POC. |
| Character | Celeste, with personality and relationship/content boundaries configured through a short setup form for each chat. Actual private definitions stay outside Git. |
| Conversation boundaries | Separate conversations; explicitly share selected facts only. Corrections and deletions apply wherever a fact is shared. Sharing must not implicitly expose another chat's transcript, personality or relationship state. |
| Persistent memory | Remember across app restarts; inspect, correct and delete memories in the MVP. Export remains a roadmap capability; its inclusion in the MVP is not yet confirmed. |
| Visual experience | A consistent photorealistic portrait plus new scenes during conversations; the face must closely match owner-provided references. Several minutes per scene are acceptable; no measured latency promise exists yet. |
| Image triggers | Manual requests and automatic scene changes. The owner accepted a per-chat automatic-generation toggle, configurable cooldown and manual-request priority. Numeric cooldown and queue/cancellation behavior belong in the visual feature spec. |
| Initiative | Celeste can initiate follow-ups and contact the owner through Mac notifications while Incanta runs; missed follow-ups appear on return. Local generation requires the Mac to be awake and Incanta running. Rate limits, quiet hours, notification permission handling and sleep/restart catch-up behavior must be defined in the proactive-dialogue feature spec. |
| Existing visual assets | Reference images and an existing character LoRA are available, but not inspected in this scope review. ComfyUI setup is unverified after a long period without review. LoRA retraining is expected after the POC unless measured visual results make it necessary earlier. |
| Later deployment | A Mac mini and Nomad machine associated with Butler are intended after the POC. Their specifications, availability and deployment boundary remain unconfirmed; Incanta stays separate from Butler production services. |
| Timing | No target date. Sequence work by dependencies and measured results. |

### MVP acceptance journey

The owner selected these release criteria:

1. Hold a 30-minute conversation with Celeste.
2. Restart Incanta and retain conversation continuity and saved memories.
3. Produce three consistent photorealistic scenes with a face closely matching the reference images, reviewed by the owner.

Feature acceptance must additionally cover per-chat setup and isolation, explicit memory sharing, inspect/correct/delete controls, both image triggers and proactive follow-ups. A timed session alone does not establish dialogue quality; the detailed feature specs must define the synthetic evaluation scenario, owner review criteria and measured response times. Visual reference review remains local and is not attached to shared verification records.

### Delivery order and remaining decisions

1. Deliver the verified M1 changes through reviewed PR/merge; automated, synthetic-browser and explicit native-model/separate-process checks passed on 2026-11-17. See [verification 001](specs/001-reliable-local-chat/verification.md).
2. Specify conversation/personality boundaries and persistence before cross-chat memory sharing; develop the M2 memory controls against those boundaries.
3. Specify and evaluate a local ComfyUI-Photoshoot integration: check the existing installation, choose a compatible workflow/model explicitly, establish reference-face acceptance, and measure resource use on the M2/16 GB target. Prompt controls alone do not prove render quality or identity consistency. Chat must remain recoverable when rendering fails or is unavailable. Whether models can stay loaded together must be measured.
4. Add manual and automatic scene requests, then opt-in proactive follow-ups with explicitly defined delivery and scheduling behavior.
5. Run the complete owner acceptance journey and M5 setup/backup/restore gates before calling the MVP released.

Product scope is sufficiently defined to author the subsequent feature specifications. The owner confirmed Mac notifications while Incanta runs, missed follow-ups on return, selected-fact sharing only, and correction/deletion propagation wherever a fact is shared. Detailed scheduling, notification limits, image queue behavior, dialogue-quality review and visual evaluation criteria must be resolved in those specifications before implementing the affected behavior. No model downloads, inference runs, private-asset inspection or external message delivery are authorized as a side effect of these planning checks.

### Spec Kit MVP implementation backlog

Created on 2026-11-17 through the installed individual specification/planning/task workflows, using resolved upstream templates and explicit feature directories. Feature 002 has 25 completed implementation/review/delivery tasks and one open owner-acceptance task; the 60 tasks in 003–005 remain unchecked. Planning is complete. Feature 002 is delivered with owner acceptance pending; 003–005 remain planned. Native M1 verification was explicitly requested separately and used the owner-supplied existing model with synthetic temporary data.

| Order | Feature | Deliverable | Tasks | Dependency |
| --- | --- | --- | --- | --- |
| 1 | [002 — Conversations and memory](specs/002-companion-conversations/spec.md) | [Plan](specs/002-companion-conversations/plan.md), isolated setup/state, canonical shared facts and memory controls | [26 tasks](specs/002-companion-conversations/tasks.md) | Verified/reviewed 001 |
| 2 | [003 — Local character visuals](specs/003-local-character-visuals/spec.md) | [Plan](specs/003-local-character-visuals/plan.md), Photoshoot workflow/API integration, portrait approval, manual/automatic jobs, resource coordination | [22 tasks](specs/003-local-character-visuals/tasks.md) | 002 contracts/store |
| 3 | [004 — Proactive follow-ups](specs/004-proactive-followups/spec.md) | [Plan](specs/004-proactive-followups/plan.md), opt-in scheduler, inbox and native Mac notifications | [21 tasks](specs/004-proactive-followups/tasks.md) | 002 context/store and 003 resource lease |
| 4 | [005 — Local MVP release](specs/005-local-mvp-release/spec.md) | [Plan](specs/005-local-mvp-release/plan.md), clean setup, backup/restore and combined owner acceptance | [17 tasks](specs/005-local-mvp-release/tasks.md) | Accepted 001–004 |

The 86 tasks (including three review corrections in 002) cover 39 functional requirements and 19 success criteria. Each feature includes research decisions/sources, data model, interface contracts, validation quickstart and a requirements-quality checklist. Those checklists assess authoring quality, not implementation. Cooldown/rate limits, fact-deletion semantics and queue behavior now have explicit planned defaults/contracts. M2/M3 roadmap work is combined in 002 because persistent conversation boundaries are prerequisites for correct shared-memory behavior; feature numbers are not milestone numbers.

## GitHub tracking

| Milestone | Tracking issue | Milestone board |
| --- | --- | --- |
| M1 | [Reliable local chat #1](https://github.com/LYF-FC/incanta/issues/1) | [M1](https://github.com/LYF-FC/incanta/milestone/1) |
| M2 | [Memory and proactive dialogue #2](https://github.com/LYF-FC/incanta/issues/2) | [M2](https://github.com/LYF-FC/incanta/milestone/2) |
| M3 | [Personality and sessions #3](https://github.com/LYF-FC/incanta/issues/3) | [M3](https://github.com/LYF-FC/incanta/milestone/3) |
| M4 | [Optional visuals #4](https://github.com/LYF-FC/incanta/issues/4) | [M4](https://github.com/LYF-FC/incanta/milestone/4) |
| M5 | [Reproducible local release #5](https://github.com/LYF-FC/incanta/issues/5) | [M5](https://github.com/LYF-FC/incanta/milestone/5) |

Issues coordinate work; feature artifacts own detailed requirements and task status. M1 is delivered and issue #1 is closed; the other milestones retain their recorded implementation/acceptance gates.

## M1 baseline (delivered in PR #7)

The detailed work is in [specification 001](specs/001-reliable-local-chat/spec.md), [implementation plan](specs/001-reliable-local-chat/plan.md), and [tasks](specs/001-reliable-local-chat/tasks.md). The scope is deliberately one baseline repair:

- Explicit configuration and local asset paths; no model loading when importing the web app.
- Status and chat contracts shared by the UI and server; safe rendering and recoverable errors.
- Correct emotion precedence and exactly one durable event per successful turn.
- Temporary synthetic data and fake inference for automated tests; a separate real-model smoke test.

## Later work

M2 should replace the hard-coded sibling milestone heuristic, define retention and recovery rules, and make proactive callbacks opt-in, grounded in retrieved events and rate-limited. The owner has requested away follow-ups for the MVP; their delivery and scheduling contract must be specified before implementing background contact. Existing M1 work does not include it.

M3 should introduce a documented character schema, prompt integration, session boundaries and a migration strategy for existing private local definitions. Do not commit those definitions as fixtures.

M4 starts by deciding which legacy expression-selection behavior to recover and specifying the requested ComfyUI-Photoshoot integration. Visuals are required for MVP acceptance, while the runtime must handle ComfyUI being off or unavailable without losing chat state. Do not revive a full older app wholesale.

M5 should replace the historical dependency freeze with reviewed direct/runtime and optional dependencies while retaining the recovery snapshot. Model choice, performance targets and distribution scope require measured hardware evidence.

## Working rules

Each feature gets a numbered directory in `specs/`, acceptance criteria, a plan, tasks and a pull request. The feature directory owns detailed requirements; this roadmap owns sequencing. GitHub issues may reference those files rather than duplicate every task. No completion checkbox is evidence of an application test unless its result is recorded.

Cloud inference, public hosting, household production integration, multi-user access and framework rewrites require separate specifications; they are outside this restart. Estimates and dates are added only when implementation evidence supports them.

## Implementation follow-up — 002

The owner requested committing M1/plans and opening a PR before starting 002. Commit `d895585` is in [PR #7](https://github.com/LYF-FC/incanta/pull/7); no merge is implied. The existing 002 branch is stacked on that baseline. [002 verification](specs/002-companion-conversations/verification.md) records implemented per-chat setup/restoration, canonical shared facts, memory controls and explicit non-destructive import, with 47 passing Python tests, 11 frontend tests, synthetic browser checks and a short native structured-message/process-reload smoke. T022 owner-reviewed 30-minute dialogue and T023 reviewed delivery remain open. No ComfyUI/notifications/release backup tooling is implemented.

GitHub-hosted jobs for PR #7 could not start due to an account billing/spending-limit issue. This is distinct from local test results and is not reported as hosted CI success. No billing/payment setting was changed.

## PR/CI review follow-up — 2026-11-17

The owner changed the GitHub repository to public. The original billing-blocked PR #7/#8 runs both passed on rerun attempt 2. New commits still require their own checks. Review of 002 added three corrected regressions: pending/failed chat selection cannot redirect a send, failed first database initialization remains retryable without resetting existing data, and malformed stored state returns an unreadable-history error before inference. Local totals are 49 Python tests (3.11/3.13) and 12 frontend tests. No native model was used for this review. M1 is ready for review/merge and issue #1 closure on merge; the other milestone issues retain their actual remaining gates.

## Final review outcome — 2026-11-17

PR #7 and corrected PR #8 were reviewed and merged after their required hosted checks passed. M1 issue #1 and the original M3 mechanical-scope issue #3 are closed; M1's milestone is closed. The separate owner-reviewed 30-minute conversation/restart assessment remains issue #9 and feature 002 T022, keeping the M3 acceptance milestone open. Feature 002 T023 (reviewed delivery) is complete. Issues #2/#4/#5 remain open for their unbuilt scope. Final regression totals are 49 Python tests and 12 frontend tests; no native inference was invoked during issue/CI review.
