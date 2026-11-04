# Incanta roadmap

Updated 2026-11-04. Priorities are ordered by dependency, not calendar promises. This roadmap covers Incanta as a local character/conversation project, with Butler remaining a separate production platform.

**Current focus:** M1, reliable local chat. M0 provides the repository workflow; it does not make the recovered application production-ready.

| Milestone | Status | Outcome | Exit gate |
| --- | --- | --- | --- |
| M0 — Development foundation | Complete | Recovered source, audit, Spec Kit, documentation, CI and contribution workflow | Repository checks pass and first implementation has a coherent specification/plan/task list |
| M1 — Reliable local chat | Ready for implementation | Predictable startup, working status/chat UI, one memory event per successful turn, meaningful emotions | All [001 acceptance criteria](specs/001-reliable-local-chat/spec.md) pass with a fake inference adapter; one documented manual local-model smoke test passes |
| M2 — Memory and proactive dialogue | Planned; depends on M1 | Relevant callbacks, natural follow-ups, explicit memory controls | Synthetic retrieval tests, callback provenance, no fabricated memories, inspect/delete/export and no background messages by default |
| M3 — Personality and session coherence | Planned; depends on M1, memory work aligns with M2 | Validated character configuration and isolated sessions | Character values affect prompts; invalid configuration is handled; two test sessions cannot leak history or state |
| M4 — Optional visuals | Planned; depends on M1 and M3 | Optional local ComfyUI adapter and expression-aware display | Chat remains usable with visuals off/unavailable; private output stays local; adapter contract and fake integration tests pass |
| M5 — Reproducible local release | Planned; depends on selected M2–M4 scope | Documented, repeatable Mac setup and tested backup/restore | Fresh-machine setup, external-SSD model path, dependency review and restore rehearsal documented before tagging a release |

## GitHub tracking

| Milestone | Tracking issue | Milestone board |
| --- | --- | --- |
| M1 | [Reliable local chat #1](https://github.com/LYF-FC/incanta/issues/1) | [M1](https://github.com/LYF-FC/incanta/milestone/1) |
| M2 | [Memory and proactive dialogue #2](https://github.com/LYF-FC/incanta/issues/2) | [M2](https://github.com/LYF-FC/incanta/milestone/2) |
| M3 | [Personality and sessions #3](https://github.com/LYF-FC/incanta/issues/3) | [M3](https://github.com/LYF-FC/incanta/milestone/3) |
| M4 | [Optional visuals #4](https://github.com/LYF-FC/incanta/issues/4) | [M4](https://github.com/LYF-FC/incanta/milestone/4) |
| M5 | [Reproducible local release #5](https://github.com/LYF-FC/incanta/issues/5) | [M5](https://github.com/LYF-FC/incanta/milestone/5) |

Issues coordinate work; feature artifacts own detailed requirements and task status. All five application milestones remain open.

## M1: the next implementation

The detailed work is in [specification 001](specs/001-reliable-local-chat/spec.md), [implementation plan](specs/001-reliable-local-chat/plan.md), and [tasks](specs/001-reliable-local-chat/tasks.md). The scope is deliberately one baseline repair:

- Explicit configuration and local asset paths; no model loading when importing the web app.
- Status and chat contracts shared by the UI and server; safe rendering and recoverable errors.
- Correct emotion precedence and exactly one durable event per successful turn.
- Temporary synthetic data and fake inference for automated tests; a separate real-model smoke test.

## Later work

M2 should replace the hard-coded sibling milestone heuristic, define retention and recovery rules, and make proactive callbacks opt-in, grounded in retrieved events and rate-limited. It does not authorize unsolicited background messages.

M3 should introduce a documented character schema, prompt integration, session boundaries and a migration strategy for existing private local definitions. Do not commit those definitions as fixtures.

M4 starts by deciding which legacy expression-selection behavior to recover. ComfyUI stays an optional local dependency. Do not revive a full older app wholesale.

M5 should replace the historical dependency freeze with reviewed direct/runtime and optional dependencies while retaining the recovery snapshot. Model choice, performance targets and distribution scope require measured hardware evidence.

## Working rules

Each feature gets a numbered directory in `specs/`, acceptance criteria, a plan, tasks and a pull request. The feature directory owns detailed requirements; this roadmap owns sequencing. GitHub issues may reference those files rather than duplicate every task. No completion checkbox is evidence of an application test unless its result is recorded.

Cloud inference, public hosting, household production integration, multi-user access and framework rewrites require separate specifications; they are outside this restart. Estimates and dates are added only when implementation evidence supports them.
