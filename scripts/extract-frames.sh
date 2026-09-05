#!/usr/bin/env bash
# avra-extract frames — see docs/USAGE.md
source "$(dirname -- "${BASH_SOURCE[0]}")/_common.sh"
avra_extract frames "$@"
