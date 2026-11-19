#!/usr/bin/env python3
"""Запасной рендер без Remotion: HTML-страница с window.render(frame) -> кадры (Chromium) -> MP4 (ffmpeg).
python3 fallback_render.py page.html --frames 1620 --out out/final.mp4 [--audio audio/mix.m4a] [--workers 4]"""
import argparse, os, shutil, subprocess, tempfile
from concurrent.futures import ProcessPoolExecutor

def work(args):
    page, a, b, d = args
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto("file://" + os.path.abspath(page)); pg.wait_for_timeout(600)
        for f in range(a, b):
            pg.evaluate(f"render({f})")
            pg.screenshot(path=f"{d}/{f:05d}.jpg", type="jpeg", quality=92)
        br.close()

def main():
    a = argparse.ArgumentParser()
    a.add_argument("page"); a.add_argument("--frames", type=int, required=True); a.add_argument("--out", required=True)
    a.add_argument("--audio"); a.add_argument("--workers", type=int, default=4)
    o = a.parse_args()
    d = tempfile.mkdtemp(prefix="frames_")
    step = -(-o.frames // o.workers)
    jobs = [(o.page, i, min(i + step, o.frames), d) for i in range(0, o.frames, step)]
    with ProcessPoolExecutor(o.workers) as ex: list(ex.map(work, jobs))
    os.makedirs(os.path.dirname(o.out) or ".", exist_ok=True)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", "60", "-i", f"{d}/%05d.jpg"]
    cmd += ["-i", o.audio] if o.audio else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    cmd += ["-t", f"{o.frames/60:.4f}", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "60",
            "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", o.out]
    subprocess.run(cmd, check=True); shutil.rmtree(d)
    print("Готово:", o.out, "" if o.audio else "(звук: заглушка)")

if __name__ == "__main__": main()
