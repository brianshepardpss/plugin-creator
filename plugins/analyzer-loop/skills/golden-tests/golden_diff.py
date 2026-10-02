#!/usr/bin/env python3
"""Measure how far a failing Flutter golden is from its master image. Standard library only.

Usage:
  python3 golden_diff.py <master.png> <test.png>
  python3 golden_diff.py <failures-dir> [name]     # e.g. test/failures price_badge
      reads <name>_masterImage.png and <name>_testImage.png that `flutter test` writes
      next to the test file when a golden fails.

How the numbers are produced (same rule as flutter_test's LocalFileComparator):
  * Both images are decoded to 8-bit RGBA. Different sizes = 100% diff (size mismatch).
  * A pixel "differs" when |dR|+|dG|+|dB|+|dA| > 0 (any channel change at all).
  * diff % = differing pixels / (width * height) * 100, shown to 4 decimals.
    flutter_test prints the same ratio rounded to 2 decimals.
  * max channel delta = largest single-channel change; bbox = smallest box holding all
    differing pixels (x0,y0)-(x1,y1), inclusive.
  * suggested tolerance = diff ratio rounded UP to the next 0.0001, i.e. the smallest
    precisionTolerance a tolerant comparator would need to accept this exact run.
Classification (heuristic, printed with its reason):
  * size mismatch                         -> layout changed or different surface size
  * <= 0.5% of pixels and max delta <= 96 -> rendering drift (fonts, anti-aliasing, GPU/OS)
  * otherwise                             -> likely a real visual change; review the diff PNGs
Supports non-interlaced PNG, bit depth 8, color types 0/2/4/6 (what Flutter writes).
"""
import math
import struct
import sys
import zlib
from pathlib import Path


def decode_png(path):
    data = Path(path).read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    pos, idat, w = 8, b"", 0
    while pos < len(data):
        ln, typ = struct.unpack(">I4s", data[pos:pos + 8])
        chunk = data[pos + 8:pos + 8 + ln]
        if typ == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", chunk)
            if depth != 8 or interlace != 0 or ctype not in (0, 2, 4, 6):
                raise ValueError(f"{path}: unsupported PNG (depth {depth}, color {ctype}, interlace {interlace})")
        elif typ == b"IDAT":
            idat += chunk
        elif typ == b"IEND":
            break
        pos += 12 + ln
    ch = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
    raw = zlib.decompress(idat)
    stride = w * ch
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(h):
        f = raw[i]
        line = bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line[x - ch] if x >= ch else 0
            b = prev[x]
            c = prev[x - ch] if x >= ch else 0
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b) & 255
            elif f == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 255
        rows.append(line)
        prev = line

    def rgba(row, x):
        o = x * ch
        if ch == 4:
            return tuple(row[o:o + 4])
        if ch == 3:
            return (row[o], row[o + 1], row[o + 2], 255)
        if ch == 2:
            return (row[o], row[o], row[o], row[o + 1])
        return (row[o], row[o], row[o], 255)

    return w, h, [[rgba(r, x) for x in range(w)] for r in rows]


def compare(master, test):
    mw, mh, mp = decode_png(master)
    tw, th, tp = decode_png(test)
    out = {"master": str(master), "test": str(test), "master_size": f"{mw}x{mh}", "test_size": f"{tw}x{th}"}
    if (mw, mh) != (tw, th):
        out.update(diff_pixels=None, diff_percent=100.0, verdict="size mismatch",
                   reason="image sizes differ; layout or surface size changed")
        return out
    n, maxd, xs, ys = 0, 0, [], []
    for y in range(mh):
        for x in range(mw):
            a, b = mp[y][x], tp[y][x]
            if a != b:
                n += 1
                maxd = max(maxd, max(abs(a[k] - b[k]) for k in range(4)))
                xs.append(x)
                ys.append(y)
    total = mw * mh
    ratio = n / total
    out.update(total_pixels=total, diff_pixels=n, diff_percent=round(ratio * 100, 4),
               flutter_reports=f"{ratio * 100:.2f}%, {n}px", max_channel_delta=maxd,
               bbox=(f"({min(xs)},{min(ys)})-({max(xs)},{max(ys)})" if n else None),
               suggested_tolerance=math.ceil(ratio * 10000) / 10000)
    if n == 0:
        out.update(verdict="identical", reason="no pixel differs")
    elif ratio <= 0.005 and maxd <= 96:
        out.update(verdict="rendering drift",
                   reason="few pixels, small channel change: typical of font hinting, anti-aliasing or OS/GPU differences")
    else:
        out.update(verdict="likely real change",
                   reason="many pixels or large color change; open the isolatedDiff/maskedDiff PNGs and review")
    return out


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    p = Path(a[0])
    if p.is_dir():
        names = [a[1]] if len(a) > 1 else sorted({f.name.rsplit("_", 1)[0] for f in p.glob("*_masterImage.png")})
        pairs = [(p / f"{n}_masterImage.png", p / f"{n}_testImage.png") for n in names]
    else:
        pairs = [(p, Path(a[1]))]
    if not pairs:
        print(f"No *_masterImage.png files in {p}")
        return 2
    for m, t in pairs:
        r = compare(m, t)
        print(f"Golden: {m.name.replace('_masterImage.png', '')}")
        print(f"  size            master {r['master_size']}, test {r['test_size']}")
        if r.get("diff_pixels") is not None:
            print(f"  differing px    {r['diff_pixels']} of {r['total_pixels']} = {r['diff_percent']}%"
                  f"  (flutter prints {r['flutter_reports']})")
            print(f"  max channel d   {r['max_channel_delta']} (0-255)")
            print(f"  bbox            {r['bbox']}")
            print(f"  min tolerance   {r['suggested_tolerance']} (precisionTolerance that would just accept this run)")
        print(f"  verdict         {r['verdict']}: {r['reason']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
