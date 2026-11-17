# Decisions

## ADR-001 — Incanta and Butler remain separate

**Status:** retained, clarified 2026-11-04.

Incanta is an experimental local character engine. Butler is the production family-assistant direction. Restarting Incanta does not authorize production household integration. Extracted components require their own audit.

## ADR-002 — Restart through specifications

**Status:** accepted 2026-11-04, following the owner's request for structured development.

Use GitHub Spec Kit v1.3.0 with Codex skills and its Git extension. Track shared templates, scripts, constitution and non-sensitive tool manifests. Keep current-feature pointers, per-machine overrides and agent authentication/session state out of Git. CLI source is pinned; upgrades get a dedicated review.

## ADR-003 — Stabilize the existing stack first

**Status:** accepted for M1, 2026-11-04.

Retain Flask and plain JavaScript. Repair startup, contracts, persistence, emotion selection and rendering before expanding functionality. Framework migration needs a separate specification and measurable benefit.

## ADR-004 — Local data and explicit asset paths

**Status:** policy accepted; runtime configuration implemented in specification 001.

Models, private personalities, memories and outputs stay outside repository history. Support external storage through explicit configuration. A disconnected SSD must produce a useful readiness/error state; no automatic cloud fallback or model download.

## ADR-005 — Test without real models by default

**Status:** tooling active; application adapter and fake-backed tests implemented in specification 001.

Repository CI uses synthetic data and no model downloads. Future application tests inject fake inference and temporary storage. Real inference remains an explicit manual check with hardware/model identity and result, excluding prompts and responses from shared logs.

## ADR-006 — Small reviewed Git changes

**Status:** active convention, 2026-11-04.

Use branches and pull requests with passing checks. CODEOWNERS assigns the owner; required reviews and branch protection are not assumed or claimed. Spec Kit automatic commits are disabled so staged content is reviewed explicitly. Archive legacy work only after checking unique source/private assets; this setup authorizes no deletion.

## ADR-007 — Preserve dependency and license provenance

**Status:** active, 2026-11-04.

Keep the recovered `requirements.txt` unchanged until a dedicated dependency review. It is not a minimal or security-certified environment. Incanta has no redistribution license selected. Bundled Spec Kit retains upstream MIT terms; this does not license the rest of the project or downloaded models.

## ADR-008 — Separate lightweight and native runtime dependencies

**Status:** accepted in M1, 2026-11-04.

Keep `requirements.txt` as the untouched recovery snapshot. `requirements-test.txt` pins the lightweight Flask web/test runtime. `requirements-inference.txt` pins optional local inference separately; CI does not install it. Default GPU offload is zero for a conservative baseline. Record native build options and smoke results rather than assuming old binaries work on the current OS. No original environment or model is modified.

## ADR-009 — Isolated conversations and canonical shared facts

**Status:** implemented for review in 002, 2026-11-17; owner acceptance remains pending.

Use standard-library SQLite with one connection per operation and short transactions for per-chat setup, turns/state, fact grants and revisions. No write transaction spans inference. Recheck settings/context revisions before atomically committing a turn; preserve request UUID idempotency. Canonical facts propagate correction/deletion without copying other transcripts. Deletion removes active fact content/grants, not historical transcript text or existing backups.

Legacy JSON import is explicit, source-checksummed and transactional after preserving exact original bytes. Keep M1's engine only as an explicit compatibility harness, not the default chat API. The owner authorized stacked implementation of 002 while M1 PR #7 remains under review; neither branch is automatically merged. Split HTTP registration into `backend/conversation_routes.py` and transport helpers into `frontend/conversation_helpers.js` to keep service/storage and UI boundaries reviewable; these are file-organization refinements to the approved plan.
