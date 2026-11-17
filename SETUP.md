# Setup

Use Python 3.11 or 3.13 for the lightweight web/test runtime (CI checks both). Local native inference is platform-specific and has a separate dependency. The original `requirements.txt` remains an unchanged historical snapshot, not the recommended restart install.

## Lightweight runtime and tests

From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
node --test tests/frontend.test.js
python frontend_app.py
```

Open `http://127.0.0.1:5001`. The interface and status work without a model or character file; they show what is missing. Importing the app and checking readiness do not initialize inference or create histories. Flask debug/reloader are disabled. `bash run.sh` is an alternative launcher; it changes to the repository directory first. No Node install/build is needed to serve the frontend; Node is only needed for frontend regression checks.

## Optional local inference

Install the separately pinned optional dependency with a platform-appropriate native build. A conservative CPU build on macOS with Xcode command-line tools and CMake is:

```sh
CMAKE_ARGS='-DGGML_METAL=OFF -DGGML_NATIVE=OFF' python -m pip install --no-binary llama-cpp-python -r requirements-inference.txt
```

This installs software, not model weights. Downloading a model is never automatic. GPU acceleration/build variants are separate choices; no GPU performance target is promised by this baseline. See the [upstream installation guide](https://github.com/abetlen/llama-cpp-python#installation) for other platforms. On 2026-11-17, the existing 0.3.36 installation passed an explicit owned-model smoke check with CPU-default settings and access to the Mac native runtime. The restricted environment could not create a Metal command queue even with zero GPU layers. See the verification record for exact scope; this does not certify other builds or models.

## Configure your assets

Use synthetic character configuration for the first run:

```sh
mkdir -p backend/personalities
cp examples/personality.example.json backend/personalities/celeste.json
```

Place an already-owned model at the default ignored path, or set an explicit local/external-SSD path. Shell environment settings are read; `.env` files are not automatically loaded.

| Setting | Default | Meaning |
| --- | --- | --- |
| `INCANTA_MODEL_PATH` | `models/Nous-Hermes-2-Mistral-7B-DPO.Q4_K_S.gguf` | Readable, nonempty local GGUF file |
| `INCANTA_PERSONALITY_PATH` | `backend/personalities/celeste.json` | Local JSON object; prompt schema/integration is still M3 |
| `INCANTA_DATA_DIR` | `chat_histories/` | Writable private history directory; file name derives from character-file stem |
| `INCANTA_HOST` | `127.0.0.1` | Loopback only: `127.0.0.1`, `localhost`, or `::1` |
| `INCANTA_PORT` | `5001` | Port 1–65535 |
| `INCANTA_CONTEXT_LENGTH` | `4096` | Context window, validated 128–131072 |
| `INCANTA_GPU_LAYERS` | `0` | CPU default; -1–1000 accepted for compatible local builds |
| `INCANTA_THREADS` | `8` | Threads, validated 1–256 |

Relative configured paths are anchored to the repository root, not the shell working directory. External storage must remain connected. Missing assets yield a controlled readiness/error state without downloads or remote inference. After fixing configuration, use **Check readiness** or restart when changing environment variables. The model loads only on the first valid chat request, once per app instance.

For a model on an SSD, export its actual path before starting the app, for example `INCANTA_MODEL_PATH='/Volumes/YourSSD/Models/your-model.gguf'`. Do not put private paths into tracked source or shared logs. The example is a placeholder, not an existing volume or a request to move files.

## Runtime boundaries

One local process and one active conversation are supported. Do not launch multiple workers or use this as a hosted service. Overlapping requests return busy; the UI also disables submission while awaiting a response. There is no automatic retry. A successful turn stores exactly one event, then publishes its in-memory state; failed generation/storage does not advance committed state. Atomic replacement protects the prior file from incomplete writes, but is not a full backup or multi-process transaction system.

Existing unknown memory fields and historical duplicates are retained. Malformed histories are preserved and produce an error instead of being silently reset. Recent in-memory dialogue/gauges reset on restart; durable timeline history reloads. Factual-memory heuristics and personality prompt integration remain known limitations for M2/M3. Native-library crashes can still terminate the process; use a verified compatible native runtime.

## Verification and privacy

See [the feature verification record](specs/001-reliable-local-chat/verification.md), [testing guide](docs/TESTING.md) and [asset guide](docs/ASSETS.md). Stage explicit reviewed paths, run `python scripts/check_repository.py`, then inspect `git diff --cached`. Use `--tracked` after committing to inspect HEAD. No private history, personality, model, environment, generated media or archive belongs in Git.
