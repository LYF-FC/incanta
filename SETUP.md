# Setup

Use Python 3.11 or 3.13 for the lightweight web/test runtime (CI checks both). Local native inference is platform-specific and has a separate dependency. The original `requirements.txt` remains an unchanged historical snapshot, not the recommended restart install.

## Lightweight runtime and tests

From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -v
node --test tests/*.test.js
python frontend_app.py
```

Open `http://127.0.0.1:5001`. The interface and status work without a model or character file; they show what is missing. Importing the app and checking readiness do not initialize inference or create histories. Flask debug/reloader are disabled. `bash run.sh` is an alternative launcher; it changes to the repository directory first. No Node install/build is needed to serve the frontend; Node is only needed for frontend regression checks.

## Optional local inference

Install the separately pinned optional dependency with a platform-appropriate native build. A conservative CPU build on macOS with Xcode command-line tools and CMake is:

```sh
CMAKE_ARGS='-DGGML_METAL=OFF -DGGML_NATIVE=OFF' python -m pip install --no-binary llama-cpp-python -r requirements-inference.txt
```

This installs software, not model weights. Downloading a model is never automatic. GPU acceleration/build variants are separate choices; no GPU performance target is promised by this baseline. See the [upstream installation guide](https://github.com/abetlen/llama-cpp-python#installation) for other platforms. On 2026-11-17, the existing 0.3.36 installation passed an explicit owned-model smoke check with CPU-default settings and access to the Mac native runtime. The restricted environment could not create a Metal command queue even with zero GPU layers. See the verification record for exact scope; this does not certify other builds or models.

## Configure the companion runtime

Set `INCANTA_MODEL_PATH` locally to an already-owned GGUF. The default remains the ignored `models/Nous-Hermes-2-Mistral-7B-DPO.Q4_K_S.gguf`; there is no automatic download or cloud fallback. Relative paths are anchored to the repository root. Shell environment variables are read; `.env` files are not loaded automatically.

| Setting | Default | Meaning |
| --- | --- | --- |
| `INCANTA_DATABASE_PATH` | `INCANTA_DATA_DIR/companion.sqlite` | Private conversation database; never replace an unreadable existing file |
| `INCANTA_DATA_DIR` | `chat_histories/` | Default private data location |
| `INCANTA_IMPORT_PATH` | unset | One owner-selected legacy JSON file, read only after explicit preview/confirm |
| `INCANTA_MODEL_PATH` | ignored local model path above | Already-owned readable GGUF |
| `INCANTA_HOST` / `INCANTA_PORT` | `127.0.0.1` / `5001` | Loopback-only server |
| `INCANTA_CONTEXT_LENGTH` | `4096` | Model context window; 256 output tokens plus conservative prompt overhead reserved |
| `INCANTA_GPU_LAYERS` / `INCANTA_THREADS` | `0` / `8` | Existing optional native inference settings |
| `INCANTA_PERSONALITY_PATH` | legacy default | Used only by the explicit M1 compatibility harness; active chats use their setup form |

Opening the page, listing conversations and checking readiness do not initialize inference or create a missing database. The first conversation creation initializes its schema. Create a conversation with a name, personality and content boundaries; relationship description is optional. Choose a saved conversation to restore its settings, transcript and emotional state. Model obedience to settings is evaluated by the owner, not guaranteed by the form.

Use **Memories and sharing** to save selected facts, optionally sourced to an exchange. Facts are not inferred automatically from model text. Share only the selected fact with another named conversation. Correct/delete applies everywhere that canonical fact is shared; deleting it excludes future fact retrieval but does not erase old transcript text or older backups.

## Optional legacy import

Set `INCANTA_IMPORT_PATH` to the exact local history file and restart. No folder is scanned. Complete the short setup form (or open **Edit setup**), expand **Import a selected legacy history**, preview counts/setup, then explicitly confirm. Preview expires after ten minutes; files are limited to 16 MiB for this bounded importer. A changed/malformed source requires a new preview.

Confirmation preserves original bytes, unknown fields and duplicate entries in a private copy under the database directory's `imports/` folder before a transactional import. Duplicate exchanges are imported; unknown fields remain in the exact preserved copy. Repeating import confirmation does not duplicate an already imported checksum. No source is moved, changed or deleted; old inferred milestones do not become verified facts. The preserved copy is not a complete application backup.

## Runtime and API boundaries

One owner and one server process are supported. One generation runs at a time across conversations; overlapping requests return busy. Per-conversation UUID request identifiers make explicit retries idempotent. Settings or facts changed during generation invalidate the pending result before commit. Inference/storage failures do not advance committed state. Conservative UTF-8 prompt budgeting trims oldest dialogue and bounds selected facts; an oversized message/setup can require shortening even below the 8,000-character transport limit.

The active API uses `/api/conversations/{id}/turns`; `/api/chat` returns `conversation_required`. Obtain a CSRF token from `/api/bootstrap` and send it with the local session cookie, exact local `Origin`, JSON content type and `X-CSRF-Token` on mutations. There is no CORS expansion or multi-user authentication. Restarting clears browser session tokens; reload the page to bootstrap again. No private content is stored in session cookies.

Preserve corrupt/read-only/disconnected storage for repair. A database observed by the process and then disconnected is not silently recreated. No ComfyUI, proactive scheduler or notification helper is installed by this feature.

## Verification

Run model-free Python/Node suites, then review [verification 002](specs/002-companion-conversations/verification.md). To explicitly check an already configured model with synthetic temporary SQLite state:

```sh
python scripts/verify_companion_model.py
```

This short native check does not replace the owner-reviewed 30-minute English conversation/restart acceptance. The historical [M1 runner](scripts/verify_local_model.py) explicitly selects its legacy app factory for baseline verification. Do not run either native check as part of ordinary test discovery or CI.
