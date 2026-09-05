#!/usr/bin/env bash
# Batch over a directory of videos. Resumable (finished artifacts are skipped),
# skip-on-failure, tees a full log. Extra flags pass straight through.
#   ./scripts/run-batch.sh /path/to/videos --data-root /path/to/data_root
source "$(dirname -- "${BASH_SOURCE[0]}")/_common.sh"
[ "$#" -ge 1 ] || { echo "usage: $0 VIDEO_DIR [avra-extract batch flags...]" >&2; exit 2; }
log_dir="${AVRA_LOG_DIR:-$repo_root/logs}"
mkdir -p "$log_dir"
log="$log_dir/batch_$(date -u +%Y%m%dT%H%M%SZ).log"
echo "logging to $log"
set -o pipefail
avra_extract batch "$@" 2>&1 | tee "$log"
