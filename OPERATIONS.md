# Operations

## Current status

Experimental local application, with the defects listed in [the audit](docs/REPOSITORY_AUDIT.md). M1 reliability changes are implemented; see the feature verification record for native-runtime evidence. Follow [SETUP.md](SETUP.md) for the recovered behavior and [testing guidance](docs/TESTING.md) for evidence requirements.

## Routine development

Pull with `git pull --ff-only` on a clean branch. Run lightweight repository checks. Work through one feature spec and use synthetic data. Keep Flask local; debug/reloader are disabled. CI never needs private personalities, conversations or real models.

## Backups and recovery

GitHub restores tracked source, shared tooling and specifications only. Back up private assets and histories separately, preferably with a second copy of irreplaceable data. Preserve model-folder structure and verify SSD copies before deleting internal files. Neither Spec Kit nor Git provides a backup of ignored files.

No automated migration/reset/cleanup of old memories is authorized by this foundation. Until M2 defines a recovery policy, preserve corrupted files for private repair and avoid overwriting them. M1 atomic writes reduce interruption risk but do not provide full transactional/multi-user storage or replace backups.

## Releases and reuse

Do not tag a working release solely because documentation/CI passes. Complete its acceptance gates, a model-backed smoke test and backup/restore evidence first. Before extracting code for Butler, review dependencies, storage, authentication, audit and permissions independently. No public deployment, hosting or automatic model download is configured.
