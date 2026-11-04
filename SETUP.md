# Setup

## Environment

Recovered from a macOS Python 3.13.5 environment. Create a new environment rather than moving or committing the original one. Run all commands from the repository root.

```sh
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The pinned file is an unmodified historical environment snapshot. Native `llama-cpp-python` builds may need Xcode command-line tools and platform-specific configuration. No dependencies have been installed or upgraded during source recovery.

## Local assets

1. Create `models/` and place your separately obtained, appropriately licensed model at `models/Nous-Hermes-2-Mistral-7B-DPO.Q4_K_S.gguf`. The filename is currently hard-coded in `backend/llm_interface.py`.
2. Create a synthetic personality file:

```sh
mkdir -p backend/personalities
cp examples/personality.example.json backend/personalities/celeste.json
```

Existing private personalities can remain in the original local project; do not stage or copy them into repository history. The loader requires a JSON file, though its fields are currently unused by the prompt builder.

The application does not currently read `.env` settings. Changing a model path or runtime setting requires a source edit. No Node install or frontend build step is needed. No working ComfyUI integration is present in this snapshot.

## Start locally

```sh
python frontend_app.py
```

Open `http://127.0.0.1:5001`. Alternatively use `bash run.sh` with the environment activated. Debug mode is enabled in the recovered code. Do not expose this prototype to a network.

Runtime memories go to `chat_histories/`; image metadata goes to `generated_images/`. Both are ignored, as are `data/`, all private personality directories and model files.

## Repository checks

```sh
python3 scripts/check_repository.py
git diff --cached --stat
```

The check scans staged blobs, or tracked blobs when invoked with `--tracked`, for forbidden paths, large files, common credential patterns and Python syntax errors. It does not import the app or load any model. It is a limited guard, not a guarantee that arbitrary prose contains no private information.

Read the known issues in [README.md](README.md) before attempting an application smoke test. A full model-backed run remains unverified.
