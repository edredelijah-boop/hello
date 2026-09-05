# Reproducibility

## Deterministic

- **The pipeline structure.** `tests/smoke-offline.sh` builds a `data_root` and
  runs the structural validator with no ffmpeg, no models, and no network. It
  proves the packaging, the `data_root` layout, the class-file generation, and
  the validator are self-consistent.
- **Frame sampling.** `ffmpeg -vf fps=2` on a given file and ffmpeg build is
  deterministic. The `manifest.json` pins `fps` and `first_frame_index`, so
  object and text timestamps are a pure function of the frame filenames.
- **Artifact schemas.** Fixed and checked by `validate.sh` — see
  [OUTPUT_FORMAT.md](OUTPUT_FORMAT.md).

## Not bit-reproducible

- **Model outputs.** Exact SED probabilities, detection boxes, and OCR strings
  depend on the weights, the framework version, CUDA/cuDNN, and GPU model. Pin
  `torch`, `ultralytics`, `paddleocr`, and `paddlepaddle`, and record the
  checkpoint filenames (`run.json`-style) alongside your `data_root`.
- **Auto-downloaded weights.** YOLOE and PP-OCRv6 weights are fetched by their
  frameworks and can be updated upstream. Cache and version them if you need to
  reproduce a specific run.
- **ffmpeg builds** differ slightly in JPEG encoding; this does not change frame
  timestamps but can nudge a borderline detection or OCR score.

## Scope

This repo reproduces the **extraction workflow and artifact contracts** of the
scored AVRA submission, not bit-identical metadata. The published challenge
result should be described as a recorded result of the stated frozen
configuration (BEATs strong SED, `yoloe-11l-seg`, PP-OCRv6, defaults as shipped
here), while the offline test is a directly re-runnable check of the released
implementation.

Source videos, questions, answers, and model weights are not distributed here.
