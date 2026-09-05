"""Object stage: YOLOE open-vocabulary detection -> ``<video_id>_detections.json``.

Runs YOLOE over the sampled frames using the fixed vocabulary in ``vocab.py``.
Frame timestamps come from the frames ``manifest.json``, never from a local
constant, so this stage cannot drift out of sync with the frame extractor.
"""

import os
import time
from pathlib import Path

import torch

from .. import constants, layout
from ..common import jsonio
from ..common.frames import frame_timestamp
from .vocab import CLASSES

torch.backends.cudnn.enabled = False   # matches the scored configuration


def _resolve_weights(weights):
    return (weights
            or os.environ.get(constants.ENV_YOLOE_WEIGHTS)
            or constants.YOLOE_WEIGHTS)


def load_model(weights=None):
    from ultralytics import YOLOE   # imported lazily: heavy, AGPL-3.0 dependency

    model = YOLOE(_resolve_weights(weights))
    model.set_classes(CLASSES, model.get_text_pe(CLASSES))
    return model


def _hhmmss(t):
    return f"{int(t // 3600):02d}:{int((t % 3600) // 60):02d}:{t % 60:05.2f}"


def detect_frames(model, frames_dir, fps, first_index, conf, progress=True):
    frames = sorted(Path(frames_dir).glob("*.jpg"))
    detections = []
    start = time.time()

    for i, path in enumerate(frames):
        frame_num = int(path.stem)
        time_s = frame_timestamp(frame_num, fps, first_index)
        results = model.predict(str(path), conf=conf, verbose=False)
        for box in results[0].boxes:
            detections.append({
                "frame": frame_num,
                "time_s": round(time_s, 2),
                "timestamp": _hhmmss(time_s),
                "class": CLASSES[int(box.cls)],
                "conf": round(float(box.conf), 3),
                "bbox": [round(x, 1) for x in box.xyxy[0].tolist()],
            })
        if progress and (i + 1) % 200 == 0:
            rate = (i + 1) / (time.time() - start)
            eta = (len(frames) - i - 1) / rate / 60
            print(f"  {i + 1}/{len(frames)} frames | {rate:.1f} fps | ~{eta:.1f} min left")

    return detections, len(frames)


def extract_objects(frames_dir, manifest, data_root, video_id=None,
                    weights=None, conf=constants.YOLOE_CONF, model=None,
                    progress=True):
    """Detect objects in the sampled frames and write the detections JSON.

    Returns the output path.
    """
    video_id = video_id or manifest["video_id"]
    out_path = layout.detections_path(data_root, video_id)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if model is None:
        if progress:
            print(f"[objects] loading YOLOE ({len(CLASSES)} classes)")
        model = load_model(weights)

    if progress:
        print(f"[objects] {video_id}: scanning {manifest['frame_count']} frames")
    detections, frame_count = detect_frames(
        model, frames_dir, manifest["fps"], manifest["first_frame_index"],
        conf, progress=progress)

    jsonio.write_json(out_path, {
        "video_id": video_id,
        "fps": manifest["fps"],
        "duration_s": manifest["duration"],
        "frame_count": frame_count,
        "total_detections": len(detections),
        "conf_threshold": conf,
        "vocabulary_size": len(CLASSES),
        "detections": detections,
    })
    if progress:
        print(f"[objects] {video_id}: {len(detections)} detections -> {out_path}")
    return out_path
