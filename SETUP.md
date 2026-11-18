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

Preserve corrupt/read-only/disconnected storage for repair. A database observed by the process and then disconnected is not silently recreated. Incanta installs no renderer, proactive scheduler or notification helper.

## Optional local visuals

Use an **Incanta-only ComfyUI instance** on a loopback port. Start ComfyUI yourself with local nodes and weights and set `--disable-api-nodes --disable-metadata`. Restrict custom nodes to reviewed local nodes and Photoshoot. Incanta does not install, launch or download dependencies. Keep this instance separate from other UI or API workloads because ComfyUI releases model resources across the entire instance. A separate port on a shared process is insufficient.

The isolated API checks exercised ComfyUI **0.3.59**, checkout `707b2638ecd82360c0a67e1d86cc4fdeae218d03`, and Photoshoot `84f168d65a432c96b491858af0bf7d90dde807d7`. Pin the source checkouts independently. The renderer reports its released version and node schemas through HTTP. The full revisions in the local profile record the operator's source pins. [ComfyUI server](https://github.com/Comfy-Org/ComfyUI/blob/707b2638ecd82360c0a67e1d86cc4fdeae218d03/server.py) · [Photoshoot export hook](https://github.com/ralksta/ComfyUI-Photoshoot/blob/84f168d65a432c96b491858af0bf7d90dde807d7/js/shared.mjs)

| Setting | Meaning |
| --- | --- |
| `INCANTA_RENDERER_URL` | Local HTTP origin with port, for example `http://127.0.0.1:8189` |
| `INCANTA_RENDERER_DEDICATED=1` | Confirm this is an Incanta-only renderer |
| `INCANTA_WORKFLOW_ROOT` | Private directory holding named `<profile>.json` bundles |
| `INCANTA_REFERENCE_ROOT` | Private ComfyUI input directory when using `LoadImage` or `LoadImageMask` in the bundle |
| `INCANTA_RENDER_OUTPUT_ROOT` | Existing private directory with mode `0700` for Incanta's validated image copies |

Create the configured private directories before running. Use real directory paths without symbolic links for these roots. ComfyUI keeps its own source outputs, separate from Incanta's asset store. If an existing v1 SQLite database will be used, close Incanta and take a private SQLite backup before upgrading. The app adds visual tables with a transactional v2 migration when it next opens the database.

1. In the Photoshoot-enabled ComfyUI editor, set the person, wardrobe, expression and local identity conditioning. Export the resolved API prompt with Photoshoot enabled. The export must contain the node-level hidden builder inputs, including the saved JSON strings. Inspect the export against `/object_info/<node-class>`. Use the browser's resolved `graphToPrompt().output` if the installed export menu omits that state. A canvas export or Photoshoot series controls do not describe a single headless submission.
2. Wrap the API prompt using the shape in [the synthetic bundle](examples/render-workflow.example.json). Record the two source revisions and the renderer version. List each Photoshoot hidden state binding by its node ID and input name. Put `{incanta_scene}` exactly once in the chosen scene string, preserving the profile's other prompt text and Photoshoot placeholders. Select a single `SaveImage` output with a batch size of one. Reference files used by ComfyUI must be present in its input folder at the same relative names.
3. Save the private bundle as `<profile>.json` and enter the profile ID in **Portraits and scenes**. Request a portrait and approve or reject that candidate. An approved portrait remains available if the renderer disconnects after releasing resources. Changing a profile invalidates pending images. Automatic scenes start off and can be enabled separately for each conversation with a cooldown of 60–3600 seconds.
4. When a render is active, a new reply waits for the renderer to finish and takes the next idle slot ahead of queued images. A pending ComfyUI item can be deleted by its owned ID. Running cancellation suppresses display after it finishes. If ownership cannot be reconciled, restart the dedicated instance and verify the request is missing before resolving it. If the renderer could still own model resources, chat generation waits for release confirmation or returns a recoverable handoff error. Reconnect the same dedicated endpoint and use **Check renderer resource release** once its queue is idle. Saved chat and images remain available during recovery.

Read [feature 003 verification](specs/003-local-character-visuals/verification.md) for the tested hardware scope and owner acceptance. The model-free checks never load diffusion or GGUF weights.

## Verification

Run model-free Python/Node suites, then review [verification 002](specs/002-companion-conversations/verification.md). To explicitly check an already configured model with synthetic temporary SQLite state:

```sh
python scripts/verify_companion_model.py
```

This short native check does not replace the owner-reviewed 30-minute English conversation/restart acceptance. The historical [M1 runner](scripts/verify_local_model.py) explicitly selects its legacy app factory for baseline verification. Do not run either native check as part of ordinary test discovery or CI.
