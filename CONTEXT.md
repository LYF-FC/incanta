# Incanta project context

## Purpose and current direction

Incanta is a private, local AI character/conversation prototype. On 2026-11-04, the owner requested structured active development after source recovery. The repository now supports that restart through Spec Kit, documented priorities and reviewable changes.

The latest recovered source came from `Documents/Projects/Incanta`. Older variants and ZIPs remain unchanged; see [source recovery](docs/SOURCE_RECOVERY.md). They are references, not interchangeable releases.

## Product boundary

Incanta develops character interaction, emotional state, memory and optional visuals. Butler remains the separate strategic production family-assistant platform. No production household data or service should depend on this experimental app. Components may be reused only after their own security, dependency and persistence review.

On 2026-11-17 the owner defined a private, English-only Celeste companion POC on a MacBook Pro M2 with 16 GB RAM, with entirely local chat/image inference. The MVP includes per-chat personality and relationship/content setup, separate conversations with explicitly shared selected facts, persistent memories with inspect/correct/delete controls, a reference-matching photorealistic portrait and scenes, manual/automatic image requests, and proactive follow-ups. Corrections/deletions apply wherever a fact is shared. Away contact uses Mac notifications while Incanta runs, with missed follow-ups shown on return. These are product requirements, not implemented capabilities. The [roadmap](ROADMAP.md#owner-defined-companion-mvp) records scope, acceptance and delivery order; feature 001 remains the narrower reliability baseline.

## Evidence over old plans

The current implementation is Flask plus plain JavaScript and `llama-cpp-python`. It is not React/FastAPI, and image metadata is not a working ComfyUI adapter. Python 3.13.5 was recorded by the recovered environment; lightweight fake-backed application checks target Python 3.11 and 3.13. Real local inference needs separate native-runtime verification.

On 2026-11-17, M1's 32 Python tests, six frontend tests, synthetic browser journey and explicit owned-model/separate-process history reload passed; reviewed delivery remains pending. See [verification 001](specs/001-reliable-local-chat/verification.md) for the exact environment and native-runtime access caveat. Features 002–005 now have specifications, plans, contracts and an initial 83-task implementation backlog linked from the roadmap; later implementation/review progress is recorded there. No MVP memory/session/render/notification capability is implied by those planning artifacts.

## Source of truth

- [Constitution](.specify/memory/constitution.md): project principles.
- [Roadmap](ROADMAP.md): sequence and milestone gates.
- `specs/<number>-<feature>/`: feature requirements, decisions, tasks and verification.
- [Audit](docs/REPOSITORY_AUDIT.md): current limitations and evidence.
- [Decisions](DECISIONS.md): durable architectural/governance choices.

Private character definitions, conversation history, models and generated assets remain local. Public or private repository status does not change that rule.

## Companion implementation follow-up

M1 and the agreed MVP plans are committed as `d895585` in review PR #7. At the owner's explicit request, 002 is implemented on its existing branch without waiting for or performing a merge. The active app now uses per-conversation setup, durable SQLite transcript/state, explicitly shared canonical facts and inspect/correct/delete controls. A configured legacy source can be previewed/confirmed with exact-byte preservation and idempotent import; no private source was imported during development. Automated/browser/short-native checks pass; owner-reviewed 30-minute acceptance and reviewed delivery remain pending. The earlier planning descriptions are historical decisions, not claims that 003–005 are implemented.

## PR/CI review follow-up

The owner made the repository public on 2026-11-17; runtime/private data rules are unchanged. GitHub rerun attempt 2 passed for both existing PR heads after the original billing-blocked attempts. The 002 review added three regression fixes under existing scope and now passes 49 Python/12 frontend tests locally; new pushes must be verified separately. No milestone is closed solely on a planning checklist, and 002 owner-reviewed 30-minute acceptance remains outstanding.

The owner subsequently authorized review/comment/merge when all current checks are green. PR #7 passed rerun CI and merged as a52cf54a50837898b3606c8e059732163b10d9db; issue #1 is closed. PR #8 corrections are reviewed and require their own green CI before merge. The owner's separate 30-minute dialogue assessment remains open as issue #9 and is not implied by a code merge.

Final outcome: required CI passed for PR #8 correction head 6f955c2, and the owner-authorized review/merge delivered PRs #7/#8. Issues #1/#3 are closed for completed mechanical scope, while owner dialogue acceptance is explicitly retained in issue #9 / 002 T022. PR delivery T023 is complete; rendering, proactive follow-ups and release/backup-restore work remain planned. Runtime-data privacy rules remain unchanged after the owner's public-repository decision.
