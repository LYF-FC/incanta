# Proposed data model and invariants

## Runtime settings

Immutable validated settings hold model/personality paths, writable data directory, loopback host/port and generation parameters. These are local environment values. Configuration errors expose a stable category and generic recovery message, not the supplied path or file contents.

## Conversation state

One owner per app instance: recent committed dialogue, seven named gauges and current emotion. Initial gauges are zero, initial emotion Neutral. All values are bounded to 0–100. Tentative next state is separate until persistence succeeds. A processing lock is operational state and is never persisted as memory.

## Memory document

Retain the existing document shape: `timeline` list; `milestones`, `emotions`, `beliefs`, `desires` and `adaptive_style` mappings; `reflections` list. Existing timeline records contain `timestamp`, `user`, and `celeste`. Preserve unknown top-level fields and historical event contents. No automatic deduplication, conversion, truncation or replacement of unreadable history.

A new successful turn adds one timestamped record. Existing JSON is read, copied and appended; write to a unique temporary file in the destination directory, flush/close, atomically replace the destination, then publish tentative in-memory state. Clean up an unsuccessful temporary write without deleting the existing history. Permission, malformed-file and I/O errors fail the turn and preserve prior data.

## Readiness

Track configuration availability separately from actual model initialization. `model_state` is `unloaded`, `loaded`, or `unavailable`; `ready` describes whether the configured dependencies are available for an attempted turn, not a guarantee of future inference success. The status route never loads the model. Generated text is not included in error responses.

## Limitations

This is a local single-process baseline. File replacement alone is not multi-process transaction coordination or a full backup. Recent history/gauges are not promised to survive a restart in this milestone; timeline history must reload intact. Multi-session state restoration and retention belong to M2/M3.
