# Workflow Playbook

## Goal

Keep the skill portable and provider-agnostic while making the deck workflow stable enough for client-facing output.

## Default Sequence

1. Define audience, objective, and expected action.
2. If the job is a simplification of an existing deck, confirm the reduced outline when page count or tone choices are not obvious.
3. Choose one deck-level style preset.
4. Build the page sequence.
5. Lock page type, page identity sentence, and reading path for each page.
6. Shorten page titles and visible text.
7. Pick one clear composition per page.
8. Create prompt-ready plan entries.
9. Generate a small reference pack.
10. Approve one style anchor page if needed.
11. Run the full batch.
12. Build deck-level review contact sheets.
13. Review every generated page.
14. Rerun only the bad pages.
15. Review the repaired pages again.
16. Package the approved image set.

## Style Preset Rules

- Use one deck-level `style_preset` unless there is a clear reason to break the visual standard.
- Treat style choice as an early planning decision, not as decoration added at the end.
- The default preset should remain business-safe unless the user explicitly asks for a stronger style.
- If the deck needs a stronger identity, prefer a named preset such as `whiteboard_handdrawn` over vague style words.
- Read `references/style-presets.md` when the user wants a specific visual direction.

Recommended presets:

- `dark_blue_business`
- `light_consulting`
- `whiteboard_handdrawn`
- `custom`

## Page Language Rules

- Titles should usually be shorter than 12 Chinese characters when possible.
- Card titles should usually be 4-8 Chinese characters.
- Prefer noun phrases over long spoken sentences.
- Remove repeated ideas before prompt writing.
- Do not keep provenance lines such as `基于某某内容简化` by default. Keep them only when the user explicitly wants source attribution visible on the slide.
- If a page needs too many words, split the page or move detail to notes.
- If the user wants higher information density, increase text only after deciding where each sentence will live.
- Do not raise information density by repeating the same meaning in the diagram area and the footer area.
- Treat image pages as final text-and-background slides, not as backgrounds waiting for later overlay.

## Composition Rules

- Do not use the same composition on every page.
- Give each page one layout job: path, matrix, cards, comparison, rollout, dashboard, or conclusion.
- Keep one obvious reading path.
- If a page has more text, reduce decoration before reducing text size.
- Preserve the page's native structure when raising information density.
- A path page should stay a path page, a matrix page should stay a matrix page, and a comparison page should stay a comparison page.
- Keep the deck's main visual standard first.
- Use light background and dark text only as a fallback when dense text remains unreadable after layout and wording repair.
- If the provider is `grsai` and the model is `gpt-image-2`, you may deliberately test denser pages after one stable reference pack proves the structure is holding.
- For `grsai` with `gpt-image-2`, two useful stress-test directions are:
  `title + 6-10 small modules + 1 conclusion strip`
  `title + 3-5 larger explanation panels with longer sentences`
- If the slide should feel premium, improve hierarchy, spacing, region ownership, and restraint before adding more glow or motion cues.
- If a page has both a page title and an inner panel title, keep the labels semantically distinct instead of repeating near-identical wording.

## Prompt Assembly Rules

Build prompts in this order:
1. Page identity
2. Page type and composition
3. Reading path
4. Exact text and region mapping
5. Style language and palette
6. Negative rules

Recommended opening line:
- `Generate a 16:9 Chinese client-facing PPT page, not a poster, not a background-only image.`

## Reference Pack Rules

Start with a small pack before full-batch generation.
A good first pack usually includes:
- the cover
- the overall path or agenda page
- one representative content page
- one dense content page with paragraph-level text or many labels
- one complex structured page such as a matrix or comparison page

Use `scripts/run_reference_pack.sh` for the first pass.

Approve the reference pack only when:
- titles are readable
- text is not repeated
- the page reads like a real client-facing slide
- the deck tone feels consistent
- at least one page can act as a style anchor
- the selected style preset is actually visible on the page and not washed out by a generic template

## Style Anchor Rules

- If one reference page best captures the deck tone, label it as the style anchor.
- If the provider supports reference images, pass the approved style anchor into later page generation.
- If the provider does not support reference images, translate the approved page into text rules for card material, lighting, line style, palette, and spacing.
- Keep page-specific structure intact even when reusing the same visual standard.
- For whiteboard decks, treat the first approved page as the strongest style anchor and keep border, handwriting, illustration, and mascot behavior consistent on later pages.
- For whiteboard decks with comic people, keep the people in a supporting role by default unless the user explicitly wants a more playful or mascot-led page.
- If the user wants a hand-drawn explanation deck without a visible board frame, do not force `whiteboard_handdrawn`; use a `custom` borderless hand-drawn style anchor instead.

## Full-Batch Review Rules

After the full batch is generated:
- build review contact sheets with `scripts/build_contact_sheet.py`
- inspect the whole deck, not just 1-2 sample slides
- check for repeated text, wrong words, wrong abbreviations, blurry text, wrong output strips, poster drift, and weak business tone
- check whether semantically duplicated headings appeared in both the page title and a panel title
- inspect the dense pages at full size, not only in contact-sheet view
- rerun only the failed slides after prompt or structure repair
- re-review the repaired slides before packaging
- package only after the reviewed image set is approved

## Recovery Rules

If the provider is busy or unstable:
- rerun with `max-workers=1`
- lower sample resolution first
- retry the small reference pack before the full batch
- rerun only the failed page after prompt fixes

If text quality is poor:
- shorten titles
- reduce the number of visible lines
- make card titles shorter
- make the page identity more explicit
- make the reading path clearer
- give the page a clearer composition
- simplify visual effects before simplifying meaning
- if needed as a fallback, switch the failed dense page to light background and dark text
- remove repeated footer summaries
- keep one sentence in one region only
- restore the original page structure if the prompt drifted into a generic template
- if the chosen preset is `whiteboard_handdrawn`, reduce module count before reducing handwriting size
- if the provider is `grsai` with `gpt-image-2`, try one more dense-structure repair before simplifying, because the model may still carry more text than the default rules assume
- if the model rewrites titles in whiteboard mode, explicitly lock the page title and forbid replacement text before rerunning

If style quality is poor:
- reduce poster-like hero compositions
- reduce dramatic glow, perspective, and cinematic elements
- strengthen business words such as `client-facing`, `proposal`, `consulting-style`, and `presentation-ready`
- require stable card zones and calmer background behavior
- if the deck should be whiteboard-style, explicitly require full 16:9 whiteboard borders, zero room background, handwritten Chinese, and hand-drawn color marker illustration behavior

If review finds specific page defects:
- rerun only the failed slide with `rerun_single_page.sh`
- update prompt wording before rerunning if the problem is repeated
- recheck the repaired slide in both contact-sheet view and full-size view
