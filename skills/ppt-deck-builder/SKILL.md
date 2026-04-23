---
name: ppt-deck-builder
description: Use when building or revising a PPT/演示文稿 in a portable, self-contained workflow folder, especially when the job spans storyline design, page briefs, page-level text compression, fixed-text image prompts, style-selectable slide image generation, sample-pack generation, page repair, and PPTX packaging without depending on repo files outside this skill folder.
version: 0.4.0
metadata:
  openclaw:
    requires:
      bins:
        - bash
        - python3
---

# PPT Deck Builder

This is a portable, single-folder PPT generation skill.
Everything needed by the workflow lives inside this skill folder: process guidance, references, templates, helper scripts, and packaging tools.

## Use When

- The user wants a reusable PPT production workflow that can be copied to another machine or repo.
- The user wants to build a new deck from notes, PDFs, spreadsheets, or an existing deck.
- The user wants to generate slide images with fixed text and package them into a `.pptx`.
- The user wants one skill folder instead of multiple linked skills.
- The user wants the image provider to stay replaceable so another agent or toolchain can switch providers later.
- The user wants to choose a visual direction such as dark blue business, light consulting, or whiteboard hand-drawn before generation.

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

Before first generation:
- Ask whether a GrsAI API key is available for the default path.
- Default model is `gpt-image-2`.
- If no provider is specified, stay on `grsai`.
- If the user is simplifying an existing deck and the new page count, density, or tone are not obvious, confirm the outline before generation.

Portable skill paths use `{baseDir}`.
Plain shell usage still works from the root of this skill folder with `bash scripts/...`.

## Workflow Decision Tree

1. If the input is messy or vague, start with story design.
2. If the user is simplifying an existing deck, confirm the reduced outline first when page count or tone choices have non-obvious consequences.
3. Choose one deck-level style preset or define a custom style direction before prompt writing.
4. If the page sequence exists, define the page type, page identity sentence, and reading path before prompt writing.
5. Compress page titles and visible text before adding style language.
6. If the deck is image-based, generate a small reference pack before the full batch.
7. If one page sets the desired visual standard, treat it as a style anchor for later pages when the provider supports reference images.
8. If text looks unstable, simplify the page before adding more visual detail.
9. After full-batch generation, build review contact sheets and inspect the whole deck.
10. If any page has text, layout, tone, or style-drift issues, rerun only that page and review again.
11. Package only after the full image set is reviewed and approved.

## Core Workflow

### 1. Define the deck job

- Identify audience, objective, and expected action.
- Choose a storyline pattern.
- Choose a deck-level style preset early. Default to a business presentation style unless the user explicitly wants a stronger style such as whiteboard hand-drawn.
- Reduce the deck to one message per page.
- Draft a page list with title, role, and key takeaway.
- If the deck is being simplified from an existing source deck, confirm the reduced page list before generation when the simplification direction is not obvious.

Read when needed:
- `references/story-patterns.md`
- `references/audience-and-goals.md`
- `references/style-presets.md`
- `references/workflow-playbook.md`

### 2. Build the page map

- Assign a page type to each page.
- Write one page identity sentence for each page such as `This is a Chinese client-facing PPT path page, not a poster.`
- Lock the deck style at the same time. Put style exceptions on the page only when a page genuinely needs to break the deck standard.
- Keep a clear reading order.
- Choose a visual job for the page: decision, diagnosis, path, matrix, rollout, results, or conclusion.
- Avoid dense structures before the narrative is stable.
- If the user wants a text-heavy image page, define the text regions before expanding the copy.

Read when needed:
- `references/page-types.md`
- `references/layout-patterns.md`
- `references/style-presets.md`
- `references/workflow-playbook.md`

### 3. Compress page language

- Shorten titles before writing prompts.
- Keep card titles short and stable.
- Prefer noun phrases over spoken-sentence titles.
- Remove repeated text and low-value labels.
- Decide what absolutely must appear as visible text.
- If the user wants higher information density, first decide where each sentence belongs before adding more text.
- Do not raise information density by repeating the same idea in both the diagram area and the footer area.
- Treat the page as an integrated text-and-background PPT page, not as a background image that will be fixed later.
- For Chinese image pages, prefer fewer but larger text groups over many scattered micro-labels.
- For `grsai` with `gpt-image-2`, once a reference pack proves the layout is stable, you may intentionally relax the default density limit and test either more modules or longer explanation sentences.
- For `grsai` with `gpt-image-2`, dense-page test patterns can include `title + 6-10 small modules + 1 conclusion strip` or `title + 3-5 longer explanation panels`.
- For whiteboard-style pages, reduce visible text earlier by default and prefer 3-6 large handwritten groups instead of many tiny labels, unless the chosen provider and model have already proven they can carry denser handwritten text.

Use these local resources:
- `assets/page_brief_template.md`
- `references/prompt-rules.md`
- `references/workflow-playbook.md`

### 4. Build prompt-ready page plans

- Work one page at a time.
- Start each prompt with page identity and page type before style words.
- Carry the chosen `style_preset` into each page plan. Only use page-level style overrides when the deck needs a controlled exception.
- Fix the exact text lines allowed on the page.
- Map each text line to one region.
- State the reading path directly.
- Give each page a clear composition, not just a generic style.
- Keep provider choice separate from page story and layout decisions.
- Preserve the page's native structure when adding more text. A path page should stay a path page, a matrix page should stay a matrix page, and a comparison page should stay a comparison page.
- Keep the deck's primary business visual standard first.
- Use a light consulting-style layout with dark text only as a fallback when dense text remains blurry or repetitive after prompt repair.
- When a model supports richer text rendering, still avoid long paragraph blocks until a reference pack proves the layout is stable.
- For `grsai` with `gpt-image-2`, a stable reference pack can unlock denser prompt plans with more visible modules or longer explanation lines than the default guardrails allow.
- If the chosen style is `whiteboard_handdrawn`, explicitly lock the whiteboard borders, zero room background, handwritten Chinese, hand-drawn illustration behavior, and mascot policy if any.
- If the user wants hand-drawn explanation without a physical board frame, switch to a `custom` borderless hand-drawn style brief instead of forcing `whiteboard_handdrawn`.
- If the chosen style uses comic people or a mascot, define whether they are supporting, medium, or dominant. Default to supporting only for client-facing decks.
- If a page contains a title plus a bubble title or panel title, make those labels distinct instead of semantically duplicated.
- Do not keep source-attribution lines such as `基于某某内容简化` unless the user explicitly wants them visible.

Use these local resources:
- `references/prompt-rules.md`
- `references/provider-adapters.md`
- `references/style-presets.md`
- `assets/slide_plan_template.json`
- `assets/page_brief_template.md`

### 5. Generate a reference pack first

Use a small sample to validate:
- text sharpness
- card consistency
- title wrapping
- reading order
- overall business tone
- style fidelity to the selected preset
- dense-page readability
- no repeated footer or summary text
- whether the page reads like a client-facing slide instead of a poster or training handout
- whether one approved page can act as a style anchor for later pages

Portable `{baseDir}` reference pack:
```bash
bash {baseDir}/scripts/run_reference_pack.sh plan.json output_dir
```

Plain shell from the skill root:
```bash
bash scripts/run_reference_pack.sh plan.json output_dir
```

### 6. Generate the full batch

Important:
- Do not stop after writing the plan file.
- Do not package a deck before slide images exist.
- If the user asked to actually generate a PPT, the workflow is not complete until image generation has run, the generated pages have been reviewed, and the deck has been packaged.

The image provider can be selected in this order:
1. Slide-level `image_provider`
2. CLI `--provider`
3. Plan-level `image_provider`
4. Environment variable `PPT_IMAGE_PROVIDER`
5. Default `grsai`

Notes:
- The built-in `runninghub_g31` adapter targets the RunningHub `rhart-image-n-g31-flash/text-to-image` path by default.
- The built-in `grsai` adapter targets the GrsAI draw API and uses `gpt-image-2` by default while keeping callback and polling details inside the provider layer.
- If the backend should use reference images, image editing, or multi-image style anchoring, switch to `command` and let the host agent own that adapter logic.
- If the user wants strong cross-page style continuation such as a whiteboard course deck, prefer a sample-first workflow and treat one approved page as the style anchor for later reruns.

Built-in providers:
- `grsai`
- `runninghub_g31`
- `command`

`command` is the generic escape hatch.
It lets another agent or toolchain replace the image backend without changing the main workflow script.

Portable `{baseDir}` full batch:
```bash
bash {baseDir}/scripts/run_image_batch.sh plan.json output_dir
```

Plain shell from the skill root:
```bash
bash scripts/run_image_batch.sh plan.json output_dir
```

Portable `{baseDir}` end-to-end generate + package:
```bash
bash {baseDir}/scripts/run_full_deck.sh plan.json output_dir deck.pptx
```

Plain shell from the skill root:
```bash
bash scripts/run_full_deck.sh plan.json output_dir deck.pptx
```

Portable `{baseDir}` single-page rerun:
```bash
bash {baseDir}/scripts/rerun_single_page.sh plan.json output_dir 8
```

### 7. Review the generated deck, then package

Check every page for wording accuracy, text sharpness, hierarchy, layout noise, repeated text, and client-facing business tone.
Do not treat generation success as delivery success.
Build review contact sheets, inspect the whole deck, rerun only the bad pages, and package only after the corrected image set is approved.

Portable `{baseDir}` contact sheet review:
```bash
python3 {baseDir}/scripts/build_contact_sheet.py output_dir
```

Plain shell from the skill root:
```bash
python3 scripts/build_contact_sheet.py output_dir
```

Portable `{baseDir}` single-page repair:
```bash
bash {baseDir}/scripts/rerun_single_page.sh plan.json output_dir 8
```

Portable `{baseDir}` packaging after review:
```bash
bash {baseDir}/scripts/package_image_deck.sh output_dir deck.pptx plan.json
```

Plain shell from the skill root:
```bash
bash scripts/package_image_deck.sh output_dir deck.pptx plan.json
```

Read when needed:
- `references/qa-checklist.md`

## Failure Recovery

- If the provider returns busy or queue-related failures, rerun a smaller sample with `max-workers=1`.
- If text quality drops, simplify the page, shorten titles, and rerun only that page.
- If the backend should change, switch to `command` instead of rewriting the deck workflow.
- If a page keeps failing, repair the story or prompt first, not the packaging step.
- If a page looks stylish but not presentation-ready, strengthen page identity, reading path, and text-region mapping before changing colors or effects.
- If a whiteboard-style page starts adding the wrong mascot, wrong title, or extra handwritten notes, tighten the exact text list and explicitly forbid replacement or summary text before rerunning that page.
- If a whiteboard-style page repeats a title in a second panel or strip, rewrite the page so each heading has one distinct role and one distinct wording before rerunning.

## Local Tools In This Folder

- `scripts/generate_from_plan.py`
- `scripts/build_pptx_from_images.py`
- `scripts/run_reference_pack.sh`
- `scripts/run_image_batch.sh`
- `scripts/run_full_deck.sh`
- `scripts/rerun_single_page.sh`
- `scripts/package_image_deck.sh`
- `scripts/build_contact_sheet.py`
- `scripts/check_env.sh`
- `scripts/provider_command_template.py`
- `scripts/provider_mock_png.py`

## Guardrails

- One page should do one job.
- Prefer fewer, larger text groups in image-based pages.
- Prefer fewer, larger text groups in image-based pages by default.
- If the provider is `grsai` and the model is `gpt-image-2`, you may deliberately push text density after sample validation, but keep each sentence bound to one region and avoid floating micro-label clutter.
- Shorten titles before prompting; do not hope the model will solve crowded copy.
- Give each page a composition job, not just a style direction.
- Define page identity and reading path before adding visual styling.
- Treat image pages as final text-and-background slides, not as background art to be fixed later.
- Approve a small reference pack before full-batch generation.
- Review the full generated deck before final delivery.
- Do not treat plan writing as deck generation.
- Do not package before validating that the expected slide images exist.
- Do not hide story problems with visual polish.
- Keep provider logic replaceable and isolated from the story and layout logic.
- Keep this folder self-contained when sharing it.
