<!-- Sync impact: initial project constitution, 1.0.0, 2026-11-04.
Principles added: privacy/local execution; evidence-based scope; spec before behavior;
reproducible verification; simple architecture and durable data. Upstream templates
are retained unchanged and read this constitution at runtime. No deferred placeholders. -->
# Incanta Constitution

## Core Principles

### I. Private data stays local

Private personalities, memories, conversations, credentials, model weights and generated assets MUST NOT enter repository history, issues, CI artifacts or shared logs. Only synthetic fixtures may be committed. Inference stays local by default; external inference, automatic downloads or data export require an explicit feature decision and owner authorization. Repository visibility is not a data-handling control.

### II. Describe implemented behavior accurately

Documentation MUST distinguish recovered behavior, known defects, planned design and tested outcomes. A specification or passing syntax check MUST NOT be presented as a working feature. Current source evidence takes precedence over old chat descriptions. Incanta remains experimental and separate from Butler production services.

### III. Specify meaningful behavior changes

A feature MUST have user scenarios, testable requirements, acceptance criteria, scope limits and an implementation plan before substantial code changes. Tasks MUST trace to requirements. Small documentation/tooling corrections may use a focused PR without a separate feature spec. Assumptions and material tradeoffs MUST be recorded, not hidden in prompts.

### IV. Verify with synthetic, reproducible checks

Automated checks MUST run without private data, real model weights or external inference. Application code MUST become testable with fake inference and temporary storage as M1 is implemented. Behavior changes require relevant regression evidence. Manual model-backed checks MUST state hardware/model context and result without publishing conversation contents.

### V. Prefer a small, recoverable local architecture

Stabilize the existing stack before changing frameworks. Models and data locations MUST be explicitly configurable in new runtime work. Storage changes MUST preserve existing user data or provide a tested migration/backup procedure. Missing assets and a disconnected SSD MUST be handled without automatic deletion, silent reset or cloud fallback.

## Development and data boundaries

Use branches, explicit staging and pull requests. Run repository safeguards and relevant tests before merge. Preserve the recovered dependency snapshot until a dedicated review. CI must not install that heavyweight runtime merely to validate documentation or repository tooling. Legacy source and archives are retained until the owner approves a concrete cleanup.

Shared Spec Kit templates, scripts, manifests and constitution belong in Git. Current-feature pointers, per-machine overrides and agent authentication/session state do not. The repository checker enforces exact metadata exceptions and remains a limited safeguard requiring human content review.

## Governance

This constitution governs Incanta development; owner instructions take precedence. Amendments must state the change, rationale, affected specs and verification implications in a reviewed commit. Increment major for incompatible principle changes, minor for new principles or materially expanded guidance, patch for clarifications. Resolve constitution/spec conflicts before implementation and record the resolution.

Review feature requirements, plan and tasks together before execution. GitHub branch protection and mandatory owner approval are not presumed merely because CODEOWNERS exists. No open-source license for Incanta is selected by this constitution; third-party tooling retains its own license.

**Version**: 1.0.0 | **Ratified**: 2026-11-04 | **Last Amended**: 2026-11-04
