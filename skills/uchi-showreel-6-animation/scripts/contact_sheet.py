#!/usr/bin/env python3
"""Контактная таблица кадров MP4: один файл вместо десятка картинок (экономит токены при просмотре).
Использование: contact_sheet.py out/final.mp4 --frames 100,600,1200 --out out/sheet.png [--cols 4] [--w 270]
Кадры заданы номерами при 60 fps. Достаточно одного взгляда на таблицу."""
import argparse, os, subprocess, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "uchi-showreel", "scripts"))
from mediatools import ffmpeg
from PIL import Image, ImageDraw
a = argparse.ArgumentParser(); a.add_argument("mp4"); a.add_argument("--frames", required=True); a.add_argument("--out", default="sheet.png")
a.add_argument("--cols", type=int, default=4); a.add_argument("--w", type=int, default=270); a.add_argument("--fps", type=float, default=60)
o = a.parse_args(); fs = [int(x) for x in o.frames.split(",")]; h = o.w * 16 // 9
rows = (len(fs) + o.cols - 1) // o.cols; sheet = Image.new("RGB", (o.cols * o.w, rows * h))
with tempfile.TemporaryDirectory() as td:
    for i, n in enumerate(fs):
        p = os.path.join(td, f"{n}.png")
        subprocess.run(ffmpeg() + ["-y", "-v", "error", "-ss", f"{n / o.fps:.4f}", "-i", o.mp4, "-vframes", "1", p], check=True)
        im = Image.open(p).convert("RGB").resize((o.w, h)); ImageDraw.Draw(im).text((6, 6), str(n), fill=(255, 255, 255))
        sheet.paste(im, ((i % o.cols) * o.w, (i // o.cols) * h))
sheet.save(o.out); print("Сохранено:", o.out)
