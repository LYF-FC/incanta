# Models, private data and external storage

GitHub holds source and shared tooling, not every file from the original project. Never commit GGUF/safetensors/diffusion weights, private character definitions, histories, generated images, environments or archive backups.

Keep one active Git checkout on the Mac and a separate private asset location, which may be an external SSD. Preserve complete diffusion-model folders/configuration/shards and complete linked cache structures. Verify copies before deleting originals and keep another backup of irreplaceable custom models, memories and character work. No original assets have been moved/deleted by this implementation.

## Active configuration

`INCANTA_MODEL_PATH`, `INCANTA_PERSONALITY_PATH` and `INCANTA_DATA_DIR` configure model, character and history locations without source edits. Paths are root-anchored when relative. Shell exports are supported; `.env` is not automatically read. Use [SETUP.md](../SETUP.md) for defaults and native dependency installation.

Models load lazily on chat requests. A missing/disconnected model or invalid character file produces a controlled error and no new history. Changing environment variables requires restarting the app; reconnecting files can be followed by **Check readiness** and a manual retry. Data directories may be created on the first successful persistence attempt, but never by a status check. Existing malformed histories are not silently replaced.

A successful event is written to a restrictive temporary file in the data directory and atomically replaces the prior document. One process is supported; concurrent processes or storage power loss require stronger guarantees than this baseline. Private backups remain necessary.

Record model identifier/revision/license/checksum privately with the asset. File names alone do not prove weights are identical. The source [recovery audit](SOURCE_RECOVERY.md) still records which original folders/archives contain unique material; this feature authorizes no cleanup.
