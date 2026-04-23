# Style Presets

Use one deck-level `style_preset` before prompt writing.
Do not leave style as a vague adjective cloud.

## Recommended Presets

### `dark_blue_business`

Use when:
- the deck is client-facing
- the audience expects enterprise polish
- the user wants a premium blue proposal style

Core traits:
- deep navy and cobalt blue
- restrained futuristic atmosphere
- dark glass or stable module zones
- strong hierarchy and calm background

Avoid:
- cyberpunk overload
- poster-like hero shots
- fake dashboard clutter

### `light_consulting`

Use when:
- the deck is dense
- readability matters more than atmosphere
- the user wants a cleaner consulting style

Core traits:
- light background
- dark text
- soft structure lines
- low visual noise

Avoid:
- washed-out low-contrast blocks
- too many thin separators

### `whiteboard_handdrawn`

Use when:
- the user explicitly asks for whiteboard, board sketch, founder board, hand-drawn courseware, or similar language
- the deck should feel like a live explanation instead of a polished corporate poster
- the content benefits from illustration-led teaching or story-like explanation

Core traits:
- whiteboard fills the entire 16:9 frame
- all four metallic borders visible
- zero room background
- elegant Chinese hard-pen handwriting
- hand-drawn colored illustrations with black outline
- red and black handwritten annotation marks
- stable mascot policy if the user wants a mascot
- comic people can be used as supporting explanation elements

Best uses:
- training decks
- founder-style explanation decks
- concept teaching decks
- product mechanism breakdown pages

Main risks:
- the model may rewrite titles
- the model may add extra doodles or notes
- dense text degrades faster than in business-card layouts
- mascot drift happens if the mascot type is not locked clearly

Rules:
- prefer 3-6 large text groups
- reduce decoration before shrinking handwriting
- explicitly lock exact title text when title wording matters
- explicitly forbid extra handwritten notes when the page must stay clean
- validate one sample title page and one dense page before full-batch generation
- if comic people are used in a client-facing deck, keep them supporting by default rather than dominant
- if a page contains a title plus an inner panel title, avoid near-duplicate wording such as repeating `当前招聘进度` twice
- if the user wants the hand-drawn teaching feeling but does not want a visible board frame, do not force this preset and switch to a `custom` borderless hand-drawn brief instead

Recommended prompt phrases:
- `full-frame whiteboard, all four metallic borders visible`
- `elegant Chinese hard-pen handwriting`
- `hand-drawn colored marker illustrations`
- `only show the approved text lines, each line once only`
- `no office background, no classroom wall, no projector screen`

### `custom`

Use when:
- the user provides strong visual references
- the deck must follow an existing brand or image pack

Rules:
- write a short deck-level style brief first
- do not let each page invent its own style
- if one page becomes the approved reference, treat it as the style anchor

## Selection Guidance

- Default to `dark_blue_business` if the user does not request a stronger style.
- Switch to `light_consulting` when dense Chinese text is the main priority.
- Switch to `whiteboard_handdrawn` only when the user explicitly wants that teaching-board feeling.
- If the user wants hand-drawn explanation without visible board borders, use `custom` with a borderless hand-drawn style brief rather than `whiteboard_handdrawn`.
- Use `custom` when the user provides specific image references or a pre-existing house style.

## Plan File Pattern

```json
{
  "style_preset": "whiteboard_handdrawn",
  "style_goal": "Founder-style whiteboard explanation deck with stable mascot and handwritten Chinese.",
  "style_anchor_strategy": "sample_first_then_full_batch",
  "slides": [
    {
      "slide_number": 1,
      "style_preset": "whiteboard_handdrawn",
      "style_notes": "Keep whiteboard borders and mascot behavior stable.",
      "must_keep_elements": [
        "all four whiteboard borders visible",
        "exact title wording"
      ],
      "forbidden_elements": [
        "room background",
        "extra handwritten notes"
      ]
    }
  ]
}
```
