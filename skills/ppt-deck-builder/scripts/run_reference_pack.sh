#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
  echo "Usage: run_reference_pack.sh <plan.json> <outdir> [resolution] [aspect_ratio] [end_slide] [extra args...]"
  echo "Default behavior: generate slides 1 through 3 with max-workers=1 for sample review."
  exit 0
fi

if [[ $# -lt 2 ]]; then
  echo "Usage: run_reference_pack.sh <plan.json> <outdir> [resolution] [aspect_ratio] [end_slide] [extra args...]"
  exit 1
fi

PLAN="$1"
OUTDIR="$2"
RESOLUTION="${3:-2k}"
ASPECT_RATIO="${4:-16:9}"
END_SLIDE="${5:-3}"
EXTRA_ARGS=()
if [[ $# -gt 5 ]]; then
  EXTRA_ARGS=("${@:6}")
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENERATOR="$SCRIPT_DIR/generate_from_plan.py"

if [[ ! -f "$GENERATOR" ]]; then
  echo "Generator script not found: $GENERATOR"
  exit 1
fi

python3 "$GENERATOR" \
  --plan "$PLAN" \
  --outdir "$OUTDIR" \
  --resolution "$RESOLUTION" \
  --aspect-ratio "$ASPECT_RATIO" \
  --max-workers 1 \
  --start-slide 1 \
  --end-slide "$END_SLIDE" \
  "${EXTRA_ARGS[@]}"
