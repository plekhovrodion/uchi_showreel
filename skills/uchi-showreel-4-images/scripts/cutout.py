#!/usr/bin/env python3
"""Вырезает однотонный фон (чёрный или белый по углам) и сохраняет PNG с прозрачностью.
Нужен для моделей gpt-image-2*, которые не принимают background=transparent.
Использование: cutout.py in.png out.png [--tol 40] [--round]
--round: для круглых предметов (планета) вместо заливки делает круглую маску по границам предмета."""
import argparse
from PIL import Image, ImageDraw, ImageFilter

a = argparse.ArgumentParser(); a.add_argument("src"); a.add_argument("dst"); a.add_argument("--tol", type=int, default=40); a.add_argument("--round", action="store_true")
o = a.parse_args()
im = Image.open(o.src).convert("RGB"); w, h = im.size
bg = im.getpixel((2, 2))
if o.round:
    thr = 25 if sum(bg) < 150 else None
    bb = im.convert("L").point(lambda v: 255 if v > 25 else 0).getbbox()
    x0, y0, x1, y1 = bb; cx, cy, r = (x0 + x1) / 2, (y0 + y1) / 2, min(x1 - x0, y1 - y0) / 2
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).ellipse((cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3), fill=255)
    out = im.convert("RGBA"); out.putalpha(m.filter(ImageFilter.GaussianBlur(1.2))); out = out.crop((int(cx - r), int(cy - r), int(cx + r), int(cy + r)))
else:
    mask = Image.new("L", im.size, 255)
    marker = Image.new("RGB", im.size, (255, 0, 255)); marker.paste(im)
    work = im.copy()
    for pt in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        ImageDraw.floodfill(work, pt, (255, 0, 255), thresh=o.tol)
    mk = work.point(lambda v: v)
    r_, g_, b_ = work.split()
    bgmask = r_.point(lambda v: 255 if v == 255 else 0)
    bgmask = Image.eval(bgmask, lambda v: v)
    from PIL import ImageChops
    isbg = ImageChops.multiply(r_.point(lambda v: 255 if v == 255 else 0), g_.point(lambda v: 255 if v == 0 else 0))
    alpha = ImageChops.invert(isbg).filter(ImageFilter.GaussianBlur(1))
    out = im.convert("RGBA"); out.putalpha(alpha)
out.save(o.dst); print("Сохранено:", o.dst, out.size)
