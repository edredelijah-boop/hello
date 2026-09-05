"""Deterministic structural check of a generated ``data_root``.

Verifies that the class files, ``META.md``, and every per-video artifact present
match the schemas in docs/OUTPUT_FORMAT.md. Does not run any model and does not
judge whether the detections are *correct* -- only that the files are well
formed and mutually consistent.

    python -m avra_metadata_extractor.validate DATA_ROOT

Exit status is 0 when everything checked is valid, 1 otherwise.
"""

import json
import sys
from pathlib import Path

from . import constants, layout

_DET_ROOT_KEYS = {"video_id", "fps", "duration_s", "frame_count",
                  "total_detections", "detections"}
_DET_REC_KEYS = {"frame", "time_s", "timestamp", "class", "conf", "bbox"}
_OCR_ROOT_KEYS = {"video_id", "fps", "frame_count", "duration", "ocr_version",
                  "ocr_lang", "min_text_length", "min_score", "stats", "detections"}
_OCR_REC_KEYS = {"t", "text", "text_norm", "score"}


def _check_class_file(path, expected_n, errors):
    if not path.exists():
        errors.append(f"missing: {path}")
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    if expected_n is not None and len(lines) != expected_n:
        errors.append(f"{path.name}: expected {expected_n} lines, got {len(lines)}")
    for i, line in enumerate(lines):
        parts = line.split("\t")
        if len(parts) != 2 or parts[0] != str(i) or not parts[1]:
            errors.append(f"{path.name}:{i + 1}: not '<index><TAB><name>'")
            break


def _check_npy(path, errors):
    try:
        import numpy as np
    except ModuleNotFoundError:
        return  # numpy-less environment: skip the shape check
    arr = np.load(path, mmap_mode="r")
    if arr.ndim != 2 or arr.shape[0] != constants.N_AUDIO_CLASSES:
        errors.append(f"{path.name}: expected ({constants.N_AUDIO_CLASSES}, T), got {arr.shape}")
    if arr.dtype != np.float16:
        errors.append(f"{path.name}: expected float16, got {arr.dtype}")


def _check_json(path, root_keys, rec_keys, errors, bbox=False):
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"{path.name}: invalid JSON ({e})")
        return
    missing = root_keys - obj.keys()
    if missing:
        errors.append(f"{path.name}: missing root keys {sorted(missing)}")
    for rec in obj.get("detections", [])[:5000]:
        if rec_keys - rec.keys():
            errors.append(f"{path.name}: a detection is missing {sorted(rec_keys - rec.keys())}")
            break
        if bbox and (not isinstance(rec.get("bbox"), list) or len(rec["bbox"]) != 4):
            errors.append(f"{path.name}: bbox is not [x1,y1,x2,y2]")
            break


def validate(data_root):
    data_root = Path(data_root)
    errors = []

    if not data_root.is_dir():
        return [f"data_root not found: {data_root}"]

    _check_class_file(layout.audio_classes_file(data_root),
                      constants.N_AUDIO_CLASSES, errors)
    _check_class_file(layout.object_classes_file(data_root), None, errors)
    if not layout.meta_file(data_root).exists():
        errors.append("missing: META.md")

    videos_dir = data_root / "data" / "videos"
    vids = sorted(p.name for p in videos_dir.iterdir() if p.is_dir()) if videos_dir.is_dir() else []
    if not vids:
        errors.append("no per-video directories under data/videos/")

    for vid in vids:
        npy = layout.npy_path(data_root, vid)
        det = layout.detections_path(data_root, vid)
        ocr = layout.ocr_path(data_root, vid)
        if npy.exists():
            _check_npy(npy, errors)
        if det.exists():
            _check_json(det, _DET_ROOT_KEYS, _DET_REC_KEYS, errors, bbox=True)
        if ocr.exists():
            _check_json(ocr, _OCR_ROOT_KEYS, _OCR_REC_KEYS, errors)
        if not (npy.exists() or det.exists() or ocr.exists()):
            errors.append(f"{vid}: no artifacts")

    return errors


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) != 1:
        print("usage: python -m avra_metadata_extractor.validate DATA_ROOT", file=sys.stderr)
        return 2
    errors = validate(argv[0])
    for e in errors:
        print(f"  - {e}")
    if errors:
        print(f"VALIDATE_FAIL ({len(errors)} error(s))")
        return 1
    print("VALIDATE_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
