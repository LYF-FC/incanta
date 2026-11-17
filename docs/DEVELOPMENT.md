# Development workflow

## First session

Read the README, roadmap, audit and constitution. Repository checks need Python 3.11+ and Git; JavaScript syntax checking additionally needs Node. Use a new Codex chat on this project after pulling the installed skills. The CLI launcher needs [uv](https://docs.astral.sh/uv/); its first use downloads development-tool dependencies, not application models.

```sh
./scripts/specify.sh version
./scripts/specify.sh check
```

## Start a new feature

In Codex chat, use the installed steps individually:

1. `$speckit-specify` followed by the user outcome and scope.
2. `$speckit-clarify` if material ambiguity remains.
3. `$speckit-plan` to produce design, research and contracts.
4. `$speckit-tasks` for traceable implementation steps.
5. `$speckit-analyze` to find gaps across those artifacts.
6. `$speckit-implement` when the implementation is actually in scope.

The Git extension creates numbered feature branches. Core specs live under `specs/<number>-<name>/`; the branch and directory are independent. Automatic Git commits are disabled. Inspect and stage content explicitly. These are Codex skill invocations, not terminal commands. The all-in-one workflow is optional and can enter implementation; do not run it for a documentation-only task.

## Resume the first feature

Specification `001-reliable-local-chat` was hand-seeded from the installed upstream templates during bootstrap. Implementation is present on its existing branch. Read its tasks and verification record: automated, synthetic browser and explicit native-model/process-restart checks pass; reviewed delivery remains pending.

```sh
git switch 001-reliable-local-chat
export SPECIFY_FEATURE_DIRECTORY=specs/001-reliable-local-chat
bash .specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
```

If the branch already exists, switch to it instead of creating another. If resuming in another tool/session, explicitly name the same feature directory; `.specify/feature.json` is only a local pointer. Run `$speckit-analyze` with that feature selected, then implement the task list when requested. Do not rerun `$speckit-specify` for the already-created feature. Running setup-plan/setup-tasks can regenerate files; read existing artifacts before doing so.

## During a change

Use temporary data and fake inference. Update the feature's unchecked tasks only when their behavior and verification are complete. Record decisions that change the architecture in `DECISIONS.md`. Avoid unrelated framework changes or copying a legacy tree over the baseline.

```sh
python3 -m unittest discover -s tests -v
node --check frontend/app.js
bash -n run.sh
# Stage only intended paths, then:
python3 scripts/check_repository.py
git diff --cached --check
```

The current suites protect repository tooling and application behavior with fake inference and temporary data; they do not prove native-model compatibility. GitHub CI runs on pull requests and pushes to main with read-only permissions, pinned action commits and no private/model assets.

## Review and merge

Open a PR using the template, link its spec or issue, and state validation plus remaining manual checks. Review requirements as well as code. Merge after relevant checks pass; branch-protection enforcement is a separate repository setting. Update roadmap status only after its exit gate is met. Tag a release only after its documented real-model and backup/restore checks.

## Source of truth

Roadmap: priorities. Spec: expected behavior. Plan/contracts: implementation decisions. Tasks: execution status. Audit: current evidence. Issues: coordination links. Changes to one must not silently contradict the others.
