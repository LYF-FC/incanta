# Feature 003 verification

## Implemented behavior

The existing Flask and plain JavaScript companion app adds a local visual profile per conversation, explicit portrait approval and rejection, private image serving, durable manual requests, and automatic scenes that default off. Queued work, ownership, cancellations and unresolved submissions are retained in SQLite. Chat and images share one heavy-work lease. No visual setting adds, copies or shares a memory fact.

## Automated checks

Synthetic-only Python coverage includes the v1-to-v2 migration, profile/workflow validation with Photoshoot hidden input schemas, owned cancellation, renderer timeout/bounds, image decoding limits and traversal, portrait ownership, restart and duplicates, disk and handoff failures, stale facts, automatic cooldown/coalescing, toggle-off and foreground/manual priority. Node covers image actions, idempotent retries and late responses after changing conversation. 68 Python tests passed on both 3.11 and 3.13, and all 15 Node tests passed. Modified JavaScript and tracked Bash scripts passed syntax checks. The staged repository checker and cached diff check passed. A synthetic browser session saved a profile, showed a running state, displayed the resulting portrait, required explicit approval, and hid the approved portrait on switching to another conversation.

## Local compatibility

- The owner-approved ComfyUI installation reports version 0.3.59. Source checkout `707b2638ecd82360c0a67e1d86cc4fdeae218d03`. Photoshoot was newly evaluated from an isolated copy pinned at `84f168d65a432c96b491858af0bf7d90dde807d7`. The existing installation was preserved. No models were downloaded or trained.
- A model-free CPU run of the base renderer passed owned submission/history, queue state and the two worker barriers after `/free`. It did not measure native model memory release.
- A second model-free isolated run used actual Photoshoot Person, Wardrobe and Expression nodes, checked their hidden API inputs headlessly, then fetched and decoded a generated 16×16 synthetic PNG. The first assertion incorrectly placed the identity marker in Person's wardrobe-overridable details. Using Person's identity trigger preserved the marker alongside the linked wardrobe. The rerun passed with all three inputs and the handoff barriers. [Photoshoot source](https://github.com/ralksta/ComfyUI-Photoshoot/tree/84f168d65a432c96b491858af0bf7d90dde807d7) · [ComfyUI source](https://github.com/Comfy-Org/ComfyUI/tree/707b2638ecd82360c0a67e1d86cc4fdeae218d03)
- Photoshoot is MIT and ComfyUI is GPL-3.0. They remain separately operated dependencies. Incanta ships no upstream renderer or Photoshoot code, checkpoint, private profile or generated images. Model file checksums and reference provenance are recorded privately. [Photoshoot license](https://github.com/ralksta/ComfyUI-Photoshoot/blob/84f168d65a432c96b491858af0bf7d90dde807d7/LICENSE) · [ComfyUI license](https://github.com/Comfy-Org/ComfyUI/blob/707b2638ecd82360c0a67e1d86cc4fdeae218d03/LICENSE)

## Authorized M2 render run · 2026-11-18

On a MacBook Pro M2 with 16 GB RAM, ComfyUI used the native MPS device and the owner-authorized checkpoint and LoRA. An isolated Incanta app used the actual profile, worker, ComfyUI adapter and owned asset endpoint. Each render used one image at 512×640 and 24 steps. The private provenance record holds exact model/workflow/file checksums and all 11 reference hashes. Original files stayed in place.

| Candidate | Render seconds, including queue and save | Peak ComfyUI physical footprint (MiB) | Footprint immediately after confirmed release (MiB) |
| --- | ---: | ---: | ---: |
| Portrait | 81.9 | 6,034 | 3,319 |
| Scene 1 | 58.4 | 6,650 | 1,107 |
| Scene 2 | 56.4 | 6,652 | 1,113 |
| Scene 3 | 54.3 | 6,658 | 1,118 |

Footprint is macOS per-process physical footprint, sampled around once per second. Lifetime process peak was 6,658 MiB. No renderer process failed during the four requests. The real ComfyUI release barriers were followed by a simulated chat reply in 0.5–0.7 seconds. That verifies ordering and the measured reduction in renderer footprint. A combined run with actual GGUF inference and the owner's visual verdict are separate gates.

## Reference-assisted follow-up · 2026-11-18

After the owner rejected the first portrait for face match, a second isolated profile used the authorized checkpoint and LoRA with a locally framed reference and feathered latent mask. ComfyUI changes the surrounding scene while retaining the central face region. A private local manifest records the exact graph and source hashes.

| Candidate | Render seconds | Sampled peak ComfyUI footprint (MiB) | ComfyUI footprint after release and reply (MiB) | Release plus native reply seconds |
| --- | ---: | ---: | ---: | ---: |
| Revised portrait | 75.0 | 5,911 | 716 | 48.1 |
| Scene 1 | 57.4 | 6,585 | 723 | 26.9 |
| Scene 2 | 60.0 | 6,676 | 733 | 25.3 |
| Scene 3 | 61.9 | 6,556 | 795 | 32.0 |

Lifetime ComfyUI peak was 6,678 MiB. Incanta physical footprint was 173–184 MiB after closing the verified GGUF and 4,533–4,583 MiB after reloading it and generating a successful synthetic reply. The real GGUF → MPS render → GGUF order was checked on each request. Both processes completed all four transitions without a crash. The reply timing includes renderer release and CPU-backed chat generation.

## Owner gates

The owner authorized an existing local checkpoint and character LoRA and 11 local reference photos. The owner reviewed the first portrait and said the face needs work. The revised portrait and three reference-assisted scenes are ready for the owner's verdict. Feature 003 requires explicit approval of a matching portrait and three consistent, distinct scenes. The existing dialogue acceptance [issue #9](https://github.com/LYF-FC/incanta/issues/9) remains separate. Keep [issue #4](https://github.com/LYF-FC/incanta/issues/4) open while native or owner gates remain.

## Delivery

[PR #11](https://github.com/LYF-FC/incanta/pull/11) contains the reviewed implementation and regression tests. Implementation self-review identified and fixed a scheduling race when a manual request arrives while an automatic workflow is being validated. The staged follow-up contains source, tests and sanitized records only.
