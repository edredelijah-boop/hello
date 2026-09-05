#!/usr/bin/env bash
# Deterministic, no ffmpeg, no models, no network.
#
# Builds a data_root by hand (class files + META via the real provisioning code,
# plus one fabricated artifact of each kind), then checks that:
#   * the structural validator passes on a conforming tree, and
#   * it fails on a tampered .npy.
#
# Ends with OFFLINE_SMOKE_PASS.
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d "${TMPDIR:-/tmp}/avra-offline.XXXXXX")"
trap 'rm -rf "$work"' EXIT
export PYTHONPATH="$repo_root/src${PYTHONPATH:+:$PYTHONPATH}"

python3 - "$work/data_root" <<'PY'
import json, sys
import numpy as np
from avra_metadata_extractor import provision, layout, validate

dr, vid = sys.argv[1], "Synthetic_Red"
provision.write_class_files(dr)
provision.write_meta(dr)
layout.video_dir(dr, vid).mkdir(parents=True, exist_ok=True)

np.save(layout.npy_path(dr, vid), np.zeros((447, 100), dtype=np.float16))
json.dump(
    {"video_id": vid, "fps": 2.0, "duration_s": 4.0, "frame_count": 8,
     "total_detections": 1,
     "detections": [{"frame": 1, "time_s": 0.5, "timestamp": "00:00:00.50",
                     "class": "person", "conf": 0.4, "bbox": [1.0, 2.0, 3.0, 4.0]}]},
    open(layout.detections_path(dr, vid), "w"))
json.dump(
    {"video_id": vid, "fps": 2.0, "frame_count": 8, "duration": 4.0,
     "ocr_version": "PP-OCRv6", "ocr_lang": "en", "min_text_length": 3,
     "min_score": 0.5, "stats": {"elapsed_s": 1.0, "dropped_short": 0, "dropped_score": 0},
     "created_at": "2026-01-01T00:00:00+00:00",
     "detections": [{"t": 1.5, "text": "HELLO", "text_norm": "hello", "score": 0.99}]},
    open(layout.ocr_path(dr, vid), "w"))

assert validate.validate(dr) == [], "conforming tree should validate clean"

np.save(layout.npy_path(dr, vid), np.zeros((10, 5), dtype=np.float32))  # tamper
errs = validate.validate(dr)
assert any("447" in e for e in errs), f"tampered .npy should be caught, got {errs}"
print("fixture + validator checks OK")
PY

printf 'OFFLINE_SMOKE_PASS work=%s\n' "$work"
