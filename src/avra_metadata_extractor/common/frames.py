"""Shared frame-sampling stage.

Extracts frames from a video at a fixed rate and writes a ``manifest.json``
recording the extraction parameters. The object and text stages read the
manifest rather than assuming an fps, so their timestamps can never silently
drift out of sync with the frames on disk.

    frames_root/<video_id>/000001.jpg ...
    frames_root/<video_id>/manifest.json

A manifest means a completed extraction. Frames with no manifest mean a crashed
run and are deleted and redone rather than trusted.
"""

import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from .. import constants
from . import jsonio
from .media import ffprobe_duration


def _parse_out_time(value: str) -> float:
    """'00:01:23.456000' -> seconds; -1.0 if unparseable.

    Parses ffmpeg's ``out_time`` rather than ``out_time_ms`` (the latter is
    reported in microseconds despite its name in many ffmpeg builds).
    """
    try:
        h, m, s = value.split(":")
        return int(h) * 3600 + int(m) * 60 + float(s)
    except (ValueError, AttributeError):
        return -1.0


def frame_timestamp(frame_number: int, fps: float, first_index: int) -> float:
    """Source-video timestamp of a frame, from its filename index and the fps."""
    return (frame_number - first_index) / fps


def extract(video_path, out_dir, fps=constants.SAMPLE_FPS,
            jpeg_quality=constants.JPEG_QUALITY, progress=True) -> dict:
    """Run ffmpeg with live progress. Returns the manifest dict (not yet written)."""
    video_path = Path(video_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    duration = ffprobe_duration(video_path)
    expected = int(duration * fps)
    if progress:
        print(f"[run] {video_path.name}")
        print(f"      duration {duration:.1f}s -> ~{expected} frames at {fps} fps")

    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-i", str(video_path),
         "-vf", f"fps={fps}", "-q:v", str(jpeg_quality),
         "-progress", "pipe:1", "-nostats", "-loglevel", "error",
         str(out_dir / constants.FRAME_PATTERN)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1,
    )

    start = time.time()
    for line in proc.stdout:
        if not line.startswith("out_time="):
            continue
        t = _parse_out_time(line.strip().split("=", 1)[1])
        if t < 0 or not progress:
            continue
        elapsed = time.time() - start
        rate = t / elapsed if elapsed > 0 else 0
        eta = (duration - t) / rate if rate > 0 else 0
        sys.stdout.write(
            f"\r  extracting: {100 * t / max(duration, 1e-9):5.1f}%  "
            f"t={t:7.1f}s/{duration:.0f}s  {rate:5.1f}x realtime  eta {eta:5.0f}s   "
        )
        sys.stdout.flush()

    proc.wait()
    stderr = proc.stderr.read()
    if progress:
        print()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed (code {proc.returncode}): {stderr[:500]}")

    frames = sorted(out_dir.glob("*.jpg"))
    if not frames:
        raise RuntimeError(f"ffmpeg produced no frames for {video_path}")
    size_mb = sum(p.stat().st_size for p in frames) / 1e6
    if progress:
        print(f"[ok] {len(frames)} frames in {time.time() - start:.1f}s ({size_mb:.0f} MB)")

    return {
        "video_id": video_path.stem,
        "source_video": str(video_path),
        "fps": fps,
        "frame_count": len(frames),
        "duration": round(duration, 3),
        "jpeg_quality": jpeg_quality,
        "frame_pattern": constants.FRAME_PATTERN,
        "first_frame_index": constants.FIRST_FRAME_INDEX,
        "timestamp_formula": "t = (frame_number - first_frame_index) / fps",
        "size_mb": round(size_mb, 1),
        "extracted_at": datetime.now(timezone.utc).isoformat(),
    }


def load_manifest(video_frames_dir) -> dict:
    """Load a frames manifest; refuse to proceed without one."""
    path = Path(video_frames_dir) / constants.MANIFEST_NAME
    if not path.exists():
        raise SystemExit(
            f"no manifest at {path}\n"
            f"run the frames stage first (frames without a manifest mean a "
            f"crashed extraction and unreliable timestamps)"
        )
    return jsonio.read_json(path)


def ensure_frames(video_path, video_frames_dir, fps=constants.SAMPLE_FPS,
                  force=False, progress=True) -> dict:
    """Extract frames if needed and return the manifest.

    * manifest present and not forcing -> reuse it
    * frames present but no manifest    -> previous crash; wipe and redo
    """
    video_frames_dir = Path(video_frames_dir)
    manifest_file = video_frames_dir / constants.MANIFEST_NAME

    if manifest_file.exists() and not force:
        m = jsonio.read_json(manifest_file)
        if progress:
            print(f"[skip] frames present: {m['frame_count']} frames at "
                  f"{m['fps']} fps -> {video_frames_dir}")
        return m

    if video_frames_dir.exists():
        stale = list(video_frames_dir.glob("*.jpg"))
        if stale:
            if progress:
                print(f"[warn] {len(stale)} frames with no manifest -- re-extracting")
            for p in stale:
                p.unlink()

    manifest = extract(video_path, video_frames_dir, fps=fps, progress=progress)
    jsonio.write_json(manifest_file, manifest)
    if progress:
        print(f"[ok] wrote {manifest_file}")
    return manifest
