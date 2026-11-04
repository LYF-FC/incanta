# Architecture

Incanta is an experimental local-AI prototype and reference implementation, not the production Butler architecture.

## Recovered source

The browser uses plain JavaScript and calls the Flask routes in `frontend_app.py`. Chat orchestration delegates to a local `llama-cpp-python` model, JSON memory storage and heuristic gauges. Personality files are loaded from disk but their values are not yet used by the prompt. Image generation currently writes metadata only.

FastAPI, React and live ComfyUI integration appeared in earlier plans; they are not implemented in the recovered snapshot. See [README.md](README.md) for known behavior gaps.

## Data boundaries

Models, private personality definitions, memories, conversations and generated assets remain local and outside Git. No production family data should become dependent on Incanta.

## Reuse

Before extracting components for Butler, audit dependencies, security and persistence, and align with Butler authentication, audit and permission requirements.
