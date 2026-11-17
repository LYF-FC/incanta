# Local maintenance and acceptance contract

Planned commands; no hosted API. CLI operates only on explicitly configured local state, never scans private folders automatically.

- `python scripts/backup_incanta.py --destination <new-local-directory>`: maintenance gate, consistent DB/assets snapshot, private manifest/checksums, atomic completion. Refuse existing/nonempty target; stable safe status/exit code.
- `python scripts/restore_incanta.py --source <backup-directory> --destination <empty-local-directory> --verify-only`: validate without mutation. Omitting verify-only performs staged restore only after full validation and running-app exclusion.
- Exit 0 success, 2 invalid/unavailable configuration, 3 failed integrity/schema validation, 4 busy/running target, 5 I/O/publication failure. Shared output is safe counts/categories only; no content/path echo.
- No silent overwrite, deletion of originals, model download, environment installation, cloud upload or dispatch of restored jobs/notifications. Backup JSON remains local; it is not allowlisted for Git.
- Release record must show each component's actual verification status, clean setup, backup/restore, 30-minute dialogue/restart/three-scene owner verdict, native notification permission/denial behavior, timings and privacy/PR checks. A mandatory non-pass gate prevents tagging.
