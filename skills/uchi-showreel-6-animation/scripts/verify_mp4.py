#!/usr/bin/env python3
"""Проверка MP4 по требованиям ролика: 1080x1920, 60 fps, H.264, AAC, число кадров, длительность."""
import argparse, json, subprocess, sys

def main():
    a = argparse.ArgumentParser()
    a.add_argument("mp4"); a.add_argument("--frames", type=int, help="ожидаемое число кадров")
    a.add_argument("--short", action="store_true", help="короткая версия: ровно 900 кадров и 15 с")
    o = a.parse_args()
    r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_format", "-of", "json", o.mp4],
                       capture_output=True, text=True)
    if r.returncode: sys.exit("ffprobe: " + r.stderr)
    d = json.loads(r.stdout)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    au = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    errs = []
    if not v: sys.exit("нет видеопотока")
    if (v["width"], v["height"]) != (1080, 1920): errs.append(f"разрешение {v['width']}x{v['height']}")
    if v["codec_name"] != "h264": errs.append("кодек " + v["codec_name"])
    num, den = map(int, v["r_frame_rate"].split("/"))
    if den == 0 or num / den != 60: errs.append("частота " + v["r_frame_rate"])
    n = int(v.get("nb_read_frames", 0)); dur = float(d["format"]["duration"])
    if not au: errs.append("нет аудиопотока")
    elif au["codec_name"] != "aac": errs.append("аудио " + au["codec_name"])
    exp = 900 if o.short else o.frames
    if exp and n != exp: errs.append(f"кадров {n}, ожидалось {exp}")
    if o.short and abs(dur - 15) > 0.05: errs.append(f"длительность {dur:.2f} с, ожидалось 15")
    if not o.short and not 20 <= dur <= 30: errs.append(f"длительность {dur:.2f} с вне 20–30 с")
    print(f"{v['width']}x{v['height']} {v['r_frame_rate']} {v['codec_name']} кадров={n} длительность={dur:.2f}с аудио={au['codec_name'] if au else '—'}")
    for e in errs: print("ОШИБКА:", e)
    if not errs: print("OK")
    sys.exit(1 if errs else 0)

main()
