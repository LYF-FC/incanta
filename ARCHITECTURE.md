# Architecture

## Active companion implementation (002)

```mermaid
flowchart LR
    Browser[HTML and plain JavaScript] --> Flask[Local Flask app factory]
    Flask --> Service[Conversation service and generation lock]
    Service --> Store[SQLite conversations and turns]
    Service --> Facts[Canonical facts and explicit grants]
    Service --> Adapter[Lazy local inference adapter]
    Adapter --> Model[Configured GGUF]
    Flask --> Import[Explicit legacy preview and import]
    Import --> Copy[Private exact original copy]
    Import --> Store
```

`frontend_app.create_app()` constructs injectable services without reading private assets or opening/creating the database. Status checks do not load the model. Empty conversation listing does not create a database. `ConversationStore` opens one connection per operation, enables foreign keys and full synchronous writes, and validates schema version; it never resets an existing unreadable database. Schema creation occurs on explicit first write. One app process is supported.

`ConversationService.process` validates message/request/conversation IDs, takes one nonblocking generation lock, snapshots settings/context revisions and scoped facts/dialogue, then closes the read transaction before inference. Structured messages contain the selected personality, relationship and content boundaries. A conservative UTF-8 byte budget reserves output/format overhead, selects fitting current facts and trims oldest turns. Oversized irreducible setup/message returns a controlled error.

After generation, a write transaction rechecks revisions and atomically commits one turn plus gauges/emotion. Same request UUID/message replays the committed response without generation; another message with that identifier conflicts. Fact/settings edits can proceed during inference and invalidate its pending commit. Stale output is never saved as a current successful turn.

`FactStore` owns canonical facts and explicit grants. Only the selected conversation's granted current facts enter retrieval; no cross-chat transcript/personality/relationship sharing occurs. Corrections update one record. Deletion removes content and grants, leaving only a content-free tombstone; recipients' context revisions change transactionally. Historical turns and older backups are not rewritten. There is no automatic generated-fact extraction or sibling heuristic in this active path.

`LegacyImporter` reads one configured source only after preview. Confirmation revalidates its checksum, atomically preserves exact bytes (including unknown fields), and imports a conversation/turns/checksum record transactionally. Original duplicates are retained. Repeated confirmation cannot duplicate a committed import. Preview tokens are local, bounded and expire; corrupt/changed sources and backup failures preserve originals.

## Browser and HTTP boundaries

The plain-JavaScript UI provides a short setup form, conversation switch/resume, literal text transcript, memory inspect/correct/delete/sharing controls and explicit import confirmation. Browser storage contains only the last selected opaque conversation ID. Transport helpers retain request IDs for explicit retry and reject obsolete view responses after chat switches.

Mutations require an exact local Origin, signed local session and CSRF token from `/api/bootstrap`; there is no new multi-user identity service or CORS expansion. Cookies contain no private dialogue/settings. Session tokens rotate on process restart; reload bootstraps again. API/error responses are no-store with safe error categories. The status endpoint does not promise model generation success merely because assets are available.

## Compatibility and deferred work

`create_app(legacy=True)` is an explicit M1 test/smoke compatibility harness. Its old JSON engine/contract is not the default running app; default `/api/chat` requires conversation selection. M1 tests select this harness, while new 002 suites test the active factory. `core/state.py` remains inactive. The gauge rules retain documented existing precedence with Neutral fallback.

Images remain metadata-only in `backend/image_gen.py`. ComfyUI, model-resource arbitration, proactive follow-ups and native Mac notifications are planned in 003/004. Full consistent backup/restore tooling is 005. Atomic SQLite transactions and preserved import copies do not replace application backups or certify power-loss behavior. Native crashes, model obedience/quality and multi-process coordination need separate evidence/design.

See [002 contract](specs/002-companion-conversations/contracts/http.md), [verification](specs/002-companion-conversations/verification.md) and [decisions](DECISIONS.md). Butler reuse remains a separate review.
