# Implementation Plan: Local proactive follow-ups

**Branch**: `codex/004-proactive-followups` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

**Status:** planned only. Depends on 002 store/context and 003 resource lease; independent fake adapters allow tests before native visuals.

## Summary

Add one in-process durable scheduler using 002 SQLite and 003's resource manager, plus an inbox and a small explicitly installed macOS notification helper. Notifications show fixed generic text; private follow-up content remains in the local app. Browser absence is supported while the server/helper run; sleep/stopped app is not an always-on service.

## Technical Context

**Language/Version:** Python 3.11/3.13, plain JS; Swift helper built with the target Mac's supported command-line tools.

**Primary Dependencies:** existing Flask/sqlite3/threading; Apple UserNotifications via a bundled local app helper; no cloud notification service.

**Storage:** 002 DB, new policy/due/inbox/attempt tables with unique due keys; settings local.

**Testing:** unittest fake clock/notifier/resource adapter, Node inbox tests, process restart tests and explicit Mac permission/delivery check.

**Target Platform:** local macOS; non-Mac tests use fake notifier.

**Project Type:** existing web app with optional native notification helper.

**Performance Goals:** fake scheduling decisions under two seconds; native generation and OS delivery measured, no hard delivery SLA.

**Constraints:** one scheduler; default opt-out; no content in notification/logs; no generation during quiet hours or active user input; no automatic permission prompt/install.

**Scale/Scope:** multiple isolated conversations for one owner; at most one proactive generation at a time, behind chat/manual images.

## Constitution Check

All inference/state local; explicit notification opt-in and install; synthetic deterministic tests; planned-only claims; durable revision checks and safe restart. No exceptions. Shared scheduler data is runtime-only. Verify native helper permissions/build on Mac before release.

## Project Structure

Add `backend/proactive/policy.py`, `backend/proactive/scheduler.py`, `backend/proactive/notifier.py`, `backend/proactive/inbox.py`, `backend/migrations/003_proactive.sql`, `frontend/followups.js`, `native/notifications/IncantaNotifications.swift`, `native/notifications/Info.plist`, `scripts/build-notifications.sh`, `tests/test_proactive.py`, `tests/test_notifications.py`, `tests/followups.test.js`; modify app lifecycle/routes and config. Build products ignored under build; no installed login item.

## Design and execution

See [research](research.md), [data model](data-model.md), [contract](contracts/http.md), [validation](quickstart.md). Defaults: minimum idle 15 minutes, cooldown 60 minutes per conversation, cap two generated follow-ups/day/chat and four/day globally, quiet hours 22:00–08:00 in explicitly configured local timezone (initially Europe/Paris). Editable limits: idle 5–240 minutes, cooldown 15–1440 minutes, daily chat cap 0–10, global cap 0–20. Zero cap disables new follow-ups. These are engineering defaults; show them before opt-in. Notification attempts have a global 15-minute minimum interval; unnotified entries stay in inbox. Catch-up never bypasses quiet hours/caps.

Use UTC durable due times, timezone-aware quiet-hour rules and injected monotonic/wall clocks. Browser activity heartbeat every 30 seconds while visible/focused, stale after 90 seconds; a user turn always updates activity. Closing the browser permits due work only after the idle threshold. Use a unique conversation/due-slot key, short transaction claim and process-singleton ownership. Recover abandoned claims without replaying already committed items. Startup reconciles overdue schedules to one candidate per chat, then normal rate limits apply.

Generate against a captured context revision outside transactions and through the resource arbiter; before committing recheck policy/activity/limits/revisions. Store follow-up as an unread inbox message, not a fake user turn or verified memory fact; a later owner reply explicitly includes it in that conversation context. Reserve rate-limit budget transactionally. Retry generation at most once after 15 minutes if still eligible; no immediate loop. Native notification failure never regenerates text.

Build a stable-identity Swift application bundle using UserNotifications; explicit install/build script and permission action, no private message content in subprocess arguments. Invoke executable by argument array with opaque ID and fixed text, capture safe result codes/timeouts. Use native delegate handling for permission/delivery and inbox deep link scoped to loopback/opaque IDs. Denied/undetermined permission means inbox-only until explicit action. Mark attempt before dispatch; crash ambiguity does not trigger automatic re-alert. No claim of exactly-once OS display. Native platform support is a gated implementation task; browser Notifications alone do not satisfy browser-closed acceptance.

## Complexity Tracking

A small native helper is justified by server-running/browser-closed Mac notifications. It does not replace the Flask UI or install a permanent service. A database-backed scheduler avoids adding a queue server or cloud automation dependency.
