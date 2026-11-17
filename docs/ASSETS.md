# Models, private data and external storage

GitHub holds source and shared tooling, not every file from the original project. Never commit GGUF/safetensors/diffusion weights, private character definitions, histories, generated images, environments or archive backups.

Keep one active Git checkout on the Mac and a separate private asset location, which may be an external SSD. Preserve complete diffusion-model folders/configuration/shards and complete linked cache structures. Verify copies before deleting originals and keep another backup of irreplaceable custom models, memories and character work. No original assets have been moved/deleted by this implementation.

## M1 baseline configuration (historical)

`INCANTA_MODEL_PATH`, `INCANTA_PERSONALITY_PATH` and `INCANTA_DATA_DIR` configure model, character and history locations without source edits. Paths are root-anchored when relative. Shell exports are supported; `.env` is not automatically read. Use [SETUP.md](../SETUP.md) for defaults and native dependency installation.

Models load lazily on chat requests. A missing/disconnected model or invalid character file produces a controlled error and no new history. Changing environment variables requires restarting the app; reconnecting files can be followed by **Check readiness** and a manual retry. Data directories may be created on the first successful persistence attempt, but never by a status check. Existing malformed histories are not silently replaced.

A successful event is written to a restrictive temporary file in the data directory and atomically replaces the prior document. One process is supported; concurrent processes or storage power loss require stronger guarantees than this baseline. Private backups remain necessary.

Record model identifier/revision/license/checksum privately with the asset. File names alone do not prove weights are identical. The source [recovery audit](SOURCE_RECOVERY.md) still records which original folders/archives contain unique material; this feature authorizes no cleanup.

## Companion state (002)

The active app now uses `INCANTA_DATABASE_PATH` (default `INCANTA_DATA_DIR/companion.sqlite`) for isolated conversations, settings, gauges/emotion and canonical facts/grants. No private personality JSON is needed; the short per-chat setup replaces it. Existing JSON histories are not opened or migrated automatically. The older configuration description above records M1 behavior; see the current [setup guide](../SETUP.md).

`INCANTA_IMPORT_PATH` selects exactly one legacy history for explicit preview/confirmation. The source is never modified, moved or deleted. Confirmation preserves byte-identical original content under the private database directory's `imports/` folder; unknown fields live in that preserved copy and duplicate exchanges remain duplicated in the imported transcript. Those copies contain private history and remain outside Git. Preview is bounded to 16 MiB; do not weaken limits/JSON allowlists to import arbitrary shared files.

Back up the private database and owned assets separately. This feature does not ship the consistent backup/restore tools planned in 005. A corrupt or disconnected database is preserved and reported; a missing previously observed database is not silently recreated. No originals or model assets were moved/deleted by 002 development or its tests.
