# Validation quickstart

Implemented validation guide; actual results and remaining owner acceptance are in [verification.md](verification.md). M1 verification passed and PR #7 is open; the owner authorized stacked implementation before merge. Prerequisites: Python 3.11/3.13 lightweight dependencies and Node. No native packages/models for automated tests.

1. Run `python3 -m unittest discover -s tests -v` and `node --test tests/conversations.test.js` with the existing tests. Run `node --test tests/*.test.js` for all frontend regressions.
2. Use a temporary database/fake adapter, create A and B with different settings, send ten turns, restart the process twice. Expect exact transcript/state restoration, settings in each captured prompt and no leakage.
3. Save two sourced facts in A; grant only one to B. Inspect B context, correct, revoke, regrant and delete. Expect each change on the next read, including after restart. Inject an edit during generation: obsolete output must not commit.
4. Import synthetic legacy data with duplicate events/unknown fields. Inject failure and repeat confirmation; original bytes remain identical, one successful import only.
5. Test read-only/corrupt storage, invalid field bounds/UUIDs, wrong-origin and missing CSRF mutation, repeated request IDs and overlapping requests.
6. In the browser, verify short setup, chat selection/restoration and memory controls, including the explanation that deleting a memory does not erase source transcripts/backups.
7. Explicit native owner review: configure an already-owned model locally, complete a 30-minute English conversation, restart and assess continuity/personality/boundaries and memory provenance. Record pass/fail and non-sensitive environment/timing only in verification.md; no private transcript.

The repeatable short native check is `python scripts/verify_companion_model.py`, with INCANTA_MODEL_PATH set locally to an already-owned model. It uses synthetic temporary SQLite/settings and a separate-process reload; it does not read private character/history or satisfy the owner-reviewed 30-minute acceptance by itself. Never invoke it from automated test discovery or CI.
