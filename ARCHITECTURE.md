# Architecture

## Role
Incanta is an experimental local-AI project and reference implementation.

## Known components
- FastAPI backend
- React frontend
- local inference via llama.cpp or equivalent
- experimental ComfyUI integration
- workstation-focused deployment

## Boundary
Incanta is not the production Butler architecture.

## Reuse strategy
Components may be extracted only after:
- dependency audit
- security review
- persistence review
- alignment with Butler auth/audit/permissions

## Data
No production family data should become dependent on Incanta.
