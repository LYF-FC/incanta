# Incanta project context

## Purpose and current direction

Incanta is a private, local AI character/conversation prototype. On 2026-11-04, the owner requested structured active development after source recovery. The repository now supports that restart through Spec Kit, documented priorities and reviewable changes.

The latest recovered source came from `Documents/Projects/Incanta`. Older variants and ZIPs remain unchanged; see [source recovery](docs/SOURCE_RECOVERY.md). They are references, not interchangeable releases.

## Product boundary

Incanta develops character interaction, emotional state, memory and optional visuals. Butler remains the separate strategic production family-assistant platform. No production household data or service should depend on this experimental app. Components may be reused only after their own security, dependency and persistence review.

## Evidence over old plans

The current implementation is Flask plus plain JavaScript and `llama-cpp-python`. It is not React/FastAPI, and image metadata is not a working ComfyUI adapter. Python 3.13.5 was recorded by the recovered environment; no tested runtime support range has yet been established for the app. Repository tooling targets Python 3.11 and 3.13.

## Source of truth

- [Constitution](.specify/memory/constitution.md): project principles.
- [Roadmap](ROADMAP.md): sequence and milestone gates.
- `specs/<number>-<feature>/`: feature requirements, decisions, tasks and verification.
- [Audit](docs/REPOSITORY_AUDIT.md): current limitations and evidence.
- [Decisions](DECISIONS.md): durable architectural/governance choices.

Private character definitions, conversation history, models and generated assets remain local. Public or private repository status does not change that rule.
