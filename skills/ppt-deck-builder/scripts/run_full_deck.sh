#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
  echo "Usage: run_full_deck.sh <plan.json> <outdir> <output.pptx> [resolution] [aspect_ratio] [max_workers] [extra args...]"
  echo "This script runs image generation, builds review contact sheets, and then packages."
  echo "Tip: run run_reference_pack.sh first if the plan or provider is new, and review the generated contact sheets before final delivery."
  exit 0
fi

if [[ $# -lt 3 ]]; then
  echo "Usage: run_full_deck.sh <plan.json> <outdir> <output.pptx> [resolution] [aspect_ratio] [max_workers] [extra args...]"
  exit 1
fi

PLAN="$1"
OUTDIR="$2"
OUTFILE="$3"
RESOLUTION="${4:-4k}"
ASPECT_RATIO="${5:-16:9}"
MAX_WORKERS="${6:-3}"
EXTRA_ARGS=()
if [[ $# -gt 6 ]]; then
  EXTRA_ARGS=("${@:7}")
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$SCRIPT_DIR/run_image_batch.sh" \
  "$PLAN" \
  "$OUTDIR" \
  "$RESOLUTION" \
  "$ASPECT_RATIO" \
  "$MAX_WORKERS" \
  "${EXTRA_ARGS[@]}"

if [[ -f "$SCRIPT_DIR/build_contact_sheet.py" ]]; then
  python3 "$SCRIPT_DIR/build_contact_sheet.py" "$OUTDIR" || true
  echo "Review contact sheets under $OUTDIR/qa before final client delivery."
fi

bash "$SCRIPT_DIR/package_image_deck.sh" "$OUTDIR" "$OUTFILE" "$PLAN"
