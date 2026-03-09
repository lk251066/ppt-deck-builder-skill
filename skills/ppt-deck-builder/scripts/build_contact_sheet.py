#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build contact sheets for generated slide images so the full deck can be reviewed quickly."
    )
    parser.add_argument("outdir", help="Directory containing slide-XX.png files")
    parser.add_argument(
        "--sheet-dir",
        default=None,
        help="Directory to write contact sheets to. Defaults to <outdir>/qa",
    )
    parser.add_argument("--columns", type=int, default=2, help="Number of columns per sheet")
    parser.add_argument("--max-per-sheet", type=int, default=6, help="Maximum slides per sheet")
    parser.add_argument("--thumb-width", type=int, default=520, help="Thumbnail width")
    parser.add_argument("--thumb-height", type=int, default=293, help="Thumbnail height")
    parser.add_argument("--margin", type=int, default=24, help="Outer and inner margin size")
    return parser.parse_args()


def list_slides(outdir: Path) -> list[Path]:
    return sorted(outdir.glob("slide-*.png"))


def chunked(items: list[Path], size: int) -> Iterable[list[Path]]:
    for idx in range(0, len(items), size):
        yield items[idx : idx + size]


def fit_image(path: Path, width: int, height: int) -> Image.Image:
    img = Image.open(path).convert("RGB")
    img.thumbnail((width, height))
    canvas = Image.new("RGB", (width, height), "#102246")
    x = (width - img.width) // 2
    y = (height - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas


def save_sheet(
    slides: list[Path],
    out_path: Path,
    *,
    columns: int,
    thumb_width: int,
    thumb_height: int,
    margin: int,
) -> None:
    rows = math.ceil(len(slides) / columns)
    label_height = 36
    sheet_width = columns * (thumb_width + margin) + margin
    sheet_height = rows * (thumb_height + label_height + margin) + margin
    sheet = Image.new("RGB", (sheet_width, sheet_height), "#0b1730")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for idx, slide_path in enumerate(slides):
        row = idx // columns
        col = idx % columns
        x = margin + col * (thumb_width + margin)
        y = margin + row * (thumb_height + label_height + margin)
        thumb = fit_image(slide_path, thumb_width, thumb_height)
        sheet.paste(thumb, (x, y))
        draw.rectangle([x, y, x + thumb_width, y + thumb_height], outline="#63d6ff", width=2)
        draw.text((x, y + thumb_height + 8), slide_path.stem, fill="#d9f3ff", font=font)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)


def main() -> int:
    args = parse_args()
    outdir = Path(args.outdir).expanduser().resolve()
    if not outdir.is_dir():
        raise SystemExit(f"Output directory not found: {outdir}")

    slides = list_slides(outdir)
    if not slides:
        raise SystemExit(f"No slide images found under: {outdir}")

    sheet_dir = Path(args.sheet_dir).expanduser().resolve() if args.sheet_dir else outdir / "qa"
    created: list[Path] = []
    for sheet_index, group in enumerate(chunked(slides, args.max_per_sheet), start=1):
        out_path = sheet_dir / f"contact_sheet_{sheet_index}.png"
        save_sheet(
            group,
            out_path,
            columns=args.columns,
            thumb_width=args.thumb_width,
            thumb_height=args.thumb_height,
            margin=args.margin,
        )
        created.append(out_path)

    for item in created:
        print(item)
    print(f"slides={len(slides)}")
    print(f"sheets={len(created)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
