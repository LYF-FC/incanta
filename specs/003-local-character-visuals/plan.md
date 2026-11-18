# Implementation Plan: Local Celeste portraits and scenes

**Branch**: `codex/003-local-character-visuals` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)

**Status:** Implemented on the feature branch. See [verification.md](verification.md) for evidence and outstanding gates.

## Summary

Keep Flask/plain JavaScript. Add a local rendering adapter, durable SQLite job records using 002's store, local asset serving and a shared resource arbiter. Integrate ComfyUI-Photoshoot through a resolved API workflow, not its browser series button. Export/validate hidden node inputs and pin tested node/server versions. Implement fake-backed acceptance first.

## Technical Context

**Language/Version:** Python 3.11/3.13; plain JS.

**Primary Dependencies:** existing Flask/SQLite; Pillow for image decoding; stdlib HTTP client adapter; separately installed/pinned ComfyUI and Photoshoot (not dependencies of web/test requirements).

**Storage:** 002 DB plus configured ignored output/reference/workflow directories; metadata stores opaque asset IDs and checksums, never public paths.

**Testing:** unittest with fake renderer/clock/resource manager, temporary files and DB; Node UI tests; explicit native rendering check.

**Target Platform:** M2/16 GB macOS; model-free CI.

**Project Type:** existing local web app plus optional rendering service.

**Performance Goals:** nonblocking HTTP submission/status and usable UI; fake job submission under two seconds excluding process startup. Actual render/model switching measured.

**Constraints:** loopback renderer URL only; one heavy-operation lease; no global interrupt on shared renderer; no automatic retry after uncertain submit; no private media in Git.

**Scale/Scope:** one owner, one running image, up to five pending manual requests globally and one pending automatic request per conversation; total pending limit ten. Extra requests return busy.

## Constitution Check

Local execution and private assets preserved; all external dependency setup is explicit; synthetic reproducible tests required; state/schema changes use migration/backup; claims follow recorded verification. No exception. Recheck measured M2 fit/face match and dependency licenses before release.

## Project Structure

Add `backend/rendering/comfyui_adapter.py`, `backend/rendering/workflow.py`, `backend/rendering/jobs.py`, `backend/resource_manager.py`, `backend/migrations/002_visuals.sql`, `frontend/visuals.js`, `tests/test_rendering.py`, `tests/test_render_jobs.py`, `tests/test_resources.py`, `tests/visuals.test.js`, `examples/render-workflow.example.json` (synthetic only, already covered by exact examples policy); modify app/config/conversation UI and native adapter unload support. No model-backed CI.

## Design and execution

See [research](research.md), [data model](data-model.md), [contract](contracts/http.md) and [validation](quickstart.md). Implement job transitions before binding UI. Keep prompts, references, outputs and resolved private workflow local. Validate workflow node classes via `/object_info`, required bindings/types and provenance; convert Photoshoot `node.properties` to hidden API inputs through the upstream browser export/hook, then test the exported prompt headlessly. Do not assume UI series orchestration executes over API.

Use `POST /prompt`, retain owned prompt ID, poll `/history/{prompt_id}` and fetch validated image output through `/view`. Correlate app request ID via workflow metadata/extra data when supported. Crash/timeout before an owned ID is saved becomes uncertain; reconcile by owned metadata/history and require owner resolution if not provable. No blind resubmit. Preserve app job history even if ComfyUI clears history. Use only capability-tested owned cancellation; unsupported running cancellation waits for completion and discards publication. Limit network responses/timeouts and validate returned image type/size before atomic output save.

Use one resource arbiter for user chat, manual images, proactive generation and automatic scenes. Foreground chat has priority at the next idle boundary, then manual image, then proactive/automatic work. No silent preemption. Before images, explicitly unload the LLM; before chat, request owned ComfyUI resource release and confirm supported handoff. Do not use a renderer sharing unknown other jobs for heavy release/cancellation; require a dedicated Incanta instance if ownership cannot be guaranteed. A resource handoff failure leaves work queued/failed safely, not concurrently loaded. `/free` alone is not proof memory was returned; native acceptance must verify measured behavior.

Automatic trigger is a bounded structured scene proposal attached to a committed dialogue turn. Malformed/no-change proposals are ignored; they are not memory facts. Default cooldown 300 seconds, selectable 60–3600 seconds; coalesce to latest proposal per chat. These are documented engineering defaults, not additional owner requirements. Snapshot and revalidate settings/context revisions before render and before publication.

## Complexity Tracking

A worker queue/resource lease is needed for multi-minute jobs and 16 GB memory constraints. No distributed queue, framework rewrite or permanent scheduler service is introduced. Server-side idempotency is not assumed across ambiguous external submissions.
