# Follow-up validation quickstart

Planned. Requires 002 and 003 interfaces, fake implementations for automated checks. Install no native helper in CI.

1. Run `python3 -m unittest discover -s tests -v` and `node --test tests/followups.test.js` after adding the planned tests.
2. Fake clock: disabled/paused/active/quiet cases generate nothing. Enable idle chat and advance time; source-grounded follow-up saved once, then generic notifier called.
3. Repeat one due tick 100 times across process restart; one committed follow-up only. Advance 24 hours, cross daylight-saving/clock changes and wake/restart; at most one catch-up per chat and caps/notification spacing hold.
4. Inject stale settings/facts, owner activity during generation, duplicate claims, renderer resource occupancy, inference failure and denied/uncertain notification. No obsolete message or regeneration to retry notification.
5. Browser: policy values visible before opt-in, pause controls, scoped unread list/read state and return-to-chat. Closing browser is not treated as app termination.
6. Explicit Mac gate: build/install reviewed helper using `scripts/build-notifications.sh`, invoke authorization from owner action, close browser while server runs and generate one synthetic follow-up. Verify generic notification; then deny permission and verify inbox-only recovery. Record actual permission/OS/helper build and outcome in verification.md with no content/screenshots of private messages.
7. Stop app/sleep Mac; expect no generation while stopped/asleep. Restart/wake and verify bounded catch-up and actual generation timestamps. Do not install a login item or promise off-machine delivery.
