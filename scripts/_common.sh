# Sourced by the wrapper scripts. Resolves how to invoke the package:
# the installed console script if present, else `python -m` with ./src on path.
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

if command -v avra-extract >/dev/null 2>&1; then
  avra_extract() { avra-extract "$@"; }
else
  avra_extract() { PYTHONPATH="$repo_root/src${PYTHONPATH:+:$PYTHONPATH}" python3 -m avra_metadata_extractor "$@"; }
fi
