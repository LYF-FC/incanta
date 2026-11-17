# Local MVP release validation

Planned commands become runnable during implementation. Prerequisite: 001–004 completed and their native/owner gates accepted, not just their planning checklists.

1. In a clean Python environment install lightweight tests, run `python3 -m unittest discover -s tests -v` and all `node --test tests/*.test.js`. No native inference/models in CI.
2. Use temporary synthetic DB/assets with two chats, shared corrected/deleted facts, approved portrait/three scenes and unread inbox. Back up and verify-only restore, then restore into an empty second root and restart. Verify all references/state and no automatic historical job/notification replay.
3. Inject corrupt manifest/hash, traversal/symlink, missing asset, unsupported schema, disk failure and nonempty destination; source/current state remain unchanged. Rehearse disconnected model/output storage and safe readiness.
4. Follow reviewed clean native setup on the M2/16 GB using already-owned assets. Record actual native build/model/workflow/helper versions and explicit installation steps; do not overwrite the historical dependency snapshot.
5. Owner combined journey: short setup, 30-minute English dialogue, memory inspection/correction/deletion/shared-fact checks, process restart and continuity, portrait plus three different reference-matching scenes, rendering-unavailable recovery, opted-in browser-closed notification and denied-permission inbox. Record pass/fail per item locally and only non-sensitive results in verification.md.
6. Review requirements/plan/tasks, staged privacy/content, required checks and PRs. Tag only when every mandatory gate passes and owner verdict is recorded. No deadline or future-machine certification is implied.
