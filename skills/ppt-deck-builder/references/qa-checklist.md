# QA Checklist

## Deck Review Setup

- Build review contact sheets with `scripts/build_contact_sheet.py` after the full batch is generated.
- Review the whole deck once in contact-sheet view.
- Review dense or risky slides again at full size.
- Do not package the final client-facing deck before this review is complete.

## Text

- Title is strongest.
- No overlap or clipping.
- No wrong words or duplicate words.
- No unwanted digits, symbols, or labels.
- No awkward forced line breaks in short titles.
- If the page contains `AI`, it is not rewritten or dropped.
- If the page contains `Excel`, it is not replaced with broken letters or other abbreviations.
- Output strips use the exact approved wording once only.

## Layout

- One obvious reading path.
- No empty decorative blocks that dilute focus.
- Visual density matches the amount of text.
- Card style is consistent with the deck direction.
- No white paper cards inside a dark blue business deck unless explicitly intended.
- The page reads like a client-facing slide, not a poster or training handout.

## Common Failure Patterns

- Repeated strip or footer text.
- Repeated or broken panel titles.
- Wrong abbreviations such as damaged `AI` or `Excel`.
- Dense pages that become blurry or tiny.
- Poster-like hero composition that weakens business tone.
- Summary line replaced by a different sentence.
- Right-side or bottom-side labels invented by the model.

## Workflow

- A small reference pack was reviewed before the full batch.
- Full-batch review was completed after generation and before final delivery.
- Failed pages were rerun individually after prompt fixes.
- Repaired pages were reviewed again before packaging.
- Provider changes did not require story or packaging rewrites.

## Delivery

- Output file exists.
- Page numbering matches the plan.
- Final deck contains the updated pages.
- The packaged deck uses the approved image set.
- Packaging was run only after all expected slide images existed.
