"""AVRA metadata extraction.

Turns a source video into the three per-video indices the AVRA solver consumes
for candidate localization:

    <video_id>.npy               frame-level BEATs SED, 447 AudioSet classes @ 40 ms
    <video_id>_detections.json   YOLOE open-vocabulary object detection @ 2 fps
    <video_id>_ocr.json          PP-OCRv6 on-screen text @ 2 fps

These are noisy search indices, not ground truth. See docs/OUTPUT_FORMAT.md.
"""

__version__ = "0.1.0"
