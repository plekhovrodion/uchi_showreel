#!/usr/bin/env python3
"""Готовит проект Remotion для ролика: копирует kit/ в src/, шрифты/логотип/озвучку в public/.
Использование: scaffold.py showreel/<slug>   (после build_audio.py, чтобы были timing.json и words.json)"""
import json, os, shutil, sys
d = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
kit = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit")
src, pub = os.path.join(d, "src"), os.path.join(d, "public")
os.makedirs(src, exist_ok=True); os.makedirs(os.path.join(pub, "fonts"), exist_ok=True); os.makedirs(os.path.join(pub, "audio"), exist_ok=True)
for f in ("brand.tsx", "clouds.ts", "kit.tsx", "Root.tsx", "index.ts", "Main.tsx"):
    dst = os.path.join(src, f)
    if os.path.exists(dst) and f == "Main.tsx": print("Main.tsx уже есть, не трогаю"); continue
    shutil.copy(os.path.join(kit, f), dst)
for f in os.listdir(os.path.join(d, "assets", "fonts")) if os.path.isdir(os.path.join(d, "assets", "fonts")) else []:
    shutil.copy(os.path.join(d, "assets", "fonts", f), os.path.join(pub, "fonts", f))
for f in ("logo.svg", "logo.png"):
    if os.path.exists(os.path.join(d, "assets", f)): shutil.copy(os.path.join(d, "assets", f), os.path.join(pub, f))
if os.path.isdir(os.path.join(d, "images")):
    os.makedirs(os.path.join(pub, "images"), exist_ok=True)
    for f in os.listdir(os.path.join(d, "images")):
        if f.endswith((".png", ".jpg", ".webp")): shutil.copy(os.path.join(d, "images", f), os.path.join(pub, "images", f))
for f, dst in (("timing.json", "src/timing.json"), ("audio/voice.words.json", "src/words.json"), ("audio/mix.wav", "public/audio/mix.wav")):
    if os.path.exists(os.path.join(d, f)): shutil.copy(os.path.join(d, f), os.path.join(d, dst))
    else: print("Нет", f, "— сначала build_audio.py")
print("Готово. Шрифты в brand.tsx подключаются по именам файлов из public/fonts: проверь пути в Fonts.")
