# Local HTTP contract

This is the implemented contract for specification 001, verified with synthetic tests; see [verification](../verification.md). Responses are JSON; asset routes continue serving the local interface. No CORS expansion, external API or authentication service is introduced.

## GET /api/status

Returns 200 without loading the model or requiring private files.

```json
{
  "status": "ok",
  "ready": false,
  "model_state": "unavailable",
  "emotion": "Neutral",
  "gauges": {"Trust": 0, "Intimacy": 0, "Curiosity": 0, "Affection": 0, "Confidence": 0, "Confusion": 0, "Arousal": 0},
  "issues": ["model_unavailable", "personality_unavailable"]
}
```

`issues` contains only applicable stable codes: `invalid_configuration`, `model_unavailable`, `personality_unavailable`, `storage_unavailable` or `history_unreadable`. An empty list means no known configuration blockers. `ready` is true when configured dependencies are accessible; it does not initialize inference or guarantee a generation succeeds. A present, not-yet-loaded model is `unloaded`; a successfully initialized one is `loaded`. Empty/missing assets or a known failed load are `unavailable`.

## POST /api/chat

Request content type must be `application/json`. Body must be an object with `message` as nonempty string, trimmed, maximum 8,000 characters; other fields are ignored for compatibility. Transport request size is capped at 64 KiB before JSON parsing. This accommodates 8,000 multibyte characters while bounding resource use.

Successful response, 200:

```json
{
  "response": "Synthetic example response.",
  "emotion": "Curious",
  "gauges": {"Trust": 0, "Intimacy": 0, "Curiosity": 60, "Affection": 0, "Confidence": 0, "Confusion": 0, "Arousal": 0}
}
```

Success means exactly one event has been durably appended before this response and committed state matches the response. The server never automatically retries generation or writes an event for a rejected/failed request.

## Errors

Every failure returns an object shaped as follows:

```json
{"error": {"code": "model_unavailable", "message": "Connect or configure the local model, then try again."}}
```

| HTTP status | Code | Trigger |
| --- | --- | --- |
| 415 | `unsupported_media_type` | Request is not JSON |
| 400 | `invalid_request` | Malformed JSON, non-object body or missing/non-string/blank message |
| 413 | `input_too_large` | Message exceeds 8,000 characters or request exceeds 64 KiB |
| 409 | `conversation_busy` | Another turn holds the process lock |
| 503 | `invalid_configuration` | Configured settings cannot be used |
| 503 | `model_unavailable` | Missing/disconnected model or failed model initialization |
| 503 | `personality_unavailable` | Missing or invalid character file |
| 503 | `storage_unavailable` | Unreadable/unwritable storage location |
| 500 | `history_unreadable` | Existing history is malformed; file preserved |
| 500 | `persistence_failed` | Commit failed; old durable state retained |
| 500 | `generation_failed` | Adapter failed or returned unusable output |

No raw exceptions, full local paths, character contents, prompts or generated replies are included in errors/logs. Validation happens before inference/memory mutation. The UI checks HTTP status before applying returned state and re-enables input after failures. Display response/error text using text nodes, never raw HTML insertion.
