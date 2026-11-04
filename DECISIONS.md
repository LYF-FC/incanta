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

**Status:** policy accepted; runtime configuration implementation planned in specification 001.

Models, private personalities, memories and outputs stay outside repository history. Support external storage through explicit configuration. A disconnected SSD must produce a useful readiness/error state; no automatic cloud fallback or model download.

## ADR-005 — Test without real models by default

**Status:** tooling active; application adapter/tests planned in specification 001.

Repository CI uses synthetic data and no model downloads. Future application tests inject fake inference and temporary storage. Real inference remains an explicit manual check with hardware/model identity and result, excluding prompts and responses from shared logs.

## ADR-006 — Small reviewed Git changes

**Status:** active convention, 2026-11-04.

Use branches and pull requests with passing checks. CODEOWNERS assigns the owner; required reviews and branch protection are not assumed or claimed. Spec Kit automatic commits are disabled so staged content is reviewed explicitly. Archive legacy work only after checking unique source/private assets; this setup authorizes no deletion.

## ADR-007 — Preserve dependency and license provenance

**Status:** active, 2026-11-04.

Keep the recovered `requirements.txt` unchanged until a dedicated dependency review. It is not a minimal or security-certified environment. Incanta has no redistribution license selected. Bundled Spec Kit retains upstream MIT terms; this does not license the rest of the project or downloaded models.
