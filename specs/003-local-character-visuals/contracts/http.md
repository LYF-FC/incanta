# Visual API and renderer adapter contract

Planned. Inherit 002 UUID validation, 64 KiB cap, same-origin/CSRF mutation protection, revision checks and safe errors. Scene/model/reference content stays local.

| Method/path | Request | Success |
| --- | --- | --- |
| GET /api/visuals/status | none | configured/available/compatible with safe blocker codes; no model initialization |
| PUT /api/conversations/{id}/visuals | revision and opaque local configuration selection | identity revision and compatibility state |
| POST /api/conversations/{id}/images | request_id, kind portrait/manual, description | 202 job id/state; idempotent same request |
| GET /api/conversations/{id}/images | cursor, limit <=100 | owned jobs/assets and approved portrait |
| PATCH /api/conversations/{id}/scene-policy | revision, enabled, cooldown_seconds | effective policy; disabling drops queued automatic work |
| GET /api/image-jobs/{id} | none | state, progress if known, error code and owned asset ID |
| POST /api/image-jobs/{id}/cancel | none | 202 cancel_requested or 200 already terminal; unsupported interruption is explicit |
| POST /api/conversations/{id}/portrait | asset_id | 200 owner-approved portrait; reject asset from another conversation |
| GET /api/assets/{id} | none | validated owned image, no directory listing; private cache policy |

Automatic scene proposals are internal service calls using committed originating turns; arbitrary client input cannot request another chat's job. Reject unknown/wrongly scoped IDs, invalid identity/config revisions, queue overflow, unexpected remote host, unsafe media and oversized output with controlled errors.

`RendererAdapter`: inspect_capabilities, validate_workflow, submit(request)->owned handle or uncertain, poll(handle)->state/output descriptors, cancel_owned(handle), release_owned_resources. Fake adapter required. Submit timeout is not permission to resubmit. Workflows require resolved node inputs; sanitize node IDs/classes/bindings, reference paths and output descriptors. Allowed endpoints are fixed operations on an explicitly configured loopback ComfyUI service, never URLs supplied by model/user text. Capability detection and server pinning select cancellation implementation; global interrupt/queue-clear is forbidden for unrelated work.

`ResourceManager`: acquire(kind, owner), release, unload_llm, release_renderer_resources; one heavy lease. UI remains responsive while chat or render may wait. Native memory-handoff proof is a separate gate, not a guarantee from method names.
