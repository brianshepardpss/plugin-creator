#!/usr/bin/env python3
"""Make a directory-ready plugin icon: .claude-plugin/icon.png, 1024x1024.

Usage:
  python3 make_icon.py <plugin-dir> --text "GS" --color "#0f766e" [--accent "#5eead4"]

The Claude directory takes the icon from .claude-plugin/icon.png (square PNG,
512-2048 px, under 2 MB) only the FIRST time the plugin is saved or submitted
in the developer portal, so make it before submitting. Needs Pillow; this is a
build-time tool, not something the plugin runs for users.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
         "C:/Windows/Fonts/arialbd.ttf"]
S = 1024


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def font(size):
    for f in FONTS:
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default(size=size)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plugin_dir")
    ap.add_argument("--text", required=True, help="1-2 characters")
    ap.add_argument("--color", required=True)
    ap.add_argument("--accent", default="#ffffff")
    a = ap.parse_args()

    base, accent = hex_rgb(a.color), hex_rgb(a.accent)
    img = Image.new("RGB", (S, S), base)
    d = ImageDraw.Draw(img)
    # Soft diagonal light from the top-left.
    for i in range(S):
        t = i / S
        c = tuple(min(255, int(v + (255 - v) * 0.10 * (1 - t))) for v in base)
        d.line([(0, i), (S, i)], fill=c)
    # Accent bar and corner dot: a quiet family mark shared by every plugin.
    d.rounded_rectangle([200, 760, 824, 800], radius=20, fill=accent)
    d.ellipse([824 - 40, 180, 824, 220], fill=accent)
    text = a.text[:2]
    size = 430 if len(text) == 2 else 520
    f = font(size)
    box = d.textbbox((0, 0), text, font=f)
    while box[2] - box[0] > 600 and size > 200:
        size -= 10
        f = font(size)
        box = d.textbbox((0, 0), text, font=f)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text(((S - w) / 2 - box[0], (S - h) / 2 - box[1] - 40), text, font=f, fill=(255, 255, 255))
    out = Path(a.plugin_dir) / ".claude-plugin" / "icon.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
