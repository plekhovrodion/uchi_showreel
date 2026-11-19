#!/usr/bin/env python3
"""Находит ffmpeg/ffprobe: системные или встроенные в Remotion (node_modules/.bin/remotion ffmpeg|ffprobe).
Импорт: from mediatools import ffmpeg, ffprobe, missing_filters. CLI: mediatools.py ffmpeg|ffprobe|filters [аргументы]"""
import glob, os, shutil, subprocess, sys

NEEDED_FILTERS = ["atrim", "asetpts", "anullsrc", "concat", "aresample", "pan", "adelay", "amix", "volume", "loudnorm", "apad"]
# В сборке ffmpeg из Remotion нет alimiter и afade: громкость ограничивай loudnorm (TP=-3), затухание задавай volume='...':eval=frame

def _remotion_bin():
    roots = [os.getcwd()] + sorted(glob.glob(os.path.join(os.getcwd(), "showreel", "*")))
    d = os.getcwd()
    for _ in range(4):
        roots += [d]; d = os.path.dirname(d)
    for r in roots:
        b = os.path.join(r, "node_modules", ".bin", "remotion")
        if os.path.exists(b): return os.path.abspath(b)
    return None

def _tool(name):
    p = shutil.which(name)
    if p:
        try:
            if subprocess.run([p, "-version"], capture_output=True).returncode == 0: return [p]
        except OSError: pass
    b = _remotion_bin()
    if b: return [b, name]
    sys.exit(f"Нет {name}: поставь ffmpeg или Remotion (cd showreel/<slug> && npm i --save-exact remotion @remotion/cli @remotion/bundler react react-dom)")

def ffmpeg(): return _tool("ffmpeg")
def ffprobe(): return _tool("ffprobe")

def missing_filters():
    out = subprocess.run(ffmpeg() + ["-hide_banner", "-filters"], capture_output=True, text=True).stdout
    names = {l.split()[1] for l in out.splitlines() if len(l.split()) > 1}
    return [f for f in NEEDED_FILTERS if f not in names]

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("ffmpeg", "ffprobe", "filters"): sys.exit(__doc__)
    if sys.argv[1] == "filters": print("не хватает фильтров:", missing_filters() or "всё есть"); sys.exit(0)
    sys.exit(subprocess.run((ffmpeg() if sys.argv[1] == "ffmpeg" else ffprobe()) + sys.argv[2:]).returncode)
