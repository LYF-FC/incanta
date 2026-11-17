# Visual validation quickstart

Planned tests become runnable during implementation. Requires 002 store/contracts and M1 runtime acceptance. Automated tests install no ComfyUI/model packages.

1. Run `python3 -m unittest discover -s tests -v` and `node --test tests/visuals.test.js` with fake renderer/clock/resource manager.
2. Queue portrait/manual/automatic jobs in temporary storage; verify scoped image display, explicit approval, cooldown, bounded queue, manual priority and next-idle chat priority.
3. Inject unavailable renderer, node mismatch, unsafe output, disk failure, memory handoff failure and stale revision; previous portrait/transcript remain intact.
4. Simulate timeout after submission, app restart, external-history removal and cancellation unsupported/targeted. No blind retry, duplicate successful asset or unrelated queue interruption.
5. Explicit local setup evaluation: inspect only authorized existing ComfyUI/reference/LoRA locations, back up configuration, pin compatible server/Photoshoot revisions, export resolved API prompt and verify hidden fields headlessly. Choose model/runtime only after M2 compatibility and license review; no automatic download or retraining.
6. Owner native gate: approve portrait and three different scenes against private reference faces. Record pass/fail, checksums, render durations, peak memory and LLM/render handoff behavior locally; commit only non-sensitive environment/results in verification.md. A failed face match blocks MVP acceptance even if rendering works.
