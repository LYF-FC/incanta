# Spec Kit installation and maintenance

## Provenance

- Upstream: [github/spec-kit](https://github.com/github/spec-kit).
- Release: `v1.3.0`, published 2026-11-03.
- Source commit: `34a0d388eac671d656eb05b125ad3ed6056168ed`.
- Integration: Codex skills, Bash helpers.
- Bundled Git extension: `1.0.3`; bundled SDD workflow: `1.0.1`.
- License: MIT; retained verbatim in `.specify/UPSTREAM_LICENSE`.

Initialized with the official CLI from that source using `init --here --force --non-interactive --integration codex --integration-options='--events false' --script sh --extension git`. No application source or historical requirements were replaced. The CLI used an isolated temporary tool environment; no global `specify` installation was added. `scripts/specify.sh` provides a reproducible pinned launcher through uvx.

## Shared versus local

Track `.agents/skills/speckit-*/SKILL.md`, `.specify/` templates/scripts, the constitution, Git config and the exact non-sensitive metadata allowlist in `scripts/check_repository.py`. Installed manifests preserve hashes for upstream files.

Ignore `.specify/feature.json`, local extension overrides, executable adapter packages, `.codex/` and other agent runtime/auth state. The constitution is an explicit exception to the general private `memory/` rule. Do not allow an entire JSON directory just to make staging easier.

## Configuration choices

Codex runtime events are disabled: the workflow runs on explicit skill invocation. Git auto-commit defaults and per-command flags remain false, so privacy review precedes commits. The official full workflow retains its upstream review gates; individual commands are usually easier for this project. No additional agents, external integrations or third-party extensions were installed.

The constitution and first feature artifacts are project-authored. Upstream core templates and installed skills are retained unchanged. `AGENTS.md` is project guidance, not a generated replacement for the constitution.

## Verify

```sh
./scripts/specify.sh version
./scripts/specify.sh check
SPECIFY_FEATURE_DIRECTORY=specs/001-reliable-local-chat bash .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
```

## Upgrade deliberately

Create a clean maintenance branch. Review the [official upgrade guide](https://github.github.io/spec-kit/upgrade.html) and a selected upstream release. Update the pinned launcher commit and provenance together. Use the upgraded CLI's integration upgrade/init instructions, then review every changed manifest, skill, helper and license. Preserve the project constitution and feature artifacts. Rerun repository tests, privacy checks, syntax validation and feature prerequisite checks before merging. Never use `--force` on unreviewed local changes.
