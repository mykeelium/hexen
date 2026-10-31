#!/usr/bin/env bash
set -Eeuo pipefail
exec python3 "$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")/generate.py" "$@"
