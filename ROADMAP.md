# Incanta Roadmap

## Objective

Turn Incanta into a documented reference/sandbox rather than a competing production platform.

## Phase 1 - Source recovery

- import all existing local source
- document current dependency versions
- document how to run it
- identify data/config files
- add basic tests where practical

## Phase 2 - Architecture audit

Classify each component:
- reusable in Butler
- useful experiment only
- obsolete
- security risk
- archive candidate

Review:
- backend
- frontend
- inference wrappers
- ComfyUI integration
- persistence
- secrets/config
- deployment

## Phase 3 - Selective migration

For worthwhile components:
- refactor
- add tests
- align with Butler auth/audit/permissions
- migrate into Butler or dedicated supporting repo

## Phase 4 - Archive or retain as sandbox

- archive redundant code
- keep experimentation branch only if it still provides unique value

## Rule

No production family data should depend on Incanta.
