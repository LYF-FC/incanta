# M1 verification record

**Date:** 2026-11-17. **Overall:** automated, synthetic-browser and explicit native-model/separate-process checks passed. Reviewed delivery remains pending; M1 is not yet merged/complete.

## Environment and automated results

macOS 27.0.1, arm64; repository `.venv` Python 3.13.5; Node 22.22.2. The local environment reports `llama-cpp-python` 0.3.36 installed. Native inference was run only after the owner supplied an accessible already-owned model. The repository's CI matrix is distinct from this local run; no remote CI result is asserted here.

| Check | Result | Evidence boundary |
| --- | --- | --- |
| `.venv/bin/python -m unittest discover -s tests -v` | PASS, 32 tests | Fake inference, temporary synthetic character/history; includes 10 turns/10 events, rollback, overlap, malformed input/storage and three non-neutral emotions |
| `node --test tests/frontend.test.js` | PASS, 6 tests | Literal rendering, failures/retry, request locking and empty input |
| `node --check frontend/app.js` and `frontend/chat_helpers.js` | PASS | Syntax only |
| `bash -n run.sh` and `scripts/specify.sh` | PASS | Syntax only |
| `python3 scripts/check_repository.py` | PASS | Final temporary index included 159 files from 82 explicitly reviewed paths plus unchanged index contents; original user staging area unchanged |
| `git diff --check` / `git diff --cached --check` | PASS | Worktree and index whitespace checks |
| Feature prerequisite resolution | PASS | Existing feature directory explicitly selected; all 10 requirements-quality checklist items checked |

## Synthetic browser journey (T018)

Used the actual Flask app factory and current frontend in the in-app browser, on a temporary loopback server with injected fake inference and synthetic files outside the repository. No private character/history/model was opened. The temporary harness is not a production endpoint or installed service.

1. Initial page displayed ready, Neutral emotion and seven zero gauges without generating or creating history.
2. Submitted markup-shaped synthetic text. Both user markup and the fake response's HTML tags appeared literally; no executable image/HTML was inserted.
3. Verified exactly one durable event after the successful turn.
4. Injected generation failure. The interface displayed a controlled error, retained retry input, restored Send, and left gauges/event count unchanged at one.
5. Retried with delayed successful fake inference. Input and Send were visibly disabled while processing; completion restored controls, cleared the error/input and added exactly one event (total two).
6. Hid gauges and observed the corresponding Show Gauges control.
7. Detached the synthetic character file and refreshed readiness. The interface displayed an actionable character-configuration message without exposing its path.

Network-failure/invalid-response behavior and true threaded overlap were verified by the automated suites, not by intercepting browser network requests. No screenshot/conversation content is committed; this record contains outcomes only.

## Native-model/restart gate (T020)

**PASS:** explicit native exchange, exactly one saved timeline event, same-process new-app reload, and a separate Python process reloading the same synthetic history with model still unloaded on status. The separate process exits successfully without further inference. The owner supplied the already-owned model location; no private character/history was accessed and nothing was downloaded.

- Model identity: Nous-Hermes-2-Mistral-7B-DPO, Q4_K_S, GGUF; 4,140,385,280 bytes.
- SHA-256: `5cf3653525ff921fb690ff96e0d5af186aaf05e8d544e76927a694b574236ec0`.
- Runtime: existing llama-cpp-python 0.3.36; Python 3.13.5, macOS 27.0.1 arm64; owner-reported M2/16 GB. Context 4096, eight threads, zero GPU layers, mmap on, mlock off, ChatML; other settings are the current LocalInference defaults. Native compilation flags were not reconstructed/certified.
- Initial restricted attempts failed at context creation (`model_unavailable`); a focused synthetic diagnostic identified Metal command-queue allocation failure. Reducing context to 2048 did not resolve it. The original 4096 context passed with access to the Mac native runtime; no application runtime setting/dependency was changed to obtain the pass.
- Repeated explicit run with the final [smoke runner](../../scripts/verify_local_model.py) passed including separate-process reload. Each run used its own disposable synthetic character/history; contents/native diagnostics were suppressed. No raw diagnostic, prompt, reply, private path or weight is committed.

This gate proves the tested model/runtime exchange and durable history reload, not 30-minute dialogue quality, restored in-memory gauges, model performance, face rendering or other models/builds. Those belong to later acceptance.

## Delivery gate (T021)

**PENDING REVIEW:** the verified implementation and MVP plans are now committed as `d895585` in [PR #7](https://github.com/LYF-FC/incanta/pull/7), following the owner's request. A temporary staging snapshot passed repository safeguards and staged whitespace checks, including M1 and new MVP planning files; the original user staging area was preserved. PR #7 is open; reviewer decision/merge is still required. Do not mark M1 delivered/merged, infer remote CI success, or conflate planning artifacts for later MVP features with implementation.

## Scope limits

M1 preserves a readable durable timeline; it does not restore recent in-memory dialogue, gauges or relationship state after process restart. Full per-conversation continuity belongs to the next MVP feature. Factual-memory quality, personality prompt integration, session isolation, live rendering and notifications remain unimplemented.

**Hosted check follow-up:** PR #7 jobs were rejected before any runner/test steps because GitHub reported an account billing/spending-limit issue. Local pass results above remain distinct; no hosted CI success is claimed and no billing setting was changed.
