"""Where every input and output file lives.

The output tree is the layout the AVRA solver's ``prepare.sh`` expects as its
``data_root`` argument:

    data_root/
    |-- META.md
    `-- data/
        |-- audio_classes_447.txt
        |-- object_classes.txt
        `-- videos/
            `-- <video_id>/
                |-- <video_id>.mp4              (symlink or copy of the source)
                |-- <video_id>.npy
                |-- <video_id>_detections.json
                `-- <video_id>_ocr.json

Sampled frames are working state, not a delivered artifact, so they live under a
separate ``frames_root`` (default ``./frames``) that can be deleted after a run.
"""

from pathlib import Path

from . import constants


def video_dir(data_root, video_id) -> Path:
    return Path(data_root) / "data" / "videos" / video_id


def video_path(data_root, video_id, ext=".mp4") -> Path:
    return video_dir(data_root, video_id) / f"{video_id}{ext}"


def npy_path(data_root, video_id) -> Path:
    return video_dir(data_root, video_id) / f"{video_id}.npy"


def detections_path(data_root, video_id) -> Path:
    return video_dir(data_root, video_id) / f"{video_id}_detections.json"


def ocr_path(data_root, video_id) -> Path:
    return video_dir(data_root, video_id) / f"{video_id}_ocr.json"


def audio_classes_file(data_root) -> Path:
    return Path(data_root) / "data" / "audio_classes_447.txt"


def object_classes_file(data_root) -> Path:
    return Path(data_root) / "data" / "object_classes.txt"


def meta_file(data_root) -> Path:
    return Path(data_root) / "META.md"


def frames_dir(frames_root, video_id) -> Path:
    return Path(frames_root) / video_id


def manifest_path(frames_root, video_id) -> Path:
    return frames_dir(frames_root, video_id) / constants.MANIFEST_NAME
