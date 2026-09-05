#!/usr/bin/env bash
# avra-extract text — see docs/USAGE.md
source "$(dirname -- "${BASH_SOURCE[0]}")/_common.sh"
avra_extract text "$@"
