#!/usr/bin/env bash
# Make a self-contained synthetic video for the end-to-end smoke test.
#   tests/create-fixture.sh FIXTURE_ROOT
# Writes FIXTURE_ROOT/videos/Synthetic_Red.mp4 (4 s, red frame, 440 Hz tone).
set -euo pipefail

[ "$#" -eq 1 ] || { printf 'Usage: %s FIXTURE_ROOT\n' "$0" >&2; exit 2; }
fixture_root="$1"
video_dir="$fixture_root/videos"
mkdir -p "$video_dir"

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i 'color=c=red:s=320x240:r=10:d=4' \
  -f lavfi -i 'sine=frequency=440:sample_rate=16000:duration=4' \
  -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac \
  "$video_dir/Synthetic_Red.mp4"

printf 'fixture=%s\n' "$video_dir/Synthetic_Red.mp4"
