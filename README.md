# AVRA-Metadata-Extractor

> **Winner — KilometerAudio Track, Perception Test Challenge 2026**
>
> **Team IUCV · Indiana University Bloomington**

[Challenge](https://eval.ai/web/challenges/challenge-page/2706/overview) ·
[Solver](https://github.com/juhha/AVRA-Solver/)

AVRA (Audio–Visual Reasoning Agent) is a training-free system for multiple-choice question answering over long videos. It uses generic metadata to localize candidate moments, directly inspects the corresponding source media, and records evidence before selecting an answer.



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
localize relevant moments in long videos. AVRA-Metadata-Extractor produces
that index. Given a set of source videos, it runs three independent extraction
pipelines — sound event detection (SED), object detection, and optical
character recognition (OCR) — and writes a unified per-video metadata file
that the downstream solver can search without touching raw media.

The extraction is entirely offline and model-agnostic with respect to the
question-answering task: no answer options, questions, or task-specific
fine-tuning influence the metadata. This separation allows the same index to
support multiple solver configurations or future challenge tracks.

## How AVRA Works

1. **Extract audio events.** A sound event detection model processes each
   video's audio track and produces timestamped event labels with confidence
   scores.
2. **Detect visual objects.** An object detection model (YOLOE) runs over
   sampled video frames and records bounding boxes, class labels, and
   timestamps.
3. **Recognize on-screen text.** An OCR stage extracts visible text from
   sampled frames with timestamps, capturing titles, captions, signs, and
   other readable content.
4. **Merge and format.** Per-pipeline outputs are merged into a single
   structured metadata file per video, following the schema expected by
   [AVRA-Solver](https://github.com/juhha/AVRA-Solver).
5. **Validate.** Deterministic checks confirm that every video in the dataset
   has a complete, well-formed metadata file before solver runs begin.

## Install
 
AVRA runs its metadata extraction directly on the host machine. The extractor produces the per-video index that
[AVRA-Solver](https://github.com/juhha/AVRA-Solver) reads at solve time.
 
```bash
git clone https://github.com/edredelijah-boop/hello.git
cd hello
 
python -m venv .venv && source .venv/bin/activate
pip install ".[all]"          # or ".[objects]" / ".[text]" for one stage
```
 
You will also need `ffmpeg` and `ffprobe` on your `PATH`, and one model
checkpoint downloaded manually (BEATs). Full details — including per-stage
extras, GPU recommendations, and weight download links — are in
**[docs/INSTALLATION.md](docs/INSTALLATION.md)** and
**[docs/MODELS.md](docs/MODELS.md)**.


## Documentation

| Document | Contents |
| --- | --- |
| [Installation](docs/INSTALLATION.md) | Python, ffmpeg, extras, model weights |
| [Usage](docs/USAGE.md) | Commands, flags, output locations, batching |
| [Output format](docs/OUTPUT_FORMAT.md) | The three artifact schemas + the `data_root` tree |
| [Models](docs/MODELS.md) | Exact checkpoints, versions, licenses |
| [Reproducibility](docs/REPRODUCIBILITY.md) | What is deterministic and what is not |


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

Released under the [MIT License](LICENSE).
](https://github.com/edredelijah-boop/hello)
