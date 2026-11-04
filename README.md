# Incanta

Private, local AI conversation prototype and reference project. See [CONTEXT.md](CONTEXT.md) and [DECISIONS.md](DECISIONS.md) for its role alongside Butler.

## Recovered implementation

- Flask serves a plain HTML/CSS/JavaScript interface at `http://127.0.0.1:5001`.
- `llama-cpp-python` loads a local GGUF model at import time.
- `backend/` contains chat orchestration, heuristic gauges, emotion mapping, personality loading and JSON memory storage.
- `core/state.py` contains a separate character state implementation.
- `backend/image_gen.py` writes image metadata; it does not currently call ComfyUI.

The recovered source is preserved without behavior changes. React, FastAPI and live ComfyUI integration are not implemented in this snapshot.

## Setup

Follow [SETUP.md](SETUP.md). Models, personality definitions, conversations and environments are deliberately absent. Use synthetic character configuration for a fresh checkout.

`requirements.txt` is the original pinned environment snapshot, including transitive and unused packages. It is retained for recovery, not presented as a minimal or freshly validated dependency set. The source environment recorded Python 3.13.5. Installation and model inference have not been verified in this checkout.

## Known issues from source review

- `/api/status` returns only `status`; the frontend expects `emotion` and `gauges` too.
- The gauge engine checks an unconditional `Neutral` rule first, masking every other emotion.
- Each chat turn is persisted twice via `update_memories` and `store_event`.
- Personality JSON is loaded but not interpolated into the LLM prompt.
- The frontend inserts chat messages through `innerHTML` without escaping.
- Flask runs in debug mode and loads the model at import time; its reloader can initialize the model more than once.

Use only locally with synthetic data until these issues are addressed.

## Repository practice

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md). Never commit private memories, personality definitions, credentials, models or generated media, even to this private repository. The ignore rules are a safeguard; review staged contents before every commit.

The first source import continues the repository's existing documentation history. Other local project variants have not been merged. No redistribution license has been granted by this setup.
