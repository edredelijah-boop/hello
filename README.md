# AVRA-Metadata-Extractor

> **2nd Place — KilometerAudio Track, Perception Test Challenge 2026**
>
> **Team IUCV · Indiana University Bloomington**

[Challenge](https://eval.ai/web/challenges/challenge-page/2706/overview) ·
[Solver](https://github.com/juhha/AVRA-Solver)

## Challenge Result

| Item | Result |
| --- | --- |
| Challenge | Perception Test Challenge 2026 |
| Track | KilometerAudio |
| Team | IUCV |
| Ranking | 2nd place |
| Score | 0.78 top-1 accuracy |
| Evaluation | Zero-shot with frozen model weights; no training or fine-tuning |

## Overview

AVRA's solver relies on a precomputed, query-agnostic metadata index to
localize relevant moments in long videos. AVRA-Metadata-Extractor produces that
index. Given a set of source videos, it runs three independent extraction
pipelines — sound event detection (SED), object detection, and optical character
recognition (OCR) — and writes a per-video file for each: an SED index, an
object-detection index, and an OCR index. The downstream solver reads these
files directly and never touches the raw media during search.

The extraction is entirely offline and model-agnostic with respect to the
question-answering task: no answer options, questions, or task-specific
fine-tuning influence the metadata. This separation allows the same index to
support multiple solver configurations or future challenge tracks.

## How It Works

1. **Extract audio events.** A sound event detection model processes each
   video's audio track and produces timestamped event labels with confidence
   scores.
2. **Detect visual objects.** An object detection model (YOLOE) runs over
   sampled video frames and records bounding boxes, class labels, and
   timestamps.
3. **Recognize on-screen text.** An OCR stage extracts visible text from
   sampled frames with timestamps, capturing titles, captions, signs, and
   other readable content.
4. **Write the index.** Each pipeline writes its own per-video file — the SED
   matrix, the object detections, and the OCR results — in the layout
   [AVRA-Solver](https://github.com/juhha/AVRA-Solver) expects as its
   `data_root`.
5. **Validate.** Deterministic checks confirm that every video's metadata files
   are present and well-formed before solver runs begin.

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

**Team IUCV**<br>
Luddy School of Informatics, Computing, and Engineering<br>
Indiana University Bloomington

- **Edred Azziz<sup>*</sup>**
- **Juhyung Ha<sup>*</sup>**
- **David Crandall<sup>†</sup>**

<sup>*</sup> Equal contribution.<br>
<sup>†</sup> Corresponding author.

## Citation

If you use AVRA in your research, please cite:

```bibtex
@software{azziz2026avra,
  author = {Edred Azziz and Juhyung Ha and David Crandall},
  title = {AVRA-Solver: Agentic Audio--Visual Reasoning for Long Videos},
  year = {2026},
  url = {https://github.com/juhha/AVRA-Solver}
}
```

## License

Released under the [MIT License](LICENSE). Third-party components retain their
own licenses — see [NOTICE](NOTICE); note that the optional `objects` extra
pulls in `ultralytics` (AGPL-3.0).
