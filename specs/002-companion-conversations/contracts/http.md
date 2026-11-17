# Local conversation and memory contract

Delivered in merged PR #8; actual checks and remaining acceptance are in [verification](../verification.md). Loopback only; no CORS expansion. Existing status readiness remains. Requests require JSON, retain 64 KiB transport cap, validate UUIDs and data-model limits. Errors use M1 `{error:{code,message}}` with no private paths/content. Mutations require same-origin validation and a local session CSRF token obtained from app bootstrap; read-only status remains available without private assets. This does not introduce multi-user authentication.

| Method/path | Request | Success |
| --- | --- | --- |
| GET /api/conversations | none | 200 list of id/title/updated_at; no transcripts |
| POST /api/conversations | title, personality, relationship, boundaries | 201 id, settings_revision, context_revision, state |
| GET /api/conversations/{id} | none | 200 setup, state and committed turns; cursor pagination, default 50, max 100 |
| PATCH /api/conversations/{id}/settings | settings_revision plus changed setup fields | 200 new revisions; 409 revision_conflict otherwise |
| POST /api/conversations/{id}/turns | request_id, message | 200 committed turn and state; same ID/message replays; different message 409 request_conflict |
| GET /api/conversations/{id}/facts | none | 200 permitted canonical facts with provenance/revision and shared recipients |
| POST /api/conversations/{id}/facts | content, optional source_turn_id | 201 canonical fact, revision |
| PATCH /api/facts/{id} | revision, content | 200 corrected canonical fact; stale revision 409 |
| DELETE /api/facts/{id} | revision | 200 content-free deletion acknowledgement; repeats do not expose deleted text |
| PUT /api/facts/{id}/grants/{conversation_id} | revision | 200 explicit grant, idempotent |
| DELETE /api/facts/{id}/grants/{conversation_id} | revision | 200 revocation; source access cannot be revoked independently |
| POST /api/imports/preview | configured local import selection | 200 opaque preview token, counts/warnings; no full path echo |
| POST /api/imports/confirm | preview_token | 201 destination id after backup/transaction; 200 existing import on repeat |

404 unknown entity, 400 invalid input, 409 busy/revision_conflict/context_changed/request_conflict, 413 oversized input, 503 missing model/storage, 500 controlled persistence/corruption failure. Scope facts and source-turn references to accessible conversations. `/api/chat` without a conversation is deprecated: return an actionable `conversation_required` response once the new UI is enabled, never silently select a chat. This intentional contract transition is documented in setup/release notes.

Future background/image work consumes context snapshots through the same service and must revalidate revisions. Do not keep a write transaction open while running inference.

## Implemented refinements

`GET /api/bootstrap` returns a CSRF token and whether an import source is configured; its signed local session cookie contains no private content. `/api/status` reports model/configuration/database readiness without per-chat state; fetch the selected conversation for gauges/emotion. Legacy `/api/chat` returns `conversation_required` (400); only the explicit M1 compatibility factory retains the old contract.

Turn lists return newest 50 exchanges in chronological order by default; positive integer `cursor` requests older sequence values, with `limit` 1–100. `next_cursor` is null when exhausted. Memory creation returns canonical provenance/revision and sharing recipients. A deletion repeat returns content-free acknowledgement even if already deleted. Grant repeats do not change recipient context again.

Import preview body is `{selection:"configured", setup:{title,personality,relationship,boundaries}}`. No arbitrary browser-supplied source path is accepted. Tokens expire after ten minutes, at most 20 live previews, and input size is at most 16 MiB. Confirmation rechecks checksum/validity and returns 409 import_changed if the source changed. Original unknown fields are preserved in the exact local copy, not interpreted as verified facts.

Local mutations additionally return 403 forbidden on wrong/missing Origin or CSRF token. Irreducible context returns 413 context_too_large; malformed/unavailable legacy sources return 400 import_unavailable. All errors remain safe categories/messages with no raw exception/path/content.
