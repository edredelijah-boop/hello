"""Write the non-per-video parts of an AVRA ``data_root``.

* ``data/audio_classes_447.txt`` and ``data/object_classes.txt`` -- the class
  vocabularies, as ``<zero-based index><TAB><class name>`` (the format the AVRA
  solver's ``prepare.sh`` reads).
* ``META.md`` -- a short free-form note recording how the metadata was produced.
* the source ``<video_id>.mp4``, symlinked (default) or copied into place.
"""

import os
import shutil
from pathlib import Path

from . import constants, layout
from .audioset_classes import as_strong_train_classes
from .objects.vocab import CLASSES as OBJECT_CLASSES


def _write_class_file(path, names):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for i, name in enumerate(names):
            f.write(f"{i}\t{name}\n")


def write_class_files(data_root):
    _write_class_file(layout.audio_classes_file(data_root), as_strong_train_classes)
    _write_class_file(layout.object_classes_file(data_root), OBJECT_CLASSES)


def write_meta(data_root, overwrite=False):
    path = layout.meta_file(data_root)
    if path.exists() and not overwrite:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_META_TEMPLATE.format(
        n_audio=len(as_strong_train_classes),
        n_object=len(OBJECT_CLASSES),
        fps=constants.SAMPLE_FPS,
        ocr_version=constants.OCR_VERSION,
        yoloe=constants.YOLOE_WEIGHTS,
    ), encoding="utf-8")
    return path


def place_video(data_root, video_path, video_id=None, copy=False):
    video_path = Path(video_path).resolve()
    video_id = video_id or video_path.stem
    dst = layout.video_path(data_root, video_id)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        return dst
    if copy:
        shutil.copy2(video_path, dst)
    else:
        os.symlink(video_path, dst)
    return dst


_META_TEMPLATE = """\
# Precomputed metadata

Produced by AVRA-Metadata-Extractor. Each source video was processed once,
independently of any question or answer option, into three temporal indices:

- **Audio events** (`<video_id>.npy`): frame-level BEATs SED, {n_audio} AudioSet
  strong classes at 40 ms resolution (25 steps per second). Row `t` maps to
  source time `t / 25` seconds. Rows follow `data/audio_classes_447.txt`.
- **Visual objects** (`<video_id>_detections.json`): YOLOE open-vocabulary
  detection (`{yoloe}`) on frames sampled at {fps} fps, over the {n_object}-class
  vocabulary in `data/object_classes.txt`.
- **On-screen text** (`<video_id>_ocr.json`): {ocr_version} on frames sampled at
  {fps} fps.

These are noisy localization hints, not ground truth and not final answer
evidence. Timestamps are in source-video seconds.
"""
