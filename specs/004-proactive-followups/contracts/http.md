# Follow-up and notification contract

Planned. Inherit 002 UUID/CSRF/same-origin/size/error conventions and 003 resource priority. Scheduler is internal, not an external trigger endpoint.

| Method/path | Request | Result |
| --- | --- | --- |
| GET /api/conversations/{id}/followup-policy | none | effective policy/revision and timezone |
| PATCH /api/conversations/{id}/followup-policy | expected revision, bounded policy fields | new revision, next eligibility; no permission prompt as side effect |
| POST /api/conversations/{id}/activity | visible/focused state | server-side timestamp, no user-supplied time authority |
| GET /api/followups | optional conversation, unread, cursor, limit <=100 | scoped inbox with generated_at/read state and safe provenance |
| POST /api/followups/{id}/read | none | idempotent read acknowledgement |
| GET /api/notifications/status | none | unavailable/undetermined/denied/authorized and helper compatibility |
| POST /api/notifications/authorize | explicit user action | local helper authorization outcome; never auto-request at startup |

Native notifier interface: status()->safe permission code; request_authorization()->safe code; deliver(opaque followup UUID)->accepted/denied/failed/uncertain. Fixed title/text only (for example, 'Incanta' and 'A follow-up is waiting in Incanta'). Opening an inbox deep link validates record ownership and loopback destination; never evaluate model-supplied URLs or commands. Invocation uses an argument list, fixed executable and timeout, no shell interpolation.

Scheduler interface: tick(clock), eligibility(conversation), claim(due), generate(snapshot), commit_if_current(), notify_saved(). Persist before notify, no generation in HTTP heartbeat handlers, one worker/process owner. Termination stops new claims and leaves unfinished claims recoverable. Browser-closed native behavior is acceptance-tested; browser-only fallback may show the inbox but does not pass native delivery.
