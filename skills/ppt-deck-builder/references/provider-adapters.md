# Provider Adapters

## Goal

Keep the PPT workflow stable while letting the image backend change.
Story design, page briefs, prompt rules, QA, and PPTX packaging should not depend on one image API.

## Built-In Provider Names

- `runninghub_g31`
- `command`

## Recommended Strategy

- Keep `runninghub_g31` as the ready-to-run default.
- Use `command` when OpenClaw or another agent should own the image backend.
- Put backend-specific changes in one adapter command instead of editing the story and layout workflow.
- Start new providers with a small reference pack before the full batch.
- If the workflow needs reference-image style anchoring, image editing, or multi-image conditioning, prefer `command` so the adapter can evolve without changing the deck workflow.

## Plan File Pattern

```json
{
  "image_provider": "command",
  "provider_options": {
    "command": "python3 {baseDir}/scripts/provider_mock_png.py"
  }
}
```

The generator expands `{baseDir}` before invoking the command.

## Command Provider Contract

The command provider is called like this:

```bash
python3 your_adapter.py --request-file /tmp/request.json
```

The request file contains fields such as:

- `slide_number`
- `slide`
- `prompt`
- `resolution`
- `aspectRatio`
- `provider_options`

Because the full `slide` object is passed through, a command adapter may also read custom fields such as:

- `page_identity`
- `reading_path`
- `negative_rules`
- `style_anchor_plan`
- `reference_images`
- `style_anchor_image`

The command must print one JSON object to stdout.

Success response can contain any one of these image outputs:

- `image_url`
- `image_path`
- `image_base64`
- `image_data_uri`

Recommended success shape:

```json
{
  "status": "SUCCESS",
  "provider": "your_provider_name",
  "model": "your_model_name",
  "image_url": "https://example.com/slide.png"
}
```

Recommended failure shape:

```json
{
  "status": "FAILED",
  "provider": "your_provider_name",
  "reason": "what went wrong"
}
```

## RunningHub Notes

Default naming:
- human-readable default: RunningHub 3.1 flash
- workflow model id: `rhart-image-n-g31-flash`

For `runninghub_g31`, supported provider options include:

- `model`
- `base_url`
- `submit_path`
- `query_path`
- `api_key_env`
- `request_overrides`

Default behavior:

- model: `rhart-image-n-g31-flash`
- submit path: `/{model}/text-to-image`
- query path: `/query`

This built-in adapter is text-to-image only by default.
If the workflow needs reference images or image-edit style continuation, switch to `command` and own that logic in the adapter command.

The current generator treats common timeout and busy responses as retryable.
If the provider still fails:
- rerun a smaller batch
- lower sample resolution first
- keep `max-workers=1` until the sample is stable

## OpenClaw Guidance

When used from OpenClaw:

- prefer `{baseDir}` in skill instructions
- let OpenClaw change only the adapter command or provider options
- avoid rewriting the main workflow unless the output contract changes
- if OpenClaw wants stronger cross-page style consistency, it should attach `reference_images` or `style_anchor_image` through the `command` adapter instead of hardcoding one image provider into the skill

## Useful Local Files

- `scripts/provider_command_template.py`
- `scripts/provider_mock_png.py`
