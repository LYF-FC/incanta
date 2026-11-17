# Research and decisions

**Date:** 2026-11-17. No backup/restore/native release executed by planning.

- **Decision:** SQLite backup API plus maintenance gate for asset consistency. **Rationale:** copying a live DB/sidecars is not a safe snapshot; the gate prevents asset references changing during the snapshot. **Alternative:** tar an active runtime directory—rejected. [Python SQLite backup](https://docs.python.org/3.13/library/sqlite3.html#sqlite3.Connection.backup).
- **Decision:** restore into new empty destination with checksums/schema/path validation and inert historical jobs. **Rationale:** preserves recoverability and prevents notification/re-render replay. **Alternative:** overwrite running app data—rejected.
- **Decision:** dedicated dependency review retains historical freeze and splits native/render/helper installs. **Rationale:** M1 test runtime stays lightweight; actual native compatibility must be measured. No dependency or model revision is asserted compatible before its acceptance check.
- **Decision:** owner visual/dialogue verdict plus mechanical checks. **Rationale:** three generated files do not prove reference resemblance or a coherent character. Exact acceptance checklist separates failure, pending and pass.
- **Decision:** future Mac mini/Nomad migration deferred until hardware/runtime evidence exists. **Rationale:** source separation from Butler remains; no inherited production-service dependency.
