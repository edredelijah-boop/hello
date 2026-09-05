# Installation

## Requirements

- Python 3.10+
- `ffmpeg` and `ffprobe` on `PATH` (frame sampling and audio decoding)
- A CUDA GPU is strongly recommended for the audio and object stages; both run
  on CPU but slowly.
- Disk for sampled frames: roughly 100 KB/frame at 2 fps, so about 700 MB per
  hour of video. Frames are deleted after each video unless `--keep-frames`.

## Package

```bash
python -m venv .venv
source .venv/bin/activate
pip install ".[all]"
```

Extras, if you only need one stage:

| Extra | Pulls in | Stage |
| --- | --- | --- |
| _(base)_ | `torch`, `torchaudio`, `librosa`, `soundfile` | `audio` |
| `.[objects]` | `ultralytics`, `opencv-python-headless` | `objects` |
| `.[text]` | `paddleocr`, `paddlepaddle` | `text` |
| `.[all]` | all of the above | `all`, `batch` |
| `.[dev]` | `pytest`, `rapidfuzz` | tests / optional OCR summary |

> **`ultralytics` is licensed AGPL-3.0.** It is only imported at runtime by the
> `objects` stage and is not redistributed here. See [MODELS.md](MODELS.md) and
> [../NOTICE](../NOTICE).

Match `torch` / `paddlepaddle` to your CUDA version per the upstream install
guides. Pin `paddleocr` / `paddlepaddle` to the versions that work in your
environment — PaddleOCR's model routing changes between minor releases.

## Model weights

| Model | How to get it | Point the tool at it |
| --- | --- | --- |
| **BEATs strong SED** (`BEATs_strong_1.pt`) | Download from [fschmid56/PretrainedSED releases](https://github.com/fschmid56/PretrainedSED/releases) | `--checkpoint PATH` or `export AVRA_BEATS_CHECKPOINT=PATH` |
| **YOLOE** (`yoloe-11l-seg.pt`) | Auto-downloaded by `ultralytics` on first run | `--weights PATH` or `AVRA_YOLOE_WEIGHTS` to override |
| **PP-OCRv6** | Auto-downloaded by PaddleOCR on first run | n/a |

The BEATs base weights are loaded from inside `BEATs_strong_1.pt`; you do not
need a separate BEATs download.

## Verify

```bash
./tests/smoke-offline.sh     # no ffmpeg / models / network  -> OFFLINE_SMOKE_PASS
```

With ffmpeg, the extras, and `AVRA_BEATS_CHECKPOINT` set:

```bash
./tests/smoke-e2e.sh         # 4 s synthetic video through all three stages -> E2E_SMOKE_PASS
```
