# Research and decisions

**Date:** 2026-11-17. Design evidence, not runtime proof. Research performed through the installed planning workflow's research-agent step. No private data was accessed.

- **Decision:** use stdlib SQLite and short transactions with foreign keys enabled per connection. **Rationale:** atomic turns/revisions/grants without a service dependency. **Alternatives:** JSON remains the M1 baseline but independent copies make shared deletion fragile; PostgreSQL is unnecessary for one owner. [SQLite isolation](https://www.sqlite.org/isolation.html), [foreign keys](https://www.sqlite.org/foreignkeys.html), [Python sqlite3](https://docs.python.org/3.13/library/sqlite3.html).
- **Decision:** canonical facts plus explicit grants and monotonic context revisions. **Rationale:** corrections/deletions invalidate all recipients and stale in-flight results. **Alternatives:** copied facts drift; embedding retrieval adds unneeded POC complexity. This is a project design inference from required semantics, not a vendor guarantee.
- **Decision:** explicit user-saved facts with provenance, not generated heuristic extraction. **Rationale:** the current sibling heuristic persists unsupported claims; bounded owner control is testable. Automatic extraction is deferred.
- **Decision:** preserve legacy JSON and unknown fields through opt-in import/backups, using consistent SQLite backups once migrated. **Rationale:** no silent destructive migration. **Alternative:** rewriting legacy files in place is rejected. Use `Connection.backup()` rather than copying an open database file.
- **Decision:** typed system messages and bounded per-conversation context with revision rechecks. **Rationale:** settings must influence prompts and stale shared facts must not be published. Model compliance still needs owner evaluation.

No unresolved architecture decision blocks task generation. Model quality and actual timing remain native acceptance measurements, not invented research results.
