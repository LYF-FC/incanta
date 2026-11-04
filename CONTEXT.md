# Incanta - Canonical Project Context

## Purpose

Incanta is an earlier private/local AI assistant prototype in the family project portfolio. It predates the Butler architecture and is now primarily useful as a technical reference, experimentation environment and source of reusable components.

Incanta should not silently evolve into a second production Butler. Butler is the strategic family-assistant platform.

## Known architecture direction

Previous/known Incanta work used or explored:
- local model inference
- FastAPI backend
- React frontend
- llama.cpp/local inference
- ComfyUI integration/experiments
- Apple Silicon/local workstation execution

The recovered source currently uses Flask and plain JavaScript. FastAPI, React and live ComfyUI integration remain earlier directions rather than implemented features in this snapshot.

## Strategic role now

Incanta should be treated as:
- prototype/reference project
- sandbox for local-AI experiments
- source of reusable components/patterns
- possible archive once useful parts are extracted

Potentially reusable:
- FastAPI service patterns
- React components
- inference wrappers
- prompt/agent experiments
- ComfyUI orchestration
- Apple Silicon deployment lessons

## Privacy

Original intent was private/local AI processing.

Continue to avoid:
- sending private family context to external model services by default
- storing production Butler data in ad-hoc Incanta stores
- treating prototype security as production-ready

## Relationship to Butler

Butler supersedes Incanta as the production family AI platform.

Any reuse should:
- inspect actual current code
- identify dependencies
- remove stale assumptions
- align with Butler auth/audit/permissions
- avoid copying persistence designs blindly

## Hardware context

Relevant systems:
- MacBook Pro M2, 16 GB
- Mac Pro 2013, 64 GB
- future dedicated Butler host in Nice

Incanta was oriented toward workstation/local execution rather than Synology-hosted inference.

## Current status

- older prototype
- not chosen as production architecture
- repo exists to preserve/review useful work
- should be audited before new development
