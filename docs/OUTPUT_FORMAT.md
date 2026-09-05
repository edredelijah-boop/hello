# Output format

The extractor writes the tree that AVRA-Solver's `scripts/prepare.sh` consumes
as its `data_root`:

```
data_root/
├── META.md
└── data/
    ├── audio_classes_447.txt
    ├── object_classes.txt
    └── videos/
        └── <video_id>/
            ├── <video_id>.mp4
            ├── <video_id>.npy
            ├── <video_id>_detections.json
            └── <video_id>_ocr.json
```

`<video_id>` is the source filename stem. Timestamps everywhere are
**source-video seconds**.

## Class vocabularies

Both files are `<zero-based index><TAB><class name>`, one class per line.

- `audio_classes_447.txt` — 447 lines. The row index matches the first
  dimension of every `.npy`.
- `object_classes.txt` — the YOLOE detection vocabulary. Read the file rather
  than hard-coding a count.

## `<video_id>.npy` — audio events

A NumPy array, shape `(447, T)`, `float16`, C-order. Value `[c, t]` is the BEATs
strong SED probability for class `c` in the 40 ms frame starting at
`t / 25` seconds (25 steps per second). `T = ceil(duration_seconds / 0.04)`.

Rows follow `audio_classes_447.txt`. Values are sigmoid outputs in `[0, 1]`; they
are **not** thresholded — that is the consumer's choice.

## `<video_id>_detections.json` — objects

```json
{
  "video_id": "abc123",
  "fps": 2.0,
  "duration_s": 3600.0,
  "frame_count": 7200,
  "total_detections": 21874,
  "conf_threshold": 0.25,
  "vocabulary_size": 51,
  "detections": [
    {
      "frame": 13,
      "time_s": 6.5,
      "timestamp": "00:00:06.50",
      "class": "person",
      "conf": 0.851,
      "bbox": [7.5, 0.0, 36.6, 35.9]
    }
  ]
}
```

`frame` is the 1-based frame index; `time_s = (frame - 1) / fps`. `bbox` is
pixel `[x1, y1, x2, y2]`.

## `<video_id>_ocr.json` — on-screen text

```json
{
  "video_id": "abc123",
  "fps": 2.0,
  "frame_count": 7200,
  "duration": 3600.0,
  "ocr_version": "PP-OCRv6",
  "ocr_lang": "en",
  "min_text_length": 3,
  "min_score": 0.5,
  "stats": { "elapsed_s": 313.8, "dropped_short": 2536, "dropped_score": 2398 },
  "created_at": "2026-08-06T18:47:41.655714+00:00",
  "detections": [
    { "t": 1.5, "text": "KADIKOY ISKELESI", "text_norm": "kadikoy iskelesi", "score": 0.8864 }
  ]
}
```

- `text` is the raw recognizer output; `score` is its confidence.
- `text_norm` is `text` lowercased, NFKD-decomposed, stripped of combining marks
  and every character outside `[a-z0-9 ]`, with whitespace collapsed. This is
  **ASCII-only by design**: Greek / Cyrillic / CJK strings normalize to empty
  and are dropped by `min_text_length`. Correct for Latin-script signage, a
  known limitation elsewhere.
- A row is kept only if `score >= min_score` **and**
  `len(text_norm) >= min_text_length`. `stats` counts what was dropped.

## `META.md`

A generated free-form note recording which models and parameters produced the
metadata. AVRA-Solver requires the file to exist and copies it into each
question workspace; its contents are informational.

## Validation

`scripts/validate.sh DATA_ROOT` (or `python -m avra_metadata_extractor.validate`)
checks structure only — file presence, array shape/dtype, JSON schema, class-file
format. It does not judge whether detections are correct.
