"""Audio loading, ffprobe duration, and OCR text normalization."""

import re
import subprocess
import unicodedata

from .. import constants


def ffprobe_duration(video_path) -> float:
    """Source-video duration in seconds via ffprobe."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def load_audio(path, sample_rate=constants.SAMPLE_RATE):
    """Load any audio/video file as a mono float32 waveform at ``sample_rate``."""
    import librosa   # lazy: only the audio stage needs it

    waveform, _ = librosa.load(str(path), sr=sample_rate, mono=True)
    return waveform


def normalize_text(s: str) -> str:
    """Lowercase, strip accents, drop non-alphanumerics, collapse whitespace.

    ASCII-restricted by design: Greek / Cyrillic / CJK normalize to empty and
    are then dropped by the minimum-length filter. This is correct for
    Latin-script landmark and street-sign queries and a known limitation for
    non-Latin signage. Carried over verbatim from the scored pipeline so the
    ``text_norm`` field stays comparable across runs.
    """
    s = s.lower().strip()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))     # o-umlaut -> o
    s = re.sub(r"[^a-z0-9 ]", "", s)
    return re.sub(r"\s+", " ", s).strip()
