# Feature 002 verification

**Date:** 2026-11-17. **Status:** implementation and automated/browser/short-native checks passed; owner-reviewed 30-minute acceptance and reviewed delivery remain pending.

## Delivery and workflow

The owner explicitly requested committing M1/plans, opening a review PR, then implementing 002. Baseline commit `d895585` is in [M1 and plans PR #7](https://github.com/LYF-FC/incanta/pull/7). The existing `codex/002-companion-conversations` branch was fast-forwarded to that baseline; no duplicate feature/branch was created, no force-push/merge performed. The owner authorized stacked development while M1 review remains open.

The installed implementation workflow resolved the explicit feature directory, loaded spec/plan/tasks/design/contracts, and passed all 16 requirements-quality checklist items without changing their markers. Optional auto-commit hooks remained disabled; commits/staging were explicit. HTTP registration and browser transport helpers are split into small additional modules as recorded in ADR-009. No new framework or native inference dependency was installed.

## Automated evidence

Local Python 3.13.5 in the existing environment and Python 3.11.14 in a separate lightweight temporary environment; Node 22.22.2. All tests use fake inference, synthetic setup/history and temporary storage.

| Check | Result |
| --- | --- |
| Python unittest discovery | PASS, 47 tests on both Python 3.11.14 and 3.13.5, including 15 new companion tests |
| Node `tests/*.test.js` | PASS, 11 tests including five new companion transport/rendering tests |
| Modified JavaScript syntax | PASS |
| Repository checker and staged whitespace | PASS; 174 staged files checked, exact JSON privacy allowlist unchanged |
| Private original source/model/personality/history migration | Not performed; synthetic import tests only |

Regression evidence: the new conversation/fact/import suites and frontend suite fail against committed pre-002 baseline `d895585` in an isolated temporary source extraction. They pass with 002. Initial development also observed the missing settings/schema and transport-helper failures before implementation.

Automated checks prove two-chat prompt/settings/transcript/state isolation, two separate-process restarts, ten successful turns/ten records, idempotent request replay, validation and failed-write rollback, global overlap rejection, settings/fact edit during inference, bounded context/old-turn trimming, explicit canonical sharing/correction/revocation/deletion, content-free fact tombstones, provenance/source scope, literal text, CSRF/origin guards, corruption/read-only/disconnected storage, pagination, and preview/backup/import failure/repeat/source-change preservation. Unknown legacy fields and duplicate events remain byte-identical in the preserved original copy.

## Synthetic browser journey

Used the real default Flask factory/frontend on a temporary loopback server with fake inference and disposable SQLite/legacy files. No private files were opened.

1. Readiness and initial short setup appeared without model loading or database creation.
2. Created astronomy and gardening conversations with different settings. Switching restored independent setup/state; the second chat did not show the first transcript.
3. Sent markup-shaped input; input and fake reply tags appeared literally. DOM inspection found zero image and bold elements in the transcript.
4. Saved one owner-selected fact in the first chat, explicitly shared it with the second, and observed sharing provenance without transcript transfer.
5. Corrected the fact from the recipient and observed the corrected content in the source chat.
6. Deleted the canonical fact and observed no saved facts in the recipient. The interface explained that transcript/backups are not erased.
7. Reloaded the browser and observed restored selected chat, settings, transcript and emotional state. Process-level restoration is separately covered by automated subprocess checks.

The browser's generated label on one dynamic sharing select required a more precise locator; the control now has an explicit accessible label. No private screenshots/transcript contents are committed. The temporary verification server was stopped after checks.

## Explicit short native smoke

**PASS:** `scripts/verify_companion_model.py` ran against the already-owned model authorized earlier by the owner, using a temporary synthetic conversation/database. It passed structured system/user generation, exactly one SQLite turn, and a separate process reloading the saved conversation without model initialization. It read no private personality or chat history, modified no model/source file and downloaded nothing.

Same environment/model as [M1 native evidence](../001-reliable-local-chat/verification.md): existing llama-cpp-python 0.3.36, Python 3.13.5, macOS arm64, context 4096, eight threads, zero GPU layers; native runtime access required. The GGUF SHA-256 recorded there is `5cf3653525ff921fb690ff96e0d5af186aaf05e8d544e76927a694b574236ec0`. Native diagnostics and all prompts/responses remain private and are suppressed by the runner.

This short check is not an owner verdict on personality/boundary adherence or 30-minute continuity quality.

## Pending acceptance and hosted checks

- **T022 / SC-005:** synthetic browser and short native checks pass, but the owner must review a 30-minute English conversation, restart continuity, configured personality/boundaries and remembered-fact quality. No owner approval or full native-dialogue acceptance is claimed.
- **T023:** documentation/checks and separate feature PR are prepared; reviewer decisions/merge remain separate. Neither M1 nor 002 is automatically merged or tagged.
- GitHub Actions for PR #7 could not start any test steps or allocate a runner. Its check annotation reports an account billing/spending-limit blocker. This is a hosted-execution blocker, not a passing remote check or evidence that tests failed. Only the owner can resolve account billing settings; no account/payment setting was changed.
- ComfyUI/rendering, proactive follow-ups/notifications and full consistent app backup/restore are still planned features 003–005.
