#!/usr/bin/env bash
# Clean-room end-to-end run on a synthetic 4 s video.
#
# Requires: ffmpeg/ffprobe, `pip install ".[all]"`, and a BEATs checkpoint in
# $AVRA_BEATS_CHECKPOINT. YOLOE weights auto-download; PaddleOCR models
# auto-download on first use.
#
# Ends with E2E_SMOKE_PASS.
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d "${TMPDIR:-/tmp}/avra-e2e.XXXXXX")"
trap 'rm -rf "$work"' EXIT

: "${AVRA_BEATS_CHECKPOINT:?set AVRA_BEATS_CHECKPOINT to a BEATs_strong_*.pt file}"

"$repo_root/tests/create-fixture.sh" "$work/fixture"

"$repo_root/scripts/extract-all.sh" "$work/fixture/videos/Synthetic_Red.mp4" \
  --data-root "$work/data_root" --frames-root "$work/frames"

"$repo_root/scripts/validate.sh" "$work/data_root"

python3 - "$work/data_root" <<'PY'
import sys
import numpy as np
from avra_metadata_extractor import layout
dr = sys.argv[1]
arr = np.load(layout.npy_path(dr, "Synthetic_Red"))
assert arr.shape[0] == 447 and arr.dtype == np.float16, (arr.shape, arr.dtype)
assert layout.detections_path(dr, "Synthetic_Red").exists()
assert layout.ocr_path(dr, "Synthetic_Red").exists()
print("artifact shapes OK:", arr.shape)
PY

printf 'E2E_SMOKE_PASS work=%s\n' "$work"
