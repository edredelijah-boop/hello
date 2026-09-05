# Models

The scored AVRA submission used the three models below with the parameters that
are the defaults in this repo. Hosted / released weights can change upstream, so
record the versions you actually ran.

## Audio — BEATs strong SED

- **Architecture:** BEATs (Microsoft), vendored under
  `src/avra_metadata_extractor/audio/beats/`. MIT License, Copyright (c) 2022
  Microsoft. Source: <https://github.com/microsoft/unilm/tree/master/beats>.
  Copied unchanged except that intra-package imports were made relative.
- **SED head + checkpoint:** `BEATs_strong_1.pt` from
  <https://github.com/fschmid56/PretrainedSED/releases>, from
  F. Schmid et al., *Effective Pre-Training of Audio Transformers for Sound
  Event Detection*, ICASSP 2025. The checkpoint bundles the BEATs base weights,
  the 447-class strong head, and an unused weak head.
- **Key remap:** checkpoints use `model.model.*`; `audio/head.py` remaps to
  `model.beats.*` at load and asserts an exact `state_dict` match.
- **Inference:** 16 kHz mono, 10 s chunks, `sigmoid` on the strong-head logits,
  adaptive-avg-pooled to a 250-frame (40 ms) grid per chunk, trimmed to the true
  audio length. `torch.backends.cudnn.enabled = False`, matching the scored run.
- **Classes:** the 447 AudioSet "strong" class names (Google, CC BY 4.0).

## Objects — YOLOE

- **Package:** `ultralytics`, **AGPL-3.0-or-later**.
  <https://github.com/ultralytics/ultralytics>
- **Weights:** `yoloe-11l-seg.pt`, auto-downloaded by `ultralytics`. Override
  with `--weights` or `$AVRA_YOLOE_WEIGHTS`.
- **Prompting:** open-vocabulary text prompts — the 51 class strings in
  `object_classes.txt`, set via `model.set_classes(names, model.get_text_pe(names))`.
- **Sampling:** frames at 2 fps, `conf >= 0.25`.

> **Licensing note.** This project imports `ultralytics` at runtime only and does
> not redistribute it or its weights, so the project's own MIT license is
> unaffected. If *you* redistribute a bundle that includes `ultralytics`, the
> AGPL-3.0 terms apply to that bundle. Ultralytics also sells a commercial
> license. If AGPL is a problem for your use, swap in a permissively licensed
> open-vocabulary detector — only `objects/extract.py` and `objects/vocab.py`
> would change.

## Text — PP-OCRv6

- **Package:** `paddleocr` + `paddlepaddle`, Apache-2.0.
  <https://github.com/PaddlePaddle/PaddleOCR>
- **Models:** PP-OCRv6 English/Latin, auto-downloaded on first use.
- **API:** `PaddleOCR(lang="en").predict(frame)`, reading `rec_texts` /
  `rec_scores` from each result.
- **Filtering:** `score >= 0.5` and normalized length `>= 3`.

## Frame sampling

`ffmpeg -vf fps=2 -q:v 2`, JPEG. A `manifest.json` records `fps`,
`frame_count`, `duration`, and `first_frame_index` (1); every downstream
timestamp is `(frame_number - 1) / fps`.
