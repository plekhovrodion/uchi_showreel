#!/usr/bin/env python3
"""Проверяет, что предмет или герой на прозрачном PNG не обрезан краем картинки.
Если по границе файла есть непрозрачные пиксели, предмет обрезан плоским срезом: перегенерируй с промптом
«entire subject fully visible, generous empty transparent margin on all sides, nothing cropped».
Использование: check_crop.py images/a.png [images/b.png ...] [--frac 0.10] [--alpha 24]
Код выхода 1, если хоть один файл обрезан."""
import argparse, sys
from PIL import Image

a = argparse.ArgumentParser(); a.add_argument("files", nargs="+"); a.add_argument("--frac", type=float, default=0.10); a.add_argument("--alpha", type=int, default=24)
o = a.parse_args(); bad = 0
for f in o.files:
    im = Image.open(f).convert("RGBA"); w, h = im.size; al = im.getchannel("A"); px = al.load();
    def frac(pts): return sum(1 for x, y in pts if px[x, y] > o.alpha) / max(1, len(pts))
    sides = {"сверху": [(x, 1) for x in range(w)], "снизу": [(x, h - 2) for x in range(w)],
             "слева": [(1, y) for y in range(h)], "справа": [(w - 2, y) for y in range(h)]}
    cut = [s for s, pts in sides.items() if frac(pts) > o.frac]  # круглый предмет касается края по касательной (мало пикселей) и это нормально
    if cut: bad = 1; print(f"ОБРЕЗАН {f}: касается края {', '.join(cut)}")
    else: print(f"ok {f}")
sys.exit(bad)
