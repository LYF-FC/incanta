#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
exec "${INCANTA_PYTHON:-python3}" frontend_app.py
