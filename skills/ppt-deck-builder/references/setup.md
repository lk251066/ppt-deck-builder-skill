# Setup

## Requirements

- Python `3.9+`
- `bash`
- `requests`
- `python-pptx`

## Install

```bash
python3 -m pip install requests python-pptx
```

## Provider Selection

Provider resolution order:

1. slide `image_provider`
2. CLI `--provider`
3. plan `image_provider`
4. env `PPT_IMAGE_PROVIDER`
5. default `runninghub_g31`

Built-in providers:

- `runninghub_g31`
- `command`

## Environment

For RunningHub:

```bash
export PPT_IMAGE_PROVIDER="runninghub_g31"
export RUNNINGHUB_API_KEY="your_api_key"
```

For a local command adapter from the skill root:

```bash
export PPT_IMAGE_PROVIDER="command"
export PPT_IMAGE_PROVIDER_COMMAND="python3 scripts/provider_mock_png.py"
```

For OpenClaw-style command paths, use `{baseDir}` inside skill instructions or plan files.
The generator expands `{baseDir}` automatically inside provider options such as `command` or `cwd`.

## Quick Checks

Run these commands from the root of the `ppt-deck-builder` folder:

```bash
python3 --version
python3 -m pip show requests
python3 -m pip show python-pptx
bash scripts/check_env.sh
python3 scripts/generate_from_plan.py --help
python3 scripts/provider_mock_png.py --help
bash scripts/run_reference_pack.sh --help || true
```

## Recommended First Run

1. Build a small plan with short titles and fixed text lines.
2. Run a reference pack first.
3. Review text sharpness and card consistency.
4. Run the full batch only after the sample looks stable.
5. Use `run_full_deck.sh` if you need an end-to-end command that guarantees image generation runs before packaging.

If the provider is busy, lower sample resolution first and keep `max-workers=1`.
