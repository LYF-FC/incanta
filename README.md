# Incanta

A private, local AI character and conversation project. Incanta combines a local language model, emotional state and persistent memory. Development is restarting from recovered source, with specifications and small, verifiable changes.

**Status:** development foundations installed; application stabilization is next ([tracking issue #1](https://github.com/LYF-FC/incanta/issues/1)). The recovered app has known defects and has not yet passed a model-backed smoke test. The framework below does not claim those defects are fixed.

## Start here

| Need | Read |
| --- | --- |
| Understand priorities and completion gates | [Roadmap](ROADMAP.md) |
| Start or resume a feature | [Development workflow](docs/DEVELOPMENT.md) |
| Pick up the first implementation | [Reliable local chat specification](specs/001-reliable-local-chat/spec.md) · [tasks](specs/001-reliable-local-chat/tasks.md) |
| Install and run the recovered app | [Setup](SETUP.md) |
| Understand actual code and known defects | [Architecture](ARCHITECTURE.md) · [repository audit](docs/REPOSITORY_AUDIT.md) |
| Manage models, private files and an external SSD | [Assets and storage](docs/ASSETS.md) |
| Contribute or use an AI coding agent | [Contributing](CONTRIBUTING.md) · [agent instructions](AGENTS.md) |

## What exists today

Flask serves HTML/CSS/plain JavaScript at `http://127.0.0.1:5001`. `llama-cpp-python` loads a local GGUF model. Chat orchestration, heuristic gauges, emotion mappings and JSON memory are present. Personality files are loaded, but their fields are not yet used by the prompt. Image generation writes metadata only; live ComfyUI integration, React and FastAPI are not implemented in this source tree.

## Work without a model

For repository tooling, use Python 3.11+ and Git. No app dependencies or model downloads are required:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py --tracked
```

The default repository check reads staged/index content; `--tracked` checks the committed tree. Tests exercise repository safeguards, not application inference. GitHub Actions also checks JavaScript and Bash syntax.

## Specification-driven work

Official [GitHub Spec Kit](https://github.com/github/spec-kit) **v1.3.0**, including its Git extension, is installed in this repository. The CLI launcher is pinned to upstream commit `34a0d388eac671d656eb05b125ad3ed6056168ed`; see [provenance and upgrade instructions](docs/SPEC_KIT.md).

The Codex integration installs project skills. In a new Codex chat opened on this checkout, use `$speckit-specify`, `$speckit-plan`, `$speckit-tasks`, `$speckit-analyze` and `$speckit-implement`. The first feature is already seeded for review; follow its [resume instructions](docs/DEVELOPMENT.md#resume-the-first-feature) rather than creating it twice.

## Boundaries

Models, private personalities, memories, conversations and generated media stay outside Git, including private GitHub. Only synthetic examples are committed. See [security guidance](SECURITY.md) and the [project constitution](.specify/memory/constitution.md).

Incanta is an active experimental character engine, separate from the production Butler platform. It is not a production household service. Source provenance and legacy-folder recommendations are in the [recovery audit](docs/SOURCE_RECOVERY.md). No license for redistribution of Incanta has been selected; bundled Spec Kit files retain their MIT license in [third-party notices](THIRD_PARTY_NOTICES.md).
