#!/usr/bin/env bash
# GitHub Spec Kit v1.3.0; use a fixed upstream commit for reproducibility.
set -euo pipefail
if ! command -v uvx >/dev/null 2>&1; then
    echo "Install uv first: https://docs.astral.sh/uv/getting-started/installation/" >&2
    exit 1
fi
exec uvx --from 'git+https://github.com/github/spec-kit.git@34a0d388eac671d656eb05b125ad3ed6056168ed' specify "$@"
