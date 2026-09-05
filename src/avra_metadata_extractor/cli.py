"""``avra-extract`` command line.

    avra-extract frames  VIDEO
    avra-extract audio   VIDEO
    avra-extract objects VIDEO
    avra-extract text    VIDEO
    avra-extract all     VIDEO
    avra-extract batch   VIDEO_DIR

Every command writes into an AVRA solver ``data_root`` (default ``./data_root``).
Sampled frames go to a separate ``frames_root`` (default ``./frames``).
"""

import argparse
import shutil
import sys
import traceback
from pathlib import Path

from . import __version__, constants, layout, provision
from .common import frames as frames_mod
from .common import jsonio

VIDEO_SUFFIXES = {".mp4", ".mkv", ".webm", ".mov", ".avi", ".m4v"}
MODALITIES = ("audio", "objects", "text")


# --------------------------------------------------------------------------- #
# shared helpers
# --------------------------------------------------------------------------- #

def _add_common(p):
    p.add_argument("--data-root", default="data_root",
                   help="AVRA data_root to write into (default: ./data_root)")
    p.add_argument("--frames-root", default="frames",
                   help="where sampled frames are cached (default: ./frames)")
    p.add_argument("--force", action="store_true",
                   help="redo stages whose output already exists")
    p.add_argument("--quiet", action="store_true", help="suppress progress output")


def _scaffold(data_root):
    provision.write_class_files(data_root)
    provision.write_meta(data_root)


def _video_id(video_path):
    return Path(video_path).stem


def _need(path, force):
    return not jsonio.already_done(path, force)


def _ensure_frames(args, video_path, vid):
    return frames_mod.ensure_frames(
        video_path, layout.frames_dir(args.frames_root, vid),
        fps=getattr(args, "fps", constants.SAMPLE_FPS),
        force=args.force, progress=not args.quiet)


def _drop_frames(args, vid):
    d = layout.frames_dir(args.frames_root, vid)
    if d.exists():
        shutil.rmtree(d, ignore_errors=True)


# --------------------------------------------------------------------------- #
# per-modality runners (accept a reusable model)
# --------------------------------------------------------------------------- #

def _run_audio(args, video_path, vid, models):
    from .audio import extract as audio_extract
    out = layout.npy_path(args.data_root, vid)
    if not _need(out, args.force):
        if not args.quiet:
            print(f"[skip] audio {vid} ({out} exists)")
        return
    if "audio" not in models:
        models["audio"] = audio_extract.load_model(
            args.checkpoint, audio_extract.pick_device(args.device))
    audio_extract.extract_audio_events(
        video_path, args.data_root, video_id=vid, model=models["audio"],
        device=args.device, progress=not args.quiet)


def _run_objects(args, video_path, vid, models):
    from .objects import extract as obj_extract
    out = layout.detections_path(args.data_root, vid)
    if not _need(out, args.force):
        if not args.quiet:
            print(f"[skip] objects {vid} ({out} exists)")
        return
    manifest = _ensure_frames(args, video_path, vid)
    if "objects" not in models:
        models["objects"] = obj_extract.load_model(args.weights)
    obj_extract.extract_objects(
        layout.frames_dir(args.frames_root, vid), manifest, args.data_root,
        video_id=vid, conf=args.conf, model=models["objects"],
        progress=not args.quiet)


def _run_text(args, video_path, vid, models):
    from .text import extract as text_extract
    out = layout.ocr_path(args.data_root, vid)
    if not _need(out, args.force):
        if not args.quiet:
            print(f"[skip] text {vid} ({out} exists)")
        return
    manifest = _ensure_frames(args, video_path, vid)
    if "text" not in models:
        models["text"] = text_extract.load_model()
    text_extract.extract_text(
        layout.frames_dir(args.frames_root, vid), manifest, args.data_root,
        video_id=vid, min_score=args.min_score,
        min_text_length=args.min_text_length, model=models["text"],
        progress=not args.quiet)


_RUNNERS = {"audio": _run_audio, "objects": _run_objects, "text": _run_text}


# --------------------------------------------------------------------------- #
# subcommands
# --------------------------------------------------------------------------- #

def cmd_frames(args):
    video_path = Path(args.video)
    vid = _video_id(video_path)
    frames_mod.ensure_frames(
        video_path, layout.frames_dir(args.frames_root, vid),
        fps=args.fps, force=args.force, progress=not args.quiet)
    return 0


def _single(args, modalities, keep_frames):
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"video not found: {video_path}", file=sys.stderr)
        return 2
    vid = _video_id(video_path)
    _scaffold(args.data_root)
    provision.place_video(args.data_root, video_path, vid,
                          copy=getattr(args, "copy_video", False))
    models = {}
    for m in modalities:
        _RUNNERS[m](args, video_path, vid, models)
    if not keep_frames:
        _drop_frames(args, vid)
    return 0


def cmd_audio(args):
    return _single(args, ["audio"], keep_frames=True)


def cmd_objects(args):
    return _single(args, ["objects"], keep_frames=args.keep_frames)


def cmd_text(args):
    return _single(args, ["text"], keep_frames=args.keep_frames)


def cmd_all(args):
    return _single(args, list(MODALITIES), keep_frames=args.keep_frames)


def cmd_batch(args):
    video_dir = Path(args.video_dir)
    videos = sorted(p for p in video_dir.iterdir()
                    if p.suffix.lower() in VIDEO_SUFFIXES)
    if not videos:
        print(f"no videos in {video_dir}", file=sys.stderr)
        return 2

    only = args.only.split(",") if args.only else list(MODALITIES)
    bad = [m for m in only if m not in MODALITIES]
    if bad:
        print(f"unknown modality: {', '.join(bad)}", file=sys.stderr)
        return 2

    _scaffold(args.data_root)
    models = {}
    ok = failed = 0
    for video_path in videos:
        vid = _video_id(video_path)
        print(f"\n{'=' * 60}\n{vid}")
        try:
            provision.place_video(args.data_root, video_path, vid,
                                  copy=args.copy_video)
            for m in only:
                _RUNNERS[m](args, video_path, vid, models)
            if not args.keep_frames:
                _drop_frames(args, vid)
            ok += 1
        except Exception:
            failed += 1
            traceback.print_exc()
            print(f"[fail] {vid}")

    print(f"\n{'=' * 60}\nbatch done: ok={ok} failed={failed} total={len(videos)}")
    return 1 if failed else 0


# --------------------------------------------------------------------------- #
# parser
# --------------------------------------------------------------------------- #

def build_parser():
    parser = argparse.ArgumentParser(prog="avra-extract", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", action="version",
                        version=f"avra-extract {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("frames", help="sample frames + write manifest.json")
    p.add_argument("video")
    p.add_argument("--fps", type=float, default=constants.SAMPLE_FPS)
    _add_common(p)
    p.set_defaults(func=cmd_frames)

    p = sub.add_parser("audio", help="BEATs SED -> <video_id>.npy")
    p.add_argument("video")
    p.add_argument("--checkpoint", help=f"BEATs checkpoint (or ${constants.ENV_BEATS_CHECKPOINT})")
    p.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    _add_common(p)
    p.set_defaults(func=cmd_audio)

    p = sub.add_parser("objects", help="YOLOE -> <video_id>_detections.json")
    p.add_argument("video")
    p.add_argument("--weights", help=f"YOLOE weights (or ${constants.ENV_YOLOE_WEIGHTS})")
    p.add_argument("--conf", type=float, default=constants.YOLOE_CONF)
    p.add_argument("--fps", type=float, default=constants.SAMPLE_FPS)
    p.add_argument("--keep-frames", action="store_true")
    _add_common(p)
    p.set_defaults(func=cmd_objects)

    p = sub.add_parser("text", help="PP-OCRv6 -> <video_id>_ocr.json")
    p.add_argument("video")
    p.add_argument("--min-score", type=float, default=constants.OCR_MIN_SCORE)
    p.add_argument("--min-text-length", type=int, default=constants.OCR_MIN_TEXT_LENGTH)
    p.add_argument("--fps", type=float, default=constants.SAMPLE_FPS)
    p.add_argument("--keep-frames", action="store_true")
    _add_common(p)
    p.set_defaults(func=cmd_text)

    for name, fn, helptext in [
        ("all", cmd_all, "frames + all three modalities for one video"),
        ("batch", cmd_batch, "run over every video in a directory"),
    ]:
        p = sub.add_parser(name, help=helptext)
        p.add_argument("video_dir" if name == "batch" else "video")
        p.add_argument("--checkpoint", help=f"BEATs checkpoint (or ${constants.ENV_BEATS_CHECKPOINT})")
        p.add_argument("--weights", help=f"YOLOE weights (or ${constants.ENV_YOLOE_WEIGHTS})")
        p.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
        p.add_argument("--conf", type=float, default=constants.YOLOE_CONF)
        p.add_argument("--min-score", type=float, default=constants.OCR_MIN_SCORE)
        p.add_argument("--min-text-length", type=int, default=constants.OCR_MIN_TEXT_LENGTH)
        p.add_argument("--fps", type=float, default=constants.SAMPLE_FPS)
        p.add_argument("--keep-frames", action="store_true")
        p.add_argument("--copy-video", action="store_true",
                       help="copy the source mp4 into data_root instead of symlinking")
        if name == "batch":
            p.add_argument("--only", help="comma-separated subset of: " + ",".join(MODALITIES))
        _add_common(p)
        p.set_defaults(func=fn)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
