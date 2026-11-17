# Incanta

A private, local AI character and conversation project. Incanta combines a local language model, emotional state and persistent memory. Development is restarting from recovered source, with specifications and small, verifiable changes.

**Status:** M1 reliability changes implemented; automated, synthetic-browser and explicit native-model/process-restart checks pass; delivery review remains pending ([tracking issue #1](https://github.com/LYF-FC/incanta/issues/1)). See the [verification record](specs/001-reliable-local-chat/verification.md) for completed checks and remaining gates.

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

Flask serves HTML/CSS/plain JavaScript at `http://127.0.0.1:5001`. `llama-cpp-python` lazily loads a configured local GGUF model on the first valid chat request. Startup/status work without private assets. Chat orchestration, heuristic gauges, emotion mappings and JSON memory are present. Personality files are loaded, but their fields are not yet used by the prompt. Image generation writes metadata only; live ComfyUI integration, React and FastAPI are not implemented in this source tree.

## Work without a model

Use Python 3.11 or 3.13 and Git. Install the lightweight web/test dependency; no native inference package or model download is needed:

```sh
python3 -m pip install -r requirements-test.txt
python3 -m unittest discover -s tests -v
node --test tests/frontend.test.js
python3 scripts/check_repository.py --tracked
```

The default repository check reads staged/index content; `--tracked` checks the committed tree. Tests exercise repository safeguards and application acceptance with fake inference. GitHub Actions also checks JavaScript and Bash syntax. A separate manual local-model test verifies native inference.

## Specification-driven work

Official [GitHub Spec Kit](https://github.com/github/spec-kit) **v1.3.0**, including its Git extension, is installed in this repository. The CLI launcher is pinned to upstream commit `34a0d388eac671d656eb05b125ad3ed6056168ed`; see [provenance and upgrade instructions](docs/SPEC_KIT.md).

The Codex integration installs project skills. In a new Codex chat opened on this checkout, use `$speckit-specify`, `$speckit-plan`, `$speckit-tasks`, `$speckit-analyze` and `$speckit-implement`. Feature 001 has an implementation and verification record; read its [tasks](specs/001-reliable-local-chat/tasks.md) and current status before resuming or creating another feature.

## Boundaries

Models, private personalities, memories, conversations and generated media stay outside Git, including private GitHub. Only synthetic examples are committed. See [security guidance](SECURITY.md) and the [project constitution](.specify/memory/constitution.md).

Incanta is an active experimental character engine, separate from the production Butler platform. It is not a production household service. Source provenance and legacy-folder recommendations are in the [recovery audit](docs/SOURCE_RECOVERY.md). No license for redistribution of Incanta has been selected; bundled Spec Kit files retain their MIT license in [third-party notices](THIRD_PARTY_NOTICES.md).
