# Models, private data and external storage

GitHub holds source and shared tooling, not every file from the original project. Never commit `.gguf`, `.safetensors`, diffusion `.bin` files, private personalities, histories, generated images, environments or archive backups.

## Suggested ownership

Keep one active Git checkout on the Mac. Keep a separate private asset location for models, character definitions and histories; this can be an external SSD. Keep complete diffusion-model folders, configuration files and all numbered shards together. Hugging Face caches may contain links: preserve their full structure rather than copying only apparent snapshot files.

Before removing an internal copy, verify the external copy and keep another backup of irreplaceable custom models, character work and memories. Repository setup does not authorize moving/deleting originals. See [the recovery audit](SOURCE_RECOVERY.md) for duplicate-folder findings.

## Current application versus planned configuration

The recovered app expects `models/Nous-Hermes-2-Mistral-7B-DPO.Q4_K_S.gguf`, `backend/personalities/celeste.json` and `chat_histories/` relative to the working directory. It does not yet consume `.env`. Keep launching it from the repository root. An existing filesystem link can point its model folder to an SSD, but no link or move has been created by this setup.

Specification 001 plans explicit environment settings for model, personality and data paths, lazy model loading and helpful disconnected-SSD errors. Those settings are not available until that feature is implemented. Do not edit tracked code merely to embed a personal volume path into a shared commit.

## Model provenance

Record a model's upstream identifier/revision, filename, license and checksum privately alongside the asset. A filename alone does not establish that two weights are identical. Public base models may be downloadable again; custom fine-tunes and private configurations may not be replaceable. Model licenses are separate from source/tooling licenses.
