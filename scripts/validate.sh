#!/usr/bin/env bash
# Structural check of a generated data_root (no models). See docs/OUTPUT_FORMAT.md
source "$(dirname -- "${BASH_SOURCE[0]}")/_common.sh"
data_root="${1:-data_root}"
if command -v avra-extract >/dev/null 2>&1; then
  exec python3 -m avra_metadata_extractor.validate "$data_root"
fi
exec env PYTHONPATH="$repo_root/src${PYTHONPATH:+:$PYTHONPATH}" python3 -m avra_metadata_extractor.validate "$data_root"
