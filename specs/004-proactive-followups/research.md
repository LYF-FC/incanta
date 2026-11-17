# Research and decisions

**Date:** 2026-11-17. Primary-source review/research-agent design recommendations; no native helper installed or notifications sent.

- **Decision:** Apple UserNotifications helper with stable bundle identity and explicit authorization. **Rationale:** notifications must work when the app server runs without an open browser. **Alternative:** browser-only notifications do not establish server-only delivery. Packaging/permission/delivery need actual Mac verification. [Apple authorization](https://developer.apple.com/documentation/usernotifications/asking-permission-to-use-notifications), [notification requests](https://developer.apple.com/documentation/usernotifications/unnotificationrequest).
- **Decision:** fixed generic preview and private in-app inbox. **Rationale:** lock-screen previews should not disclose private conversations. No generated content in native arguments/logs; opaque IDs only.
- **Decision:** durable due keys, atomic claims, separate notification attempt state and coalesced catch-up. **Rationale:** restart-safe inbox creation with bounded notification ambiguity. **Alternative:** transient timers and replaying every missed interval duplicate/burst after sleep. This is project design reasoning, not an OS delivery guarantee.
- **Decision:** opt-in per chat, idle detection, quiet hours/caps, revision checks and foreground priority through 003 lease. **Rationale:** owner wants initiative with control and local memory safety. **Alternative:** unrestricted background generation competes for 16 GB and may use obsolete shared facts.
- **Decision:** app awake/running boundary, no launch agent/cloud push. **Rationale:** matches agreed local POC. Future always-on Butler-associated machines require their own deployment assessment.

No unresolved design question blocks tasks. Native bundle authorization behavior on the target OS remains an explicit acceptance experiment, not an assumed capability.
