#!/usr/bin/env python3
"""Проверка окружения для ролика. Пишет <project>/00-preflight.json. Секреты не печатает."""
import glob, json, os, shutil, subprocess, sys, urllib.error, urllib.request

def run(cmd, t=25):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=t)
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except Exception as e:
        return False, str(e)

def main():
    proj = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(proj, exist_ok=True)
    res = {}
    for tool in ("node", "npm", "ffmpeg", "ffprobe"):
        res[tool] = bool(shutil.which(tool))
    ok, _ = run(["npx", "--no-install", "remotion", "--version"]) if shutil.which("npx") else (False, "")
    res["remotion"] = ok
    chromium = any(shutil.which(c) for c in ("chromium", "chromium-browser", "google-chrome"))
    try:
        import playwright  # noqa
        pw = True
    except Exception:
        pw = False
    res["chromium_or_playwright"] = chromium or pw
    for mod in ("PIL", "whisper"):
        try:
            __import__(mod); res[mod.lower()] = True
        except Exception:
            res[mod.lower()] = False
    res["elevenlabs_key_set"] = bool(os.environ.get("ELEVENLABS_API_KEY"))
    fl = run(["fc-list"])[1].lower() if shutil.which("fc-list") else ""
    local = [os.path.basename(p).lower() for p in glob.glob(os.path.join(proj, "assets", "fonts", "*"))]
    fonts = {"oceanic_grotesk_condensed": "oceanic" in fl or any("oceanic" in n for n in local),
             "factor_a": "factor" in fl or any("factor" in n for n in local)}
    res["fonts"] = fonts
    res["logo"] = bool(glob.glob(os.path.join(proj, "assets", "logo.*")))
    try:
        urllib.request.urlopen(urllib.request.Request("https://api.elevenlabs.io", method="HEAD"), timeout=6)
        res["network_elevenlabs"] = True
    except urllib.error.HTTPError:
        res["network_elevenlabs"] = True  # ответ получен, сеть есть
    except Exception:
        res["network_elevenlabs"] = False
    missing = []
    if not res["remotion"]: missing.append("Remotion (запасной рендер: Chromium + ffmpeg)")
    if not res["ffmpeg"] or not res["ffprobe"]: missing.append("ffmpeg/ffprobe")
    if not res["elevenlabs_key_set"]: missing.append("ELEVENLABS_API_KEY или готовая запись диктора")
    if not all(fonts.values()): missing.append("файлы шрифтов Oceanic Grotesk Condensed ExtraBold и Factor A")
    if not res["logo"]: missing.append("утверждённый логотип (assets/logo.svg|png)")
    if not res["network_elevenlabs"]: missing.append("доступ в сеть до api.elevenlabs.io")
    res["missing"] = missing
    res["mode"] = "full" if not missing else "preview"
    json.dump(res, open(os.path.join(proj, "00-preflight.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Режим: {res['mode']}")
    for k, v in res.items():
        if k not in ("missing", "mode"): print(f"  {k}: {v}")
    for m in missing: print("  НЕ ХВАТАЕТ:", m)

main()
