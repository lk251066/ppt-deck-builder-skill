---
name: ppt-deck-builder
description: Use when building or revising a PPT/演示文稿 in a shareable, self-contained workflow folder, especially when the job spans storyline design, page briefs, chart pages, fixed-text image prompts, provider-selectable slide image generation, page repair, and PPTX packaging without depending on repo files outside this skill folder.
version: 0.1.0
metadata: {"openclaw":{"requires":{"bins":["bash","python3"]}}}
---

# PPT Deck Builder

This is a portable, single-folder PPT generation skill.
Everything needed by the workflow lives inside this skill folder: process guidance, references, templates, helper scripts, and packaging tools.

## Use When

- The user wants a reusable PPT production workflow that can be copied to another machine or repo.
- The user wants to build a new deck from notes, PDFs, spreadsheets, or an existing deck.
- The user wants to generate slide images with fixed text and package them into a `.pptx`.
- The user wants one skill folder instead of multiple linked skills.
- The user wants the image provider to stay replaceable so OpenClaw or another agent can switch providers later.

## Do Not Use When

- The user only wants one sentence rewritten.
- The user only wants speaking advice, with no deck production.
- The user needs fully editable theme engineering beyond this workflow's image-based packaging path.

## Setup

Read `references/setup.md` before first use.
This workflow expects:
- `bash`
- `python3`
- `requests`
- `python-pptx`
- an image provider selected by CLI, plan file, or environment variable
- provider-specific environment variables only for the chosen provider

OpenClaw-safe paths use `{baseDir}`.
Plain shell usage still works from the root of this skill folder with `bash scripts/...`.

## Workflow Decision Tree

1. If the input is messy or vague, start with story design.
2. If the page sequence exists, move to page briefs and layout planning.
3. If charts or metrics drive the message, design data pages before image prompts.
4. If the deck is image-based, generate a small sample first.
5. If a page fails quality checks, rerun only that page.
6. Package only after the full image set is approved.

## Core Workflow

### 1. Build the story

- Identify audience, objective, and expected action.
- Choose a storyline pattern.
- Reduce the deck to one message per page.
- Draft a page list with title, role, and key takeaway.

Read when needed:
- `references/story-patterns.md`
- `references/audience-and-goals.md`

### 2. Turn the story into pages

- Assign a page type to each page.
- Keep a clear reading order.
- Use cards, comparison, process, timeline, chart, or conclusion patterns based on page job.
- Avoid dense page structures before the narrative is stable.

Read when needed:
- `references/page-types.md`
- `references/layout-patterns.md`

### 3. Design data pages

- Use charts only when they clarify the decision.
- Pick the chart type based on comparison, trend, composition, funnel, progress, or anomaly logic.
- Give each data page one visible takeaway.

Read when needed:
- `references/chart-selection.md`
- `references/data-slide-patterns.md`

### 4. Build prompt plans for image-based decks

- Work one page at a time.
- Fix the exact text lines allowed on the page.
- Map each text line to one region.
- Forbid extra text, random labels, wrong symbols, and unwanted numeric markers if needed.
- Keep provider choice separate from page story and layout decisions.

Use these local resources:
- `references/prompt-rules.md`
- `references/provider-adapters.md`
- `assets/slide_plan_template.json`
- `assets/page_brief_template.md`

### 5. Generate slide images

The image provider can be selected in this order:
1. Slide-level `image_provider`
2. CLI `--provider`
3. Plan-level `image_provider`
4. Environment variable `PPT_IMAGE_PROVIDER`
5. Default `runninghub_g31`

Built-in providers:
- `runninghub_g31`
- `command`

`command` is the generic escape hatch.
It lets OpenClaw or another agent replace the image backend without changing the main workflow script.

OpenClaw-safe batch generation:
```bash
bash {baseDir}/scripts/run_image_batch.sh plan.json output_dir
```

Plain shell batch generation from the skill root:
```bash
bash scripts/run_image_batch.sh plan.json output_dir
```

OpenClaw-safe single-page rerun:
```bash
bash {baseDir}/scripts/rerun_single_page.sh plan.json output_dir 8
```

### 6. Run QA and package

Check every page for wording accuracy, text sharpness, hierarchy, and layout noise.
When approved, package the deck:

OpenClaw-safe:
```bash
bash {baseDir}/scripts/package_image_deck.sh output_dir deck.pptx
```

Plain shell from the skill root:
```bash
bash scripts/package_image_deck.sh output_dir deck.pptx
```

Read when needed:
- `references/qa-checklist.md`

## Local Tools In This Folder

- `scripts/generate_from_plan.py`
- `scripts/build_pptx_from_images.py`
- `scripts/run_image_batch.sh`
- `scripts/rerun_single_page.sh`
- `scripts/package_image_deck.sh`
- `scripts/check_env.sh`
- `scripts/provider_command_template.py`
- `scripts/provider_mock_png.py`

## Guardrails

- One page should do one job.
- Prefer fewer, larger text groups in image-based pages.
- Do not hide story problems with visual polish.
- If text quality drops, simplify the page and rerun.
- Keep provider logic replaceable and isolated from the story and layout logic.
- Keep this folder self-contained when sharing it.
