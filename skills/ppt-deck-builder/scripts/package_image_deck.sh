#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
  echo "Usage: package_image_deck.sh <images_dir> <output.pptx> [plan.json]"
  echo "If plan.json is provided, the script validates that all expected slide images exist first."
  exit 0
fi

if [[ $# -lt 2 ]]; then
  echo "Usage: package_image_deck.sh <images_dir> <output.pptx> [plan.json]"
  exit 1
fi

INDIR="$1"
OUTFILE="$2"
PLAN="${3:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGER="$SCRIPT_DIR/build_pptx_from_images.py"
VALIDATOR="$SCRIPT_DIR/validate_generated_deck.py"

if [[ ! -f "$PACKAGER" ]]; then
  echo "Packager script not found: $PACKAGER"
  exit 1
fi

if [[ -n "$PLAN" ]]; then
  if [[ ! -f "$VALIDATOR" ]]; then
    echo "Validator script not found: $VALIDATOR"
    exit 1
  fi
  python3 "$VALIDATOR" --plan "$PLAN" --indir "$INDIR"
fi

python3 "$PACKAGER" --indir "$INDIR" --out "$OUTFILE"
