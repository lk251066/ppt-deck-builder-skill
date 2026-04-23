#!/usr/bin/env python3
"""
Generate slide images from a plan JSON using a selectable image provider.

Built-in providers:
- runninghub_g31: RunningHub Standard Model API
- grsai: GrsAI draw API
- command: call a local command adapter that returns JSON on stdout

This script intentionally does NOT store API keys in any file.
Set provider-specific env vars before running.
"""

from __future__ import annotations

import argparse
import base64
import binascii
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
from threading import Lock
import time
from typing import Any

import requests


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PROVIDER = "grsai"
DEFAULT_RUNNINGHUB_BASE = "https://www.runninghub.cn/openapi/v2"
DEFAULT_RUNNINGHUB_MODEL = "rhart-image-n-g31-flash"
DEFAULT_QUERY_PATH = "/query"
DEFAULT_GRSAI_BASE = "https://grsai.dakka.com.cn"
DEFAULT_GRSAI_MODEL = "gpt-image-2"
GRSAI_SUPPORTED_SIZES = {
    "auto",
    "1:1",
    "3:2",
    "2:3",
    "16:9",
    "9:16",
    "4:3",
    "3:4",
    "21:9",
    "9:21",
    "1:3",
    "3:1",
    "2:1",
    "1:2",
}


def as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def resolve_templates(value: Any) -> Any:
    if isinstance(value, str):
        return value.replace("{baseDir}", str(SKILL_ROOT))
    if isinstance(value, dict):
        return {str(k): resolve_templates(v) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve_templates(v) for v in value]
    return value


def parse_scalar(value: str) -> Any:
    try:
        return json.loads(value)
    except Exception:
        return value


def parse_provider_options(raw_items: list[str]) -> dict[str, Any]:
    options: dict[str, Any] = {}
    for item in raw_items:
        if "=" not in item:
            raise SystemExit(f"Invalid --provider-option: {item}. Expected KEY=VALUE")
        key, raw_value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise SystemExit(f"Invalid --provider-option: {item}. Empty key")
        options[key] = parse_scalar(raw_value.strip())
    return options


def normalize_provider(name: str | None) -> str:
    if not name:
        return DEFAULT_PROVIDER
    normalized = str(name).strip()
    aliases = {
        "runninghub": "runninghub_g31",
        "runninghub_g31": "runninghub_g31",
        "grsai": "grsai",
        "grsai_draw": "grsai",
        "grsai_gpt_image": "grsai",
        "command": "command",
        "custom-command": "command",
    }
    return aliases.get(normalized, normalized)


def pick_prompt(slide: dict[str, Any]) -> str:
    return slide.get("prompt_override") or slide.get("prompt") or slide.get("content") or ""


def build_fallback_prompt(prompt: str) -> str:
    """
    Simplify prompt to reduce model load while keeping page identity, layout,
    and text constraints.
    """
    lines = [ln.strip() for ln in prompt.splitlines() if ln.strip()]
    keep: list[str] = []
    section_starts = (
        "你是一位",
        "Generate a 16:9",
        "【风格】",
        "【版式】",
        "【文字要求】",
        "【页面文字",
        "Page type:",
        "Reading path:",
        "Composition:",
        "Text rule:",
        "Style:",
        "Negative rules:",
    )
    for ln in lines:
        if ln.startswith(section_starts):
            keep.append(ln)
        elif keep and (keep[-1].startswith("【页面文字") or keep[-1].startswith("Text rule:")) and not ln.startswith("【"):
            keep.append(ln)
    if len(keep) < 6:
        return prompt + "\n画面更简洁，减少复杂背景细节，确保文字清晰。"
    return "\n".join(keep) + "\n画面更简洁，减少复杂背景细节，确保文字清晰。"


def is_retryable_runninghub_failure(final_resp: dict[str, Any] | None) -> bool:
    if not final_resp:
        return False
    code = str(final_resp.get("errorCode") or "")
    msg = str(final_resp.get("errorMessage") or "")
    lowered = msg.lower()
    if code in {"1006", "1011", "1504"}:
        return True
    if "超时" in msg or "timed out" in lowered:
        return True
    if "system is currently busy" in lowered or "当前系统负载较高" in msg or "please retry later" in lowered:
        return True
    return False


def select_provider(plan: dict[str, Any], slide: dict[str, Any], cli_provider: str | None) -> str:
    return normalize_provider(
        slide.get("image_provider")
        or cli_provider
        or plan.get("image_provider")
        or os.getenv("PPT_IMAGE_PROVIDER")
        or DEFAULT_PROVIDER
    )


def select_resolution(plan: dict[str, Any], slide: dict[str, Any], cli_resolution: str | None) -> str:
    return str(slide.get("resolution") or cli_resolution or plan.get("resolution") or "4k")


def select_aspect_ratio(plan: dict[str, Any], slide: dict[str, Any], cli_aspect_ratio: str | None) -> str:
    return str(slide.get("aspect_ratio") or cli_aspect_ratio or plan.get("aspect_ratio") or "16:9")


def build_provider_options(
    *,
    plan: dict[str, Any],
    slide: dict[str, Any],
    cli_model: str | None,
    cli_provider_command: str | None,
    cli_provider_options: dict[str, Any],
) -> dict[str, Any]:
    options: dict[str, Any] = {}
    options.update(as_dict(plan.get("provider_options")))
    options.update(as_dict(slide.get("provider_options")))

    model_suggestion = slide.get("model_suggestion") or plan.get("model_suggestion")
    if model_suggestion and "model" not in options:
        options["model"] = model_suggestion

    if cli_model:
        options["model"] = cli_model
    if cli_provider_command:
        options["command"] = cli_provider_command
    options.update(cli_provider_options)
    return resolve_templates(options)


def download_first_image(results: Any) -> str | None:
    if not isinstance(results, list):
        return None
    for item in results:
        if isinstance(item, dict) and item.get("url"):
            return str(item["url"])
    return None


def slim_attempt_record(record: dict[str, Any]) -> dict[str, Any]:
    slim = dict(record)
    for key in ("image_base64", "image_data_uri"):
        if key in slim and isinstance(slim[key], str):
            slim[key] = f"<{key}:{len(slim[key])} chars>"
    provider_response = slim.get("provider_response")
    if isinstance(provider_response, dict):
        provider_response = dict(provider_response)
        for key in ("image_base64", "image_data_uri"):
            if key in provider_response and isinstance(provider_response[key], str):
                provider_response[key] = f"<{key}:{len(provider_response[key])} chars>"
        slim["provider_response"] = provider_response
    return slim


def guess_mime_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    if suffix == ".gif":
        return "image/gif"
    return "image/png"


def maybe_to_data_uri(value: str) -> str:
    lowered = value.lower()
    if lowered.startswith("http://") or lowered.startswith("https://") or lowered.startswith("data:"):
        return value

    path = Path(value).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.exists() or not path.is_file():
        return value

    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{guess_mime_type(path)};base64,{encoded}"


def collect_reference_images(slide: dict[str, Any], provider_options: dict[str, Any]) -> list[str]:
    raw_images: list[Any] = []

    for key in ("reference_images", "style_anchor_images"):
        value = slide.get(key)
        if isinstance(value, list):
            raw_images.extend(value)

    style_anchor_image = slide.get("style_anchor_image")
    if isinstance(style_anchor_image, str) and style_anchor_image.strip():
        raw_images.append(style_anchor_image.strip())

    provider_reference_images = provider_options.get("reference_images")
    if isinstance(provider_reference_images, list):
        raw_images.extend(provider_reference_images)

    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_images:
        if not isinstance(item, str):
            continue
        value = item.strip()
        if not value:
            continue
        encoded = maybe_to_data_uri(value)
        if encoded in seen:
            continue
        seen.add(encoded)
        normalized.append(encoded)
    return normalized


def pick_grsai_size(aspect_ratio: str, provider_options: dict[str, Any]) -> str:
    size = str(provider_options.get("size") or aspect_ratio or "auto").strip()
    if size in GRSAI_SUPPORTED_SIZES:
        return size
    return "auto"


def write_image_from_result(result: dict[str, Any], out: Path) -> dict[str, Any] | None:
    image_path = result.get("image_path")
    if image_path:
        src = Path(str(image_path)).expanduser()
        if not src.is_absolute():
            src = Path.cwd() / src
        if not src.exists():
            return None
        out.write_bytes(src.read_bytes())
        return {"image_source": "path", "image_path": str(src.resolve())}

    image_url = result.get("image_url")
    if image_url:
        img = requests.get(str(image_url), timeout=180)
        img.raise_for_status()
        out.write_bytes(img.content)
        return {"image_source": "url", "image_url": str(image_url)}

    image_data_uri = result.get("image_data_uri")
    if isinstance(image_data_uri, str) and "," in image_data_uri:
        _, encoded = image_data_uri.split(",", 1)
        try:
            out.write_bytes(base64.b64decode(encoded))
            return {"image_source": "data_uri"}
        except (binascii.Error, ValueError):
            return None

    image_base64 = result.get("image_base64")
    if isinstance(image_base64, str):
        try:
            out.write_bytes(base64.b64decode(image_base64))
            return {"image_source": "base64"}
        except (binascii.Error, ValueError):
            return None

    return None


def run_runninghub_attempt(
    *,
    prompt: str,
    resolution: str,
    aspect_ratio: str,
    provider_options: dict[str, Any],
    max_poll_seconds: int,
) -> dict[str, Any]:
    base_url = str(provider_options.get("base_url") or os.getenv("RUNNINGHUB_BASE_URL") or DEFAULT_RUNNINGHUB_BASE).rstrip("/")
    model = str(provider_options.get("model") or os.getenv("RUNNINGHUB_MODEL") or DEFAULT_RUNNINGHUB_MODEL)
    submit_path = str(provider_options.get("submit_path") or f"/{model}/text-to-image")
    query_path = str(provider_options.get("query_path") or DEFAULT_QUERY_PATH)
    api_key_env = str(provider_options.get("api_key_env") or "RUNNINGHUB_API_KEY")
    api_key = os.getenv(api_key_env)
    if not api_key:
        return {
            "status": "FAILED",
            "provider": "runninghub_g31",
            "model": model,
            "reason": f"{api_key_env} is not set",
        }

    request_overrides = as_dict(provider_options.get("request_overrides"))
    payload = {
        "prompt": prompt,
        "resolution": resolution,
        "aspectRatio": aspect_ratio,
    }
    payload.update(request_overrides)

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    submit_url = f"{base_url}{submit_path if submit_path.startswith('/') else '/' + submit_path}"
    query_url = f"{base_url}{query_path if query_path.startswith('/') else '/' + query_path}"

    submit_resp = requests.post(submit_url, headers=headers, json=payload, timeout=120)
    submit_resp.raise_for_status()
    submit_json = submit_resp.json()

    task_id = submit_json.get("taskId")
    if not task_id:
        return {
            "status": "FAILED",
            "provider": "runninghub_g31",
            "model": model,
            "submit_response": submit_json,
            "reason": "no_taskId",
        }

    start = time.time()
    final_json: dict[str, Any] | None = None
    while time.time() - start < max_poll_seconds:
        q = requests.post(query_url, headers=headers, json={"taskId": task_id}, timeout=120)
        q.raise_for_status()
        qj = q.json()
        status = qj.get("status")
        if status in {"SUCCESS", "FAILED", "CANCELLED"}:
            final_json = qj
            break
        time.sleep(5)

    attempt_record: dict[str, Any] = {
        "status": "FAILED",
        "provider": "runninghub_g31",
        "model": model,
        "taskId": task_id,
        "submit_response": submit_json,
        "final_response": final_json,
    }

    if not final_json:
        attempt_record["reason"] = "poll_timeout"
        return attempt_record

    if final_json.get("status") != "SUCCESS":
        attempt_record["reason"] = final_json.get("errorMessage") or final_json.get("status")
        return attempt_record

    image_url = download_first_image(final_json.get("results"))
    if not image_url:
        attempt_record["reason"] = "no_image_url"
        return attempt_record

    attempt_record["status"] = "SUCCESS"
    attempt_record["image_url"] = image_url
    return attempt_record


def is_retryable_grsai_failure(final_resp: dict[str, Any] | None) -> bool:
    if not final_resp:
        return False
    data = as_dict(final_resp.get("data"))
    reason = str(data.get("failure_reason") or "")
    error = str(data.get("error") or "")
    lowered = f"{reason} {error}".lower()
    return any(
        token in lowered
        for token in (
            "excessive system load",
            "system load",
            "server busy",
            "try again later",
            "timeout",
        )
    )


def run_grsai_attempt(
    *,
    slide: dict[str, Any],
    prompt: str,
    resolution: str,
    aspect_ratio: str,
    provider_options: dict[str, Any],
    max_poll_seconds: int,
) -> dict[str, Any]:
    del resolution

    base_url = str(provider_options.get("base_url") or os.getenv("GRSAI_BASE_URL") or DEFAULT_GRSAI_BASE).rstrip("/")
    model = str(provider_options.get("model") or os.getenv("GRSAI_MODEL") or DEFAULT_GRSAI_MODEL)
    submit_path = str(provider_options.get("submit_path") or "/v1/draw/completions")
    result_path = str(provider_options.get("result_path") or "/v1/draw/result")
    api_key_env = str(provider_options.get("api_key_env") or "GRSAI_API_KEY")
    api_key = os.getenv(api_key_env)
    if not api_key:
        return {
            "status": "FAILED",
            "provider": "grsai",
            "model": model,
            "reason": f"{api_key_env} is not set",
        }

    request_overrides = as_dict(provider_options.get("request_overrides"))
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "size": pick_grsai_size(aspect_ratio, provider_options),
        "webHook": "-1",
        "shutProgress": True,
    }
    reference_images = collect_reference_images(slide, provider_options)
    if reference_images:
        payload["urls"] = reference_images
    payload.update(request_overrides)

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    submit_url = f"{base_url}{submit_path if submit_path.startswith('/') else '/' + submit_path}"
    result_url = f"{base_url}{result_path if result_path.startswith('/') else '/' + result_path}"

    try:
        submit_resp = requests.post(submit_url, headers=headers, json=payload, timeout=120)
        submit_resp.raise_for_status()
        submit_json = submit_resp.json()
    except requests.RequestException as exc:
        return {
            "status": "FAILED",
            "provider": "grsai",
            "model": model,
            "reason": f"submit_request_failed: {exc}",
            "retryable": True,
        }

    submit_data = as_dict(submit_json.get("data"))
    task_id = submit_data.get("id") or submit_json.get("id")
    if not task_id:
        return {
            "status": "FAILED",
            "provider": "grsai",
            "model": model,
            "submit_response": submit_json,
            "reason": "no_task_id",
        }

    start = time.time()
    final_json: dict[str, Any] | None = None
    while time.time() - start < max_poll_seconds:
        try:
            q = requests.post(result_url, headers=headers, json={"id": task_id}, timeout=120)
            q.raise_for_status()
            qj = q.json()
        except requests.RequestException as exc:
            attempt_record = {
                "status": "FAILED",
                "provider": "grsai",
                "model": model,
                "taskId": task_id,
                "submit_response": submit_json,
                "reason": f"poll_request_failed: {exc}",
                "retryable": True,
            }
            return attempt_record
        data = as_dict(qj.get("data"))
        status = str(data.get("status") or "").lower()
        if status in {"succeeded", "failed", "cancelled"}:
            final_json = qj
            break
        time.sleep(4)

    attempt_record: dict[str, Any] = {
        "status": "FAILED",
        "provider": "grsai",
        "model": model,
        "taskId": task_id,
        "submit_response": submit_json,
        "final_response": final_json,
    }

    if not final_json:
        attempt_record["reason"] = "poll_timeout"
        return attempt_record

    final_data = as_dict(final_json.get("data"))
    final_status = str(final_data.get("status") or "").lower()
    if final_status != "succeeded":
        attempt_record["reason"] = final_data.get("error") or final_data.get("failure_reason") or final_status or "failed"
        return attempt_record

    image_url = download_first_image(final_data.get("results")) or final_data.get("url")
    if not image_url:
        attempt_record["reason"] = "no_image_url"
        return attempt_record

    attempt_record["status"] = "SUCCESS"
    attempt_record["image_url"] = str(image_url)
    return attempt_record


def run_command_attempt(
    *,
    slide: dict[str, Any],
    slide_number: int,
    prompt: str,
    resolution: str,
    aspect_ratio: str,
    provider_options: dict[str, Any],
) -> dict[str, Any]:
    command = str(provider_options.get("command") or os.getenv("PPT_IMAGE_PROVIDER_COMMAND") or "").strip()
    if not command:
        return {
            "status": "FAILED",
            "provider": "command",
            "reason": "provider command is not set",
        }

    request_payload = {
        "slide_number": slide_number,
        "slide": slide,
        "prompt": prompt,
        "resolution": resolution,
        "aspectRatio": aspect_ratio,
        "provider": "command",
        "provider_options": provider_options,
    }

    fd, request_path_raw = tempfile.mkstemp(prefix=f"slide-{slide_number:02d}-", suffix=".json")
    os.close(fd)
    request_path = Path(request_path_raw)
    request_path.write_text(json.dumps(request_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    env = os.environ.copy()
    for key, value in as_dict(provider_options.get("env")).items():
        env[str(key)] = str(value)

    timeout_seconds = int(provider_options.get("timeout_seconds") or 900)
    cwd = provider_options.get("cwd")
    run_cwd = str(cwd) if cwd else None

    cmd = shlex.split(command) + ["--request-file", str(request_path)]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
            cwd=run_cwd,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        request_path.unlink(missing_ok=True)
        return {
            "status": "FAILED",
            "provider": "command",
            "command": command,
            "reason": f"provider command timed out after {timeout_seconds}s",
            "retryable": True,
        }

    request_path.unlink(missing_ok=True)

    if proc.returncode != 0:
        return {
            "status": "FAILED",
            "provider": "command",
            "command": command,
            "reason": f"provider command exited with {proc.returncode}",
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

    stdout = proc.stdout.strip()
    if not stdout:
        return {
            "status": "FAILED",
            "provider": "command",
            "command": command,
            "reason": "provider command returned empty stdout",
        }

    try:
        provider_response = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return {
            "status": "FAILED",
            "provider": "command",
            "command": command,
            "reason": f"provider command returned invalid JSON: {exc}",
            "stdout": stdout,
            "stderr": proc.stderr,
        }

    result: dict[str, Any] = {
        "status": str(provider_response.get("status") or "FAILED").upper(),
        "provider": str(provider_response.get("provider") or "command"),
        "model": provider_response.get("model"),
        "command": command,
        "provider_response": provider_response,
    }
    for key in ("image_url", "image_path", "image_base64", "image_data_uri", "taskId", "reason"):
        if provider_response.get(key) is not None:
            result[key] = provider_response.get(key)
    return result


def run_provider_attempt(
    *,
    provider: str,
    slide: dict[str, Any],
    slide_number: int,
    prompt: str,
    resolution: str,
    aspect_ratio: str,
    provider_options: dict[str, Any],
    max_poll_seconds: int,
) -> dict[str, Any]:
    if provider == "runninghub_g31":
        return run_runninghub_attempt(
            prompt=prompt,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            provider_options=provider_options,
            max_poll_seconds=max_poll_seconds,
        )
    if provider == "grsai":
        return run_grsai_attempt(
            slide=slide,
            prompt=prompt,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            provider_options=provider_options,
            max_poll_seconds=max_poll_seconds,
        )
    if provider == "command":
        return run_command_attempt(
            slide=slide,
            slide_number=slide_number,
            prompt=prompt,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            provider_options=provider_options,
        )
    return {
        "status": "FAILED",
        "provider": provider,
        "reason": f"unsupported provider: {provider}",
    }


def generate_one_slide(
    *,
    slide: dict[str, Any],
    plan: dict[str, Any],
    outdir: Path,
    cli_provider: str | None,
    cli_resolution: str | None,
    cli_aspect_ratio: str | None,
    cli_model: str | None,
    cli_provider_command: str | None,
    cli_provider_options: dict[str, Any],
    max_poll_seconds: int,
    max_retries: int,
    overwrite: bool,
) -> dict[str, Any]:
    slide_number = int(slide.get("slide_number") or 0)
    prompt = pick_prompt(slide)
    if not prompt:
        return {"slide": slide_number, "status": "FAILED", "reason": "empty_prompt"}

    out = outdir / f"slide-{slide_number:02d}.png"
    if out.exists() and not overwrite:
        return {"slide": slide_number, "status": "SKIPPED", "path": str(out)}

    provider = select_provider(plan, slide, cli_provider)
    resolution = select_resolution(plan, slide, cli_resolution)
    aspect_ratio = select_aspect_ratio(plan, slide, cli_aspect_ratio)
    provider_options = build_provider_options(
        plan=plan,
        slide=slide,
        cli_model=cli_model,
        cli_provider_command=cli_provider_command,
        cli_provider_options=cli_provider_options,
    )

    attempts: list[dict[str, Any]] = []
    for attempt in range(1, max_retries + 2):
        use_prompt = prompt if attempt == 1 else build_fallback_prompt(prompt)
        result = run_provider_attempt(
            provider=provider,
            slide=slide,
            slide_number=slide_number,
            prompt=use_prompt,
            resolution=resolution,
            aspect_ratio=aspect_ratio,
            provider_options=provider_options,
            max_poll_seconds=max_poll_seconds,
        )
        result["attempt"] = attempt
        attempts.append(slim_attempt_record(result))

        if result.get("status") != "SUCCESS":
            if provider == "runninghub_g31" and is_retryable_runninghub_failure(result.get("final_response")):
                continue
            if provider == "grsai" and (result.get("retryable") or is_retryable_grsai_failure(result.get("final_response"))):
                continue
            if provider == "command" and result.get("retryable"):
                continue
            break

        image_meta = write_image_from_result(result, out)
        if not image_meta:
            continue

        return {
            "slide": slide_number,
            "status": "SUCCESS",
            "provider": provider,
            "model": result.get("model") or provider_options.get("model"),
            "path": str(out),
            "attempts": attempts,
            **image_meta,
        }

    return {
        "slide": slide_number,
        "status": "FAILED",
        "provider": provider,
        "model": provider_options.get("model"),
        "attempts": attempts,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True, help="Path to slides_plan_*.json")
    ap.add_argument("--outdir", required=True, help="Output directory for images")
    ap.add_argument("--provider", help="Image provider override, e.g. grsai, runninghub_g31, or command")
    ap.add_argument("--provider-command", help="Local adapter command for provider=command")
    ap.add_argument("--provider-option", action="append", default=[], metavar="KEY=VALUE", help="Extra provider option override")
    ap.add_argument("--model", help="Model override for providers that use a model name")
    ap.add_argument("--resolution", help="Resolution override, e.g. 4k or 1024x1024")
    ap.add_argument("--aspect-ratio", help="Aspect ratio override, e.g. 16:9")
    ap.add_argument("--max-poll-seconds", type=int, default=600, help="Polling timeout per slide")
    ap.add_argument("--max-retries", type=int, default=2, help="Retries per slide on timeouts")
    ap.add_argument("--max-workers", type=int, default=3, help="Parallel workers")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing slide-XX.png files")
    ap.add_argument("--start-slide", type=int, default=1, help="First slide number to generate")
    ap.add_argument("--end-slide", type=int, default=9999, help="Last slide number to generate")
    args = ap.parse_args()

    plan_path = Path(args.plan).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    slides = plan.get("slides") or []
    slides = [s for s in slides if args.start_slide <= int(s.get("slide_number") or 0) <= args.end_slide]

    cli_provider = normalize_provider(args.provider) if args.provider else None
    cli_provider_options = parse_provider_options(args.provider_option)
    default_provider = normalize_provider(
        cli_provider or plan.get("image_provider") or os.getenv("PPT_IMAGE_PROVIDER") or DEFAULT_PROVIDER
    )

    summary: dict[str, Any] = {
        "plan": str(plan_path),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "provider_default": default_provider,
        "model_default": args.model or plan.get("model_suggestion") or as_dict(plan.get("provider_options")).get("model"),
        "resolution_default": args.resolution or plan.get("resolution") or "4k",
        "aspectRatio_default": args.aspect_ratio or plan.get("aspect_ratio") or "16:9",
        "generated": [],
        "failed": [],
        "skipped": [],
    }

    summary_lock = Lock()

    def persist_summary() -> None:
        (outdir / "generation_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    with ThreadPoolExecutor(max_workers=max(1, int(args.max_workers))) as executor:
        futures = [
            executor.submit(
                generate_one_slide,
                slide=slide,
                plan=plan,
                outdir=outdir,
                cli_provider=cli_provider,
                cli_resolution=args.resolution,
                cli_aspect_ratio=args.aspect_ratio,
                cli_model=args.model,
                cli_provider_command=args.provider_command,
                cli_provider_options=cli_provider_options,
                max_poll_seconds=args.max_poll_seconds,
                max_retries=args.max_retries,
                overwrite=bool(args.overwrite),
            )
            for slide in slides
        ]

        for future in as_completed(futures):
            record = future.result()
            with summary_lock:
                status = record.get("status")
                if status == "SUCCESS":
                    summary["generated"].append(record)
                elif status == "SKIPPED":
                    summary["skipped"].append(record)
                else:
                    summary["failed"].append(record)
                persist_summary()

    summary_path = outdir / "generation_summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(summary_path)
    print(f"generated={len(summary['generated'])}, skipped={len(summary['skipped'])}, failed={len(summary['failed'])}")


if __name__ == "__main__":
    main()
