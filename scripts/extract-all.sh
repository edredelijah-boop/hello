#!/usr/bin/env bash
# frames + audio + objects + text for one video — see docs/USAGE.md
source "$(dirname -- "${BASH_SOURCE[0]}")/_common.sh"
avra_extract all "$@"
