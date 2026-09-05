"""Fixed parameters for the three extraction stages.

Split into two groups:

* Model facts fixed by a checkpoint or an architecture — do not change these
  unless you also swap the corresponding weights.
* Sampling / threshold knobs that were frozen for the scored AVRA submission.
  They are exposed as CLI flags; the values here are the defaults.
"""

# ---------------------------------------------------------------------------
# BEATs SED — fixed by the checkpoint
# ---------------------------------------------------------------------------
SAMPLE_RATE = 16_000
CHUNK_SECONDS = 10
CHUNK_SAMPLES = CHUNK_SECONDS * SAMPLE_RATE
FRAME_SECONDS = 0.04            # 250 SED frames per 10 s chunk -> 40 ms grid, 25 steps/s
N_AUDIO_CLASSES = 447
SED_BATCH_SIZE = 16            # 10 s chunks per forward pass

# ---------------------------------------------------------------------------
# Frame sampling — shared by the object and text stages
# ---------------------------------------------------------------------------
SAMPLE_FPS = 2.0               # frames/sec; signage passes quickly in a walking tour
JPEG_QUALITY = 2               # ffmpeg -q:v, lower = better quality / larger files
FRAME_PATTERN = "%06d.jpg"
FIRST_FRAME_INDEX = 1          # ffmpeg numbers extracted frames from 1
MANIFEST_NAME = "manifest.json"

# ---------------------------------------------------------------------------
# YOLOE object detection
# ---------------------------------------------------------------------------
YOLOE_WEIGHTS = "yoloe-11l-seg.pt"
YOLOE_CONF = 0.25

# ---------------------------------------------------------------------------
# PP-OCRv6 text
# ---------------------------------------------------------------------------
OCR_VERSION = "PP-OCRv6"       # PaddleOCR default for English / Latin script
OCR_LANG = "en"
OCR_MIN_SCORE = 0.5           # recognizer confidence floor
OCR_MIN_TEXT_LENGTH = 3       # drop normalized strings shorter than this

# ---------------------------------------------------------------------------
# Environment variables consulted for model weights
# ---------------------------------------------------------------------------
ENV_BEATS_CHECKPOINT = "AVRA_BEATS_CHECKPOINT"
ENV_YOLOE_WEIGHTS = "AVRA_YOLOE_WEIGHTS"
