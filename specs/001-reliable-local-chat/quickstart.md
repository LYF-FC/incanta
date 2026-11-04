# Planned validation quickstart

These instructions describe checks to add while implementing 001. The referenced application tests do not exist yet. For currently available tooling, use [the development guide](../../docs/DEVELOPMENT.md).

## Model-free acceptance

1. Create the reviewed test environment from the future `requirements-test.txt`; do not install/download a real model.
2. Run the proposed Flask contract, chat/state, gauge and temporary-memory tests plus frontend helper tests listed in `tasks.md`.
3. Launch the app with fake inference and synthetic configuration; verify useful initial state, literal markup text, one stored event and error retry behavior.
4. Simulate missing SSD, malformed JSON, concurrent requests, inference failure and atomic-write failure. Preserve existing history in every failure case.

## Manual local-model exit gate

After automated acceptance passes, explicitly configure an already-owned local model and synthetic personality. Use the implemented settings documented by T019, not speculative environment instructions from this plan.

- Open the interface and confirm no initialization/generation occurs on status polling.
- Send one synthetic message. Confirm a response and exactly one additional timeline entry.
- Restart and confirm the history remains readable. Confirm errors contain no private path/content.
- Record date, OS/hardware, runtime version, model identity/revision/checksum and pass/fail in a non-sensitive verification note. Do not attach conversation data or model weights.

M1 is not complete until both automated and manual gates pass. A disconnected model or lack of native runtime can leave the manual gate pending; report it plainly rather than marking the milestone complete.
