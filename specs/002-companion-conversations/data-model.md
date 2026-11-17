# Data model and invariants

- **Conversation:** UUID id; title `1–120 characters`; personality `1–2000 characters`; relationship `0–1000 characters`; boundaries `1–2000 characters`; settings_revision/context_revision positive integers; current emotion; exactly seven gauges each `0–100`; created/updated UTC timestamps. Setup strings are private plain text. English UI; free-form owner settings.
- **Turn:** UUID id, conversation foreign key, request_id UUID, input `1–8000 characters after trimming`, nonempty response, committed timestamp, settings/context revision and resulting emotion/gauges. Unique `(conversation_id, request_id)`. Never store an incomplete turn as committed.
- **Fact:** UUID id, source_conversation_id, optional source_turn_id, content `1–2000 characters`, revision positive integer, created/updated timestamps. Source text may be owner-authored; source_turn_id cannot point to another conversation. Deleted facts become content-free tombstones with revision, not retained old content in an audit column.
- **FactGrant:** unique `(fact_id, conversation_id)`; source conversation always has access until deletion; recipient grant explicit. Revocation does not delete canonical fact. No separate copied fact content.
- **ImportRecord:** source checksum, destination conversation, schema version, completed UTC timestamp; unique checksum for repeated import prevention. Original bytes/backup remain ignored local assets; private source path is not an error/log field.

Fact edit/delete/revoke and context revision updates are transactional. Grant creation also bumps the recipient revision. A pending generation compares captured settings/context revisions immediately before commit. Source and sharing recipients must all lose deleted facts from future context; old transcript/backups are not implicitly rewritten.

Migration runs only after explicit preview/confirm. Malformed input, corruption, missing storage and failed backup leave existing data intact. Schema version mismatches fail safely. UUIDs identify records, not filesystem paths. All lookups use conversation ownership checks and parameterized SQL.
