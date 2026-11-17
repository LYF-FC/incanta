# Research and decisions: reliable local chat

Research basis: direct static inspection of the recovered source on 2026-11-04. These are design decisions, not results from a runtime experiment.

| Question | Decision and evidence | Alternative deferred |
| --- | --- | --- |
| Rewrite the stack? | Keep Flask/plain JS; the current routes/UI are small and defects are identifiable | React/FastAPI rewrite adds scope before establishing a baseline |
| Make imports testable? | App factory and injected lazy inference; current `Llama(...)` is module-level | Import patching around a real model is fragile and hides lifecycle defects |
| How to store one turn? | One writer, preserve existing JSON fields, atomic same-directory replace | New database/schema migration risks private histories and is unnecessary for one owner |
| What is a committed turn? | Persist the event before publishing new in-memory state; failure returns an error | Mutating global state first leaves invisible partial turns after disk failure |
| Concurrent input? | One nonblocking process lock, explicit busy response and frontend submit lock | Queues, automatic retries or multiple workers require separate semantics |
| Which emotion order? | Existing gauge order with Neutral last; controlled variation in tests | `core/state.py` has different thresholds/order; merging the two changes character semantics |
| External SSD? | Explicit paths, root-anchored defaults and useful availability errors | Copying weights into every checkout wastes storage; automatic downloads violate local-control expectations |
| Which dependencies? | Retain recovery freeze; introduce reviewed lightweight test requirements as an implementation task | Installing the entire old ML stack in CI is unnecessary for fake inference |
| What about factual milestones/personality? | Track in M2/M3; this feature preserves legacy data and fixes mechanical reliability | Silent memory inference or persona redesign should not be smuggled into baseline repair |

No hardware benchmarks, model selection, dependency vulnerability audit or private-history migration tests were conducted. The original open evidence is now tracked in [verification.md](verification.md): automated failure injection, synthetic browser and explicit native-model/process-restart checks passed on 2026-11-17; reviewed delivery remains pending.
