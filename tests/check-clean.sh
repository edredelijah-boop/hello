#!/usr/bin/env bash
# Clean-room scan: fail if a private path or a credential-shaped string is
# committed, or if a runtime artifact escaped .gitignore.
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
fail=0

if grep -RInE '/nfs/|/nobackup/|gigantamax|/u/[a-z]+/|cookies\.txt|AIza[0-9A-Za-z_-]{30,}|ya29\.[0-9A-Za-z_-]+' \
  --exclude-dir=.git --exclude-dir=.venv --exclude-dir=frames --exclude-dir=data_root \
  --exclude=check-clean.sh "$repo_root"; then
  printf 'private path or credential-shaped string found\n' >&2
  fail=1
fi

if find "$repo_root" \
  \( -path "$repo_root/.git" -o -path "$repo_root/frames" -o -path "$repo_root/data_root" \) -prune -o \
  -type f \( -name '*.pt' -o -name '*.npy' -o -name '*.mp4' -o -name '*.log' \) -print | grep -q .; then
  printf 'runtime artifact committed outside an ignored dir\n' >&2
  fail=1
fi

[ "$fail" -eq 0 ] && printf 'CLEAN_SCAN_PASS\n'
exit "$fail"
