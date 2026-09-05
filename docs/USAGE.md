# Usage

Every command is a subcommand of `avra-extract` (installed console script). The
`scripts/*.sh` wrappers call the same thing and also work from a source checkout
without installing.

```
avra-extract frames   VIDEO
avra-extract audio     VIDEO
avra-extract objects   VIDEO
avra-extract text      VIDEO
avra-extract all       VIDEO
avra-extract batch     VIDEO_DIR
```

## Common flags

| Flag | Default | Meaning |
| --- | --- | --- |
| `--data-root DIR` | `./data_root` | where artifacts are written (AVRA-Solver layout) |
| `--frames-root DIR` | `./frames` | where sampled frames are cached |
| `--force` | off | redo a stage whose output already exists |
| `--quiet` | off | suppress progress output |

`video_id` is always the input filename without extension.

## Stages

### `frames`
Samples frames with ffmpeg and writes `frames/<video_id>/manifest.json`. The
`objects` and `text` stages run this automatically when the manifest is missing
and reuse it when present, so you rarely call it directly. `--fps` (default `2`)
lives here only — every downstream timestamp is derived from the manifest.

### `audio`
BEATs strong SED over the whole soundtrack → `<video_id>.npy`, a `(447, T)`
float16 matrix at 40 ms resolution. Needs `--checkpoint` or
`$AVRA_BEATS_CHECKPOINT`. `--device auto|cuda|cpu`. Does not use frames.

### `objects`
YOLOE over the sampled frames → `<video_id>_detections.json`. `--conf` (default
`0.25`), `--weights` / `$AVRA_YOLOE_WEIGHTS`. The detection vocabulary is fixed
in `object_classes.txt` (51 classes validated on walking-tour footage).

### `text`
PP-OCRv6 over the sampled frames → `<video_id>_ocr.json`. `--min-score`
(default `0.5`) and `--min-text-length` (default `3`, applied to the normalized
form). Text normalization is ASCII-only by design — see
[OUTPUT_FORMAT.md](OUTPUT_FORMAT.md).

### `all`
`frames` → `audio` → `objects` → `text` for one video, then deletes the frames
unless `--keep-frames`. `--copy-video` hard-copies the source mp4 into
`data_root` instead of symlinking it.

### `batch`
Runs `all` over every video in `VIDEO_DIR` (`.mp4 .mkv .webm .mov .avi .m4v`).
Models are loaded once and reused. `--only audio,objects,text` restricts the
stages. Finished artifacts are skipped, so re-running resumes. A failure on one
video is logged and the batch continues; the command exits non-zero if any
video failed. `scripts/run-batch.sh` adds a tee'd log under `logs/`.

## Output

```
data_root/
├── META.md
└── data/
    ├── audio_classes_447.txt
    ├── object_classes.txt
    └── videos/<video_id>/
        ├── <video_id>.mp4              # symlink (or copy with --copy-video)
        ├── <video_id>.npy
        ├── <video_id>_detections.json
        └── <video_id>_ocr.json
```

Check a finished tree:

```bash
./scripts/validate.sh ./data_root      # -> VALIDATE_PASS
```

Then hand it straight to the solver:

```bash
# in an AVRA-Solver checkout
./scripts/prepare.sh /abs/questions.json /abs/data_root
```
