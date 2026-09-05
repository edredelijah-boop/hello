"""Text stage: PP-OCRv6 on sampled frames -> ``<video_id>_ocr.json``.

Frame timestamps come from the frames ``manifest.json``. Recognized strings are
kept only when the recognizer score clears ``min_score`` and the normalized form
is at least ``min_text_length`` characters.
"""

import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .. import constants, layout
from ..common import jsonio
from ..common.frames import frame_timestamp
from ..common.media import normalize_text

PROGRESS_EVERY = 100   # frames between progress updates


def load_model(lang=constants.OCR_LANG):
    from paddleocr import PaddleOCR   # imported lazily: heavy optional dependency

    return PaddleOCR(lang=lang)


def ocr_frames(ocr, frames_dir, fps, first_index,
               min_score=constants.OCR_MIN_SCORE,
               min_text_length=constants.OCR_MIN_TEXT_LENGTH,
               progress=True):
    frames = sorted(Path(frames_dir).glob("*.jpg"))
    detections = []
    dropped_short = dropped_score = 0
    total = len(frames)
    start = time.time()

    for i, path in enumerate(frames):
        if progress and i % PROGRESS_EVERY == 0 and i > 0:
            elapsed = time.time() - start
            eta = (total - i) * elapsed / i
            sys.stdout.write(
                f"\r  ocr: {100 * i / total:5.1f}%  [{i}/{total}]  "
                f"{i / elapsed:5.1f} fps  kept={len(detections)}  eta {eta:5.0f}s   ")
            sys.stdout.flush()

        t = frame_timestamp(int(path.stem), fps, first_index)
        for res in ocr.predict(str(path)):
            texts = res.get("rec_texts", [])
            scores = res.get("rec_scores", [])
            for text, score in zip(texts, scores):
                if score < min_score:
                    dropped_score += 1
                    continue
                norm = normalize_text(text)
                if len(norm) < min_text_length:
                    dropped_short += 1
                    continue
                detections.append({
                    "t": round(t, 3),
                    "text": text,
                    "text_norm": norm,
                    "score": round(float(score), 4),
                })

    if progress:
        print()
    return detections, {
        "elapsed_s": round(time.time() - start, 1),
        "dropped_short": dropped_short,
        "dropped_score": dropped_score,
    }


def extract_text(frames_dir, manifest, data_root, video_id=None,
                 min_score=constants.OCR_MIN_SCORE,
                 min_text_length=constants.OCR_MIN_TEXT_LENGTH,
                 model=None, progress=True):
    """OCR the sampled frames and write the text index. Returns the output path."""
    video_id = video_id or manifest["video_id"]
    out_path = layout.ocr_path(data_root, video_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if model is None:
        if progress:
            print(f"[text] loading PaddleOCR ({constants.OCR_VERSION}, lang={constants.OCR_LANG})")
        model = load_model()

    if progress:
        print(f"[text] {video_id}: reading {manifest['frame_count']} frames")
    detections, stats = ocr_frames(
        model, frames_dir, manifest["fps"], manifest["first_frame_index"],
        min_score=min_score, min_text_length=min_text_length, progress=progress)

    jsonio.write_json(out_path, {
        "video_id": video_id,
        "fps": manifest["fps"],
        "frame_count": manifest["frame_count"],
        "duration": manifest["duration"],
        "ocr_version": constants.OCR_VERSION,
        "ocr_lang": constants.OCR_LANG,
        "min_text_length": min_text_length,
        "min_score": min_score,
        "stats": stats,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "detections": detections,
    })
    if progress:
        print(f"[text] {video_id}: kept {len(detections)} "
              f"(dropped_short={stats['dropped_short']}, "
              f"dropped_score={stats['dropped_score']}) -> {out_path}")
    return out_path
