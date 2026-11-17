# Incanta

A private, local AI character and conversation project. Incanta combines a local language model, emotional state and persistent memory. Development is restarting from recovered source, with specifications and small, verifiable changes.

**Status:** M1 and MVP plans are delivered in [merged PR #7](https://github.com/LYF-FC/incanta/pull/7). Feature 002 conversation/memory implementation passes automated, synthetic-browser and short native checks; owner-reviewed 30-minute acceptance is tracked in [issue #9](https://github.com/LYF-FC/incanta/issues/9); PR #8 awaits its correction commit’s CI/review. See [verification 002](specs/002-companion-conversations/verification.md) and the [M1 record](specs/001-reliable-local-chat/verification.md).

## Start here

| Need | Read |
| --- | --- |
| Understand priorities and completion gates | [Roadmap](ROADMAP.md) |
| Start or resume a feature | [Development workflow](docs/DEVELOPMENT.md) |
| Review the current companion implementation | [Conversations/memory specification](specs/002-companion-conversations/spec.md) · [tasks](specs/002-companion-conversations/tasks.md) · [verification](specs/002-companion-conversations/verification.md) |
| Install and run the recovered app | [Setup](SETUP.md) |
| Understand actual code and known defects | [Architecture](ARCHITECTURE.md) · [repository audit](docs/REPOSITORY_AUDIT.md) |
| Manage models, private files and an external SSD | [Assets and storage](docs/ASSETS.md) |
| Contribute or use an AI coding agent | [Contributing](CONTRIBUTING.md) · [agent instructions](AGENTS.md) |

## What exists today

Flask serves HTML/CSS/plain JavaScript at `http://127.0.0.1:5001`. Each Celeste conversation has its own short setup form, transcript, emotional state and explicitly saved facts. SQLite persists this state across restarts. Selected canonical facts can be shared between conversations; corrections/deletions propagate to every recipient's future fact retrieval. The interface includes inspect/correct/delete and sharing controls.

Local GGUF inference remains lazy. A configured private personality file is no longer required by the active conversation path. Legacy JSON history is imported only through an explicitly configured source, preview and confirmation, preserving exact original bytes. The old M1 engine remains available only to its explicit compatibility tests/smoke runner. Image generation is still metadata-only; live ComfyUI, notifications, React and FastAPI are not implemented.

## Work without a model

Use Python 3.11 or 3.13 and Git. Install the lightweight web/test dependency; no native inference package or model download is needed:

```sh
python3 -m pip install -r requirements-test.txt
python3 -m unittest discover -s tests -v
node --test tests/*.test.js
python3 scripts/check_repository.py --tracked
```

The default repository check reads staged/index content; `--tracked` checks the committed tree. Tests exercise repository safeguards and application acceptance with fake inference. GitHub Actions also checks JavaScript and Bash syntax. A separate manual local-model test verifies native inference.

## Specification-driven work

Official [GitHub Spec Kit](https://github.com/github/spec-kit) **v1.3.0**, including its Git extension, is installed in this repository. The CLI launcher is pinned to upstream commit `34a0d388eac671d656eb05b125ad3ed6056168ed`; see [provenance and upgrade instructions](docs/SPEC_KIT.md).

The Codex integration installs project skills. In a new Codex chat opened on this checkout, use `$speckit-specify`, `$speckit-plan`, `$speckit-tasks`, `$speckit-analyze` and `$speckit-implement`. Feature 001 has an implementation and verification record; read its [tasks](specs/001-reliable-local-chat/tasks.md) and current status before resuming or creating another feature.

## Boundaries

Models, private personalities, memories, conversations and generated media stay outside Git, including private GitHub. Only synthetic examples are committed. See [security guidance](SECURITY.md) and the [project constitution](.specify/memory/constitution.md).

Incanta is an active experimental character engine, separate from the production Butler platform. It is not a production household service. Source provenance and legacy-folder recommendations are in the [recovery audit](docs/SOURCE_RECOVERY.md). No license for redistribution of Incanta has been selected; bundled Spec Kit files retain their MIT license in [third-party notices](THIRD_PARTY_NOTICES.md).
