# AVRA-Metadata-Extractor

> Companion to **[AVRA-Solver](https://github.com/juhha/AVRA-Solver)** —
> **2nd Place, KilometerAudio Track, Perception Test Challenge 2026** ·
> **Team IUCV · Indiana University Bloomington**

AVRA answers multiple-choice questions about long videos by first searching a
precomputed, query-agnostic index of what can be heard and seen, then inspecting
the source media directly. This repository builds that index.

Given a source video it produces three per-video metadata streams:

| Artifact | Model | Rate | Contents |
| --- | --- | --- | --- |
| `<video_id>.npy` | BEATs strong SED (PretrainedSED) | 40 ms / 25 Hz | frame-level scores for 447 AudioSet classes |
| `<video_id>_detections.json` | YOLOE open-vocabulary detector | 2 fps | class, confidence, timestamp, bbox |
| `<video_id>_ocr.json` | PP-OCRv6 (PaddleOCR) | 2 fps | recognized text, normalized text, confidence, timestamp |

These are **noisy search indices for candidate localization**, not ground truth
and not final answer evidence. The solver verifies every candidate moment in the
source media.

## What this repo is

The metadata-extraction half of the scored AVRA system, lifted out of a much
larger research codebase and rewritten as a small installable package. It takes
videos in and writes an [AVRA-Solver](https://github.com/juhha/AVRA-Solver)
`data_root` out.

The scored submission used BEATs strong SED, YOLOE (`yoloe-11l-seg`), and
PP-OCRv6 with the parameters that are the defaults here.

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install ".[all]"          # or ".[objects]" / ".[text]" for one stage
```

`ffmpeg` and `ffprobe` must be on `PATH`. Model weights are fetched separately —
see **[docs/INSTALLATION.md](docs/INSTALLATION.md)** and
**[docs/MODELS.md](docs/MODELS.md)**.

## Quick start

Structural self-test (no ffmpeg, no models, no network):

```bash
./tests/smoke-offline.sh
```

Extract everything for one video:

```bash
export AVRA_BEATS_CHECKPOINT=/path/to/BEATs_strong_1.pt
avra-extract all /path/to/video.mp4 --data-root ./data_root
./scripts/validate.sh ./data_root
```

Batch a directory of videos:

```bash
./scripts/run-batch.sh /path/to/videos --data-root ./data_root
```

The `data_root/` that comes out is exactly what AVRA-Solver's `scripts/prepare.sh`
expects. See **[docs/USAGE.md](docs/USAGE.md)**.

## Documentation

| Document | Contents |
| --- | --- |
| [Installation](docs/INSTALLATION.md) | Python, ffmpeg, extras, model weights |
| [Usage](docs/USAGE.md) | Commands, flags, output locations, batching |
| [Output format](docs/OUTPUT_FORMAT.md) | The three artifact schemas + the `data_root` tree |
| [Models](docs/MODELS.md) | Exact checkpoints, versions, licenses |
| [Reproducibility](docs/REPRODUCIBILITY.md) | What is deterministic and what is not |

## What this repo does not contain

Source videos, challenge questions or answers, model weights, the AVRA solver
itself (see [AVRA-Solver](https://github.com/juhha/AVRA-Solver)), or any Gemini /
LLM answering code. You supply videos; the extractor supplies metadata.

## Team

**Team IUCV** — Luddy School of Informatics, Computing, and Engineering,
Indiana University Bloomington.

- **Edred Azziz\*** · **Juhyung Ha\*** · **David Crandall†**

\* Equal contribution.  † Corresponding author.

## Citation

```bibtex
@software{azziz2026avra,
  author = {Edred Azziz and Juhyung Ha and David Crandall},
  title  = {AVRA: Agentic Audio--Visual Reasoning for Long Videos},
  year   = {2026},
  url    = {https://github.com/eazziz/AVRA-Metadata-Extractor}
}
```

## License

MIT — see [LICENSE](LICENSE). Third-party components (vendored BEATs, and the
optional Ultralytics and PaddleOCR dependencies) retain their own licenses;
see [NOTICE](NOTICE). Note that `ultralytics` is **AGPL-3.0**.
