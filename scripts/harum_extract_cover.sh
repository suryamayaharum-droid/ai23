#!/usr/bin/env bash
set -euo pipefail
SRC="$1"; OUT="$2"; OFFSET="${3:-4}"
ffmpeg -y -ss "$OFFSET" -i "$SRC" -frames:v 1 -vf "scale=1080:1350:force_original_aspect_ratio=increase,crop=1080:1350" -q:v 2 "$OUT"
test -s "$OUT"
