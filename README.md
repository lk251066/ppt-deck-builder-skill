# PPT Deck Builder for OpenClaw

A portable PPT production skill for OpenClaw.

This repository keeps the actual skill source under `skills/` so it can be used as a clean skill source without project files, customer materials, or personal environment data.

## What This Skill Does

`ppt-deck-builder` is a reusable workflow for:

- turning notes, PDFs, spreadsheets, or old decks into a slide storyline
- writing page briefs and fixed-text slide prompts
- generating slide images with a replaceable image provider
- rerunning only failed or weak pages
- packaging the final slide images into a `.pptx`

It is optimized for image-based delivery decks where each slide is generated as a finished visual page and then packed into PowerPoint.

## Repository Layout

```text
skills/
  ppt-deck-builder/
    SKILL.md
    agents/
    assets/
    references/
    scripts/
```

## Install

Choose one of these patterns.

### Option 1: Copy into a workspace-local skills directory

```bash
git clone https://github.com/lk251066/ppt-deck-builder-openclaw-skill.git
mkdir -p <your-workspace>/skills
cp -R ppt-deck-builder-openclaw-skill/skills/ppt-deck-builder <your-workspace>/skills/
```

### Option 2: Copy into a shared local OpenClaw skills directory

```bash
git clone https://github.com/lk251066/ppt-deck-builder-openclaw-skill.git
mkdir -p ~/.openclaw/skills
cp -R ppt-deck-builder-openclaw-skill/skills/ppt-deck-builder ~/.openclaw/skills/
```

## Requirements

From `skills/ppt-deck-builder/` the workflow expects:

- `bash`
- `python3`
- `requests`
- `python-pptx`

Install Python packages if needed:

```bash
python3 -m pip install requests python-pptx
```

## Image Providers

The workflow supports provider selection instead of forcing a single image backend.

### Built-in providers

- `runninghub_g31`: ready-to-run default for RunningHub text-to-image generation
- `command`: generic adapter mode for custom image backends

### Provider selection order

1. slide-level `image_provider`
2. CLI `--provider`
3. plan-level `image_provider`
4. environment variable `PPT_IMAGE_PROVIDER`
5. default `runninghub_g31`

## Quick Start

Enter the skill directory:

```bash
cd skills/ppt-deck-builder
```

Run environment checks:

```bash
bash scripts/check_env.sh
```

### RunningHub example

```bash
export PPT_IMAGE_PROVIDER="runninghub_g31"
export RUNNINGHUB_API_KEY="your_api_key"
bash scripts/run_image_batch.sh plan.json output_dir
```

### Custom provider example

Use the generic `command` provider when OpenClaw or another agent should control the image backend.

```bash
export PPT_IMAGE_PROVIDER="command"
export PPT_IMAGE_PROVIDER_COMMAND="python3 scripts/provider_command_template.py"
bash scripts/run_image_batch.sh plan.json output_dir
```

The adapter contract is documented in:

- `skills/ppt-deck-builder/references/provider-adapters.md`

A local offline test adapter is included here:

- `skills/ppt-deck-builder/scripts/provider_mock_png.py`

## Typical Workflow

1. define audience, outcome, and page sequence
2. write one page brief per slide
3. convert the brief into a slide plan JSON
4. generate a small sample first
5. run the full batch
6. rerun only weak pages
7. QA the full image set
8. package images into a `.pptx`

## Key Files

- `skills/ppt-deck-builder/SKILL.md`: main skill instructions
- `skills/ppt-deck-builder/assets/page_brief_template.md`: page brief template
- `skills/ppt-deck-builder/assets/slide_plan_template.json`: slide plan template
- `skills/ppt-deck-builder/references/provider-adapters.md`: custom provider contract
- `skills/ppt-deck-builder/scripts/generate_from_plan.py`: main image generation entrypoint
- `skills/ppt-deck-builder/scripts/build_pptx_from_images.py`: pack slide images into PowerPoint

## Privacy

This repository is intentionally clean for reuse:

- no customer names
- no customer documents
- no local machine paths
- no API keys or personal tokens

## Notes

- This skill is designed for finished-image PPT workflows, not fully editable theme-heavy decks.
- OpenClaw-friendly `{baseDir}` usage is already included in the skill instructions.
- The `command` provider is the recommended extension point when you want OpenClaw to switch image backends without rewriting the PPT workflow.
