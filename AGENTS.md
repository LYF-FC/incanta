# Incanta agent instructions

Read `README.md`, `CONTEXT.md`, `.specify/memory/constitution.md`, `ROADMAP.md` and the active feature's spec/plan/tasks before changing behavior. `docs/REPOSITORY_AUDIT.md` distinguishes current defects from planned work.

## Scope and evidence

Keep the existing Flask/plain JavaScript stack unless a specification changes it. Never claim React, FastAPI or live ComfyUI is implemented here. M1 is delivered through merged PR #7; 002 continues on its existing branch/PR #8 with the owner's green-CI merge authorization. Read each feature's tasks and verification record before claiming completion; owner dialogue acceptance remains explicit in issue #9. Do not treat planning checklists as proof of runtime verification.

Use `./scripts/specify.sh` for CLI commands that upstream instructions refer to as `specify`; no global CLI install is assumed.

For a feature, use the installed `.agents/skills/speckit-*` workflows. Set `SPECIFY_FEATURE_DIRECTORY` to the intended feature directory when resuming work. Do not create a second spec or branch for an existing feature. The full runner can proceed into implementation; use individual steps when doing planning only.

## Privacy and local assets

Do not read private personalities, memories, conversation histories or credentials unless necessary and authorized for the current task. Never print or commit their contents. Do not load/download models, call external inference, or run model-backed smoke tests as a side effect of repository checks. Use synthetic examples, fake inference and temporary storage.

Track only the explicit shared Spec Kit JSON allowlist. Do not weaken privacy rules to accommodate arbitrary files. `.specify/feature.json`, per-machine overrides, `.codex/` and agent runtime/auth state are local-only. Installed skill instructions are shared.

Do not delete/move original source folders, archives or model assets under the guise of cleanup. A path on an external SSD is not permission to remove a local copy.

## Verification and delivery

Run `python3 -m unittest discover -s tests -v`, the staged repository checker, and `git diff --cached --check` for relevant changes. Check modified JavaScript with `node --check`; Bash with `bash -n`. Repository-only checks need no app dependencies. Full acceptance tests install the lightweight `requirements-test.txt`; never install native inference just for CI. Keep `requirements.txt` as the historical snapshot until a separate dependency change.

Use reviewed branches and PRs, no force-pushes, and explicit staging. Report what changed, what was tested and what remains unverified. Keep generated Spec Kit files upstream-compatible; record customizations and preserve the upstream license. The project owner's instructions remain authoritative.
