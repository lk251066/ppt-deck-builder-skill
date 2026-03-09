#!/usr/bin/env python3
"""
Validate that all expected slide images exist before packaging a deck.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SLIDE_RE = re.compile(r"slide-(\d+)\.png$")


def iter_existing_slides(indir: Path) -> set[int]:
    found: set[int] = set()
    for path in indir.glob("slide-*.png"):
        match = SLIDE_RE.match(path.name)
        if match:
            found.add(int(match.group(1)))
    return found


def iter_expected_slides(plan_path: Path) -> list[int]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    slides = plan.get("slides") or []
    expected = [int(slide.get("slide_number") or 0) for slide in slides]
    expected = [num for num in expected if num > 0]
    expected.sort()
    return expected


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True, help="Path to slides_plan_*.json")
    ap.add_argument("--indir", required=True, help="Directory containing slide-XX.png files")
    args = ap.parse_args()

    plan_path = Path(args.plan).resolve()
    indir = Path(args.indir).resolve()

    expected = iter_expected_slides(plan_path)
    if not expected:
        raise SystemExit(f"No slides found in plan: {plan_path}")

    existing = iter_existing_slides(indir)
    missing = [num for num in expected if num not in existing]
    if missing:
        pretty = ", ".join(f"{num:02d}" for num in missing)
        raise SystemExit(
            f"Missing slide images for packaging in {indir}. Missing slide numbers: {pretty}. Run image generation first."
        )

    summary_path = indir / "generation_summary.json"
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            failed = summary.get("failed") or []
            if failed:
                print(f"warning: generation_summary.json still lists failed items: {len(failed)}")
        except Exception:
            print("warning: generation_summary.json exists but could not be parsed")

    print(indir)
    print(f"validated_slides={len(expected)}")


if __name__ == "__main__":
    main()
