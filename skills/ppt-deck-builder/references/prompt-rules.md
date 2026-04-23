# Prompt Rules

## Strong Defaults

- One page, one prompt.
- Treat the slide as a final text-and-background PPT page, not as a background image.
- Start with page identity and page type before style words.
- Put exact allowed text lines at the end.
- Tell the model each line appears once only.
- Prefer fewer, larger text groups by default.
- If the provider is `grsai` and the model is `gpt-image-2`, you may relax this default after a stable reference pack and intentionally test denser text layouts.
- Give the page a composition job, not just a style direction.

## Page Identity First

- Start with one identity sentence such as `Generate a 16:9 Chinese client-facing PPT page, not a poster, not a training handout, not a background-only image.`
- Name the page type directly: path, matrix, comparison, rollout, dashboard, diagnostic, or conclusion.
- If the page should look formal and client-facing, say `client-facing business presentation page` or `consulting-style proposal slide`.
- If the page should feel high-end, use structure words first and mood words second.

## Prompt Order

Use this order unless a provider needs a stricter format:
1. Page identity
2. Page type and composition
3. Reading path
4. Exact text rules
5. Deck style and color direction
6. Negative rules

## Style Preset First

- Choose one deck-level style preset before writing page prompts.
- Keep the preset name stable across the whole deck unless one page truly needs an exception.
- Good default presets are `dark_blue_business`, `light_consulting`, and `whiteboard_handdrawn`.
- If the user wants a custom style, write one short style brief first, then apply it to all page prompts.
- Read `references/style-presets.md` when the user asks for a named style or strong visual direction.

## Before You Write Prompts

- Shorten the title first.
- Shorten card titles before shortening body text.
- Remove repeated ideas.
- Remove source-attribution lines such as `基于某某内容简化` unless the user explicitly wants them kept.
- Decide which lines must stay visible on the page.
- Decide which region owns each sentence before adding density.

## Text Budgets

- Keep visible text as low as the page allows.
- Prefer one-line titles.
- Keep card titles short and stable.
- If a page is still crowded, split the page instead of shrinking everything.
- High-information pages can carry more text, but only when each sentence has a fixed region and large enough text area.
- Do not increase information density by repeating the same idea in multiple cards, strips, or footers.
- Prefer `title + 4-6 modules + 1 summary strip` before trying long paragraph layouts.
- For `grsai` with `gpt-image-2`, a validated dense-mode page may extend this to `title + 6-10 modules + 1 summary strip`.
- For `grsai` with `gpt-image-2`, another stable dense pattern is `title + 3-5 explanation panels` where each panel carries a longer sentence.

## Reading Path And Region Binding

- State how the audience should read the page: `top to bottom`, `left to right`, or `center first then surrounding labels`.
- Give each sentence one home region.
- Keep region names simple and concrete: `title zone`, `left conclusion card`, `center path nodes`, `bottom summary strip`.
- If one block should dominate, say so explicitly.
- For dense pages, enlarge the explanation region instead of duplicating text inside the main diagram.
- If the page contains both a page title and an inner bubble or panel title, make them distinct in wording and role instead of near-duplicates.

## Dense Page Rules

- Preserve the page's native structure first: a path page stays a path page, a matrix page stays a matrix page, and a comparison page stays a comparison page.
- Do not force one universal card template across every page in the deck.
- Keep the deck's primary visual standard first.
- Only switch to a light background with dark text when repeated or blurry dense text is not resolved by structure and text-region repair.
- Give each long sentence one dedicated region.
- Use one summary strip at most.
- If a page needs more explanation, expand one lower explanation area instead of duplicating copy inside the main diagram.
- For `grsai` with `gpt-image-2`, dense-page stress tests may use either more small modules or longer explanation sentences, but each sentence still needs one clear home region.
- Even in dense mode, avoid tiny floating labels, crowded sidebars, and decorative micro-copy that do not belong to a named module.

## Chinese Text Guardrails

- Make text sharp and readable.
- Forbid extra labels, fake text, and decorative English.
- Forbid repeated words, wrong numbers, wrong symbols, and random markers when needed.
- If the page contains `AI`, tell the model not to rewrite or replace it.
- Prefer short Chinese noun phrases over spoken full sentences for card titles.
- Avoid tiny interface labels, tiny chart tags, and decorative micro-copy.
- If the page must carry more Chinese text, enlarge text panels before shrinking font size in the prompt.

## Business Tone Rules

- Prefer `business`, `proposal`, `boardroom`, `client-facing`, `consulting-style`, and `presentation-ready` over vague words such as `epic` or `stunning`.
- For blue enterprise decks, prefer dark glass cards over white cards.
- Use `deep navy`, `cobalt blue`, `ice blue`, and `titanium silver accents` for a stable blue-tech palette.
- Ask for `light sci-fi` or `subtle futuristic atmosphere`, not cyberpunk overload.
- Design quality should come from order, focus, spacing, and hierarchy rather than from more glowing effects.

## Whiteboard Hand-Drawn Rules

- Use this preset only when the user explicitly wants whiteboard, founder-board, board sketch, hand-drawn training, or similar language.
- State that the whiteboard fills the entire 16:9 frame and all four borders remain visible.
- Forbid room background, desk, projector screen, office wall, and classroom environment.
- Ask for elegant Chinese hard-pen handwriting, not printed font and not thick marker block text.
- Ask for hand-drawn cartoon illustration with black outline and marker color fill.
- If comic people are used, define whether they are supporting, medium, or dominant. Default to supporting only for client-facing decks.
- If the page includes a mascot, state the mascot type explicitly and keep it stable across all pages.
- Prefer 3-6 large handwritten text groups, not many tiny labels.
- Forbid extra handwritten notes, replacement titles, or freestyle annotations unless they are part of the approved text.
- If the model keeps inventing extra notes, explicitly say `the page may only contain the approved text lines`.
- If the user wants hand-drawn explanation without a visible board frame, do not force this preset; switch to a `custom` borderless hand-drawn brief with pure white canvas and no border.

## Poster Avoidance Rules

- Say `not a poster` when the page keeps drifting into hero-shot compositions.
- Forbid giant foreground characters, dramatic cinematic perspective, and huge glowing objects behind the title.
- Forbid game UI panels, fake dashboards, fake app screenshots, and busy HUD overlays unless the page truly needs that structure.
- Tell the model that the background supports the information and must not overpower the text.

## Style Anchor Rules

- Generate a small reference pack before the full batch.
- If one page best captures the deck tone, mark it as the style anchor.
- If the provider supports reference images, reuse the approved style anchor image for later pages.
- If the provider does not support reference images, restate the approved style anchor in text with color, material, lighting, and card rules.
- Do not sacrifice page-specific composition just to force visual sameness.

## Text Guardrails

- Tell the model when a footer, strip, or bottom explanation must appear once only.
- If the page is text-heavy, explicitly say `this is a text-and-background integrated PPT page, not a background-only graphic`.
- Use a fixed block such as `Only show the following text. Each line appears once only.`
- Forbid extra English, extra numbers, extra percent signs, watermarks, QR codes, and logos unless required.
- For dense business pages, explicitly mark light-background readability mode as a fallback only, not as the default style standard.
- If the page title must stay exact, explicitly say it cannot be replaced, shortened, or rewritten.

## Composition Guidance

- Name the page structure directly: path, matrix, 2x2 cards, comparison, rollout, or conclusion.
- Tell the model where the title zone sits.
- Tell the model how many main blocks exist and how they are arranged.
- If one block should dominate, say so explicitly.
- For high-information pages, describe which sentences belong in which regions.
- If the page already has a strong structure, add explanation text around that structure instead of replacing it.
- For `grsai` with `gpt-image-2`, denser structures can be tested deliberately after sample validation, but only by expanding named modules or named explanation panels.

## Sample-First Rules

- Run a small reference pack before the full batch.
- Check title wrapping, card consistency, and text sharpness first.
- Check whether the page reads like a real client-facing slide.
- Do not scale up a weak prompt set.

## Repair Rules

- Repeated text -> assign one line to one region.
- Blurry text -> enlarge text blocks and reduce glow, noise, and tiny decorations.
- Random labels -> replace chart-like shapes with abstract graphics.
- Unwanted numeric markers -> explicitly forbid digits and percent signs.
- White paper cards in a dark deck -> explicitly require dark blue glass cards.
- Weak business tone -> reduce sci-fi effects and strengthen layout order.
- Repeated footer or strip text -> state that the strip appears once only and remove any duplicate summary cards.
- Dense text still blurry -> keep the original brand direction if possible, but as a fallback you may switch to a light background, dark text, fewer glow effects, and fewer visible regions.
- Page became generic after adding text -> restore the original page structure and only add one explanation area.
- Page looks pretty but not like a slide -> strengthen page identity, page type, and reading path before changing color language.
- Whiteboard page added extra doodles or wrong mascot -> lock approved text harder, reduce optional decoration, and restate mascot type explicitly.
- Whiteboard page replaced the main title -> restate the exact title and explicitly forbid replacement, summary, or alternate headings.
- Whiteboard page duplicated a heading in both the page title and a panel title -> rewrite the labels so each heading appears once with one distinct role, then rerun only that page.

## Provider Recovery

- Busy or queue failures -> retry smaller batches.
- Start with `max-workers=1` for unstable providers.
- Lower sample resolution before changing the story.
- Repair one page at a time after the reference pack.

## Prompt Skeleton

```text
Generate a 16:9 Chinese client-facing PPT page, not a poster, not a background-only image.
Page type: [path / matrix / comparison / rollout / dashboard].
Reading path: [left to right / top to bottom / center first then four surrounding cards].
Composition: [title zone + center process band + bottom summary strip].
Text rule: only show the following text, each line once only, do not add extra English, numbers, labels, or tiny UI copy.
Style: business, presentation-ready, deep navy and cobalt blue, subtle futuristic atmosphere, dark glass cards, clear hierarchy.
Negative rules: no poster look, no giant hero figure, no fake dashboard clutter, no repeated text, no blurry text.
```

## Whiteboard Prompt Skeleton

```text
Generate a 16:9 Chinese whiteboard-style PPT page, not a poster, not a classroom photo, not a background-only image.
Page type: [comparison / matrix / path / chapter page].
Reading path: [top to bottom / left to right].
Composition: [top title zone + center structured modules + bottom summary area].
Text rule: only show the approved text lines, each line once only, do not replace the title, do not add extra handwritten notes, labels, or room elements.
Style: full-frame whiteboard, all four metallic borders visible, elegant Chinese hard-pen handwriting, hand-drawn colored marker illustrations, red and black annotation marks, stable mascot policy if required.
Negative rules: no office background, no projector screen, no printed font, no extra doodles, no wrong mascot, no repeated text, no blurry text.
```
