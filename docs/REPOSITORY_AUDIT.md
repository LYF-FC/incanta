# Repository restart audit

**Date:** 2026-11-04. **Baseline:** source import `84ae8d5`, recovery audit `1b17a90`. Static review of all tracked application source, dependency snapshot and root guidance, plus GitHub repository state. No private data, model inference, dependency installation or performance/security certification was part of this application audit.

## GitHub and governance

The repository is private under LYF-FC and uses `main`. At the start of this pass it had no open issues/PRs or workflow runs. Existing recovery commits were preserved. This pass installs Spec Kit/Codex skills, a project constitution, documentation, feature artifacts, issue/PR templates and repository CI. GitHub returned HTTP 403 for both rulesets and branch protection, with an upgrade-to-Pro requirement for this private repository. Enforced branch protections are therefore unavailable under the current plan; keep the repository private and use PR/check discipline. No public release or Incanta redistribution license is created.

## Application findings

| ID | Evidence | Impact | Planned work |
| --- | --- | --- | --- |
| A01 | `frontend_app.py` imports chat, which imports a module-level `Llama` and private personality | Import/startup fails without assets; debug reloader can initialize inference twice | 001 / US1 |
| A02 | `/api/status` returns only `status`; `frontend/app.js` expects gauges/emotion | Initial dashboard receives undefined state | 001 / US1 |
| A03 | Chat handler assumes a mapping JSON body and string message, lacks bounded input | Malformed requests fail inconsistently; resource use is unbounded | 001 / US3 |
| A04 | `EMOTION_MAPPING` starts with unconditional Neutral | Other emotions never selected on active chat path | 001 / US2 |
| A05 | Chat invokes both `update_memories` and `store_event` | Each turn is appended twice | 001 / US2 |
| A06 | Chat is rendered with `innerHTML`; HTTP errors are not handled explicitly | User/model text can execute markup; failed responses corrupt UI state | 001 / US3 |
| A07 | Model and storage paths are relative/hard-coded; Flask debug is true | External assets and different launch locations are fragile | 001 / US1 |
| A08 | Memory rewrites the whole file without atomic replacement or corruption handling | Interrupted writes can destroy state or block further conversation | 001 / US2; fuller recovery/retention in M2 |
| A09 | Personality argument is unused by prompt construction; biography is hard-coded | Changing private character files does not change persona | M3 |
| A10 | Sibling milestone is inferred from generated response; retrieval ignores the query | Unsupported facts and irrelevant callbacks can become persistent | M2 |
| A11 | History/gauges are global; `core/state.py` duplicates state rules | No session isolation and divergent emotion behavior | One state owner in 001; isolation in M3 |
| A12 | `ImageGenerator` writes metadata only; not part of chat route | Earlier visual-generation claims are unimplemented | M4 |
| A13 | Historical requirements include heavyweight and unused packages | Setup cost/reproducibility/security review outstanding | M1 runtime/test split; M5 full dependency review |
| A14 | Frontend has no in-flight request lock; state updates are unsynchronized | Overlapping turns can race or lose memory updates | 001 / US2 and US3 |

## What this foundation verifies

Repository privacy guard regression tests, Python parsing, JavaScript/Bash syntax, first-party Markdown link targets, metadata/YAML parsing and installed feature prerequisite resolution. A passing workflow does not verify model availability, application correctness, offline inference, latency, dependency safety or a backup restore.

## Next action

Implement [001-reliable-local-chat](../specs/001-reliable-local-chat/spec.md) against its task list. Retain known limitations until tests and smoke-test evidence justify closing them. Re-run this audit when architecture or milestone scope changes; do not silently erase unresolved findings.

## Verification follow-up — 2026-11-17

The findings above describe the recovery baseline and are retained for provenance. Current working-tree M1 changes address A01–A08 and A14 mechanically, plus single-process state ownership from A11; 32 Python/six frontend tests and the synthetic browser journey pass. See [verification 001](../specs/001-reliable-local-chat/verification.md) for environment and evidence limits. An explicit owned-model exchange and separate-process history reload also passed after granting native-runtime access; the restricted attempt failed to create a Metal command queue. This does not mean changes are merged: the reviewed-delivery gate remains open.

A09 personality prompt integration, A10 factual-memory quality, A11 session isolation, A12 actual rendering and A13 full dependency review remain later MVP work. Durable timeline reload is verified synthetically; recent conversation state restoration is outside M1. The owner-approved MVP in [the roadmap](../ROADMAP.md#owner-defined-companion-mvp) adds these capabilities through separately planned increments; it does not retroactively expand 001.
