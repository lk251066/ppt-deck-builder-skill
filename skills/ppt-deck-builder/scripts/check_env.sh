#!/usr/bin/env bash
set -euo pipefail

python3 --version
python3 - <<'PY'
mods=[('requests','requests'),('pptx','python-pptx')]
missing=[]
for mod,pkg in mods:
    try:
        __import__(mod)
        print(f'OK {pkg}')
    except Exception:
        missing.append(pkg)
if missing:
    print('Missing packages:', ', '.join(missing))
    raise SystemExit(1)
PY

PROVIDER="${PPT_IMAGE_PROVIDER:-grsai}"
echo "PPT_IMAGE_PROVIDER=$PROVIDER"

if [[ -n "${PPT_IMAGE_PROVIDER_COMMAND:-}" ]]; then
  echo "PPT_IMAGE_PROVIDER_COMMAND is set"
else
  echo "PPT_IMAGE_PROVIDER_COMMAND is not set"
fi

case "$PROVIDER" in
  runninghub|runninghub_g31)
    if [[ -n "${RUNNINGHUB_API_KEY:-}" ]]; then
      echo "RUNNINGHUB_API_KEY is set"
    else
      echo "RUNNINGHUB_API_KEY is not set"
    fi
    ;;
  grsai|grsai_draw|grsai_gpt_image)
    if [[ -n "${GRSAI_API_KEY:-}" ]]; then
      echo "GRSAI_API_KEY is set"
    else
      echo "GRSAI_API_KEY is not set"
    fi
    ;;
  command|custom-command)
    echo "Command provider selected; verify the adapter command path is correct"
    ;;
  *)
    echo "Custom provider selected; verify provider-specific settings manually"
    ;;
esac
