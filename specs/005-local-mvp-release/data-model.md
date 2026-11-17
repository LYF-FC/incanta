# Backup and release evidence model

- **BackupManifest (private):** format_version positive integer, DB schema_version, created UTC time, app revision, DB hash, relative asset keys/hashes/byte counts, optional private runtime dependency identities, completed flag. Only regular contained files; no symlinks, absolute paths, traversal or executable hooks. Weights excluded by default.
- **RestoreReport:** safe status codes for manifest/integrity/schema/relations/assets and publication state; never private content/full paths in shared logs. Unsupported schema fails before modification. Operational jobs/claims reset to reconciliation-required and no historical notifications auto-send.
- **AcceptanceGate:** stable ID, feature/reference, required boolean, state `pending|pass|fail|blocked`, date, environment summary and evidence location. 'Blocked' for a check is a result description, not an autonomous goal status.
- **CompatibilityRecord:** OS/chip/RAM, Python/native build/node versions, model/workflow hashes, measured timing/peak memory and observed limitations. Private paths excluded from shared record.

A published backup must have matching checksums and completed manifest. Backup source is preserved. Restore publication is atomic into an empty destination. Owner verdict is explicit; unchecked tasks or planning checklists do not count as verification.
