#!/usr/bin/env python3
"""Озвучка текста через ElevenLabs (синтез с таймкодами). Ключ: ELEVENLABS_API_KEY."""
import argparse, base64, json, os, sys, urllib.request

def _load_key():
    """Ключ: окружение, затем .env (текущая папка и родители, ~/.config/uchi_showreel). Не печатается."""
    k = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if k: return k
    d = os.path.abspath(os.getcwd()); dirs = []
    for _ in range(5): dirs.append(d); d = os.path.dirname(d)
    dirs.append(os.path.expanduser("~/.config/uchi_showreel"))
    for d in dirs:
        p = os.path.join(d, ".env")
        if os.path.isfile(p):
            for line in open(p, encoding="utf-8"):
                if line.strip().startswith("ELEVENLABS_API_KEY="):
                    v = line.split("=", 1)[1].strip().strip("\"'")
                    if v: return v
    return ""

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--voice-id", help="по умолчанию из ../voice.json"); a.add_argument("--text-file", required=True)
    a.add_argument("--out", required=True); a.add_argument("--model", default=None)
    a.add_argument("--dry-run", action="store_true")
    a.add_argument("--stability", type=float); a.add_argument("--style", type=float); a.add_argument("--speed", type=float)
    a.add_argument("--no-defaults", action="store_true", help="не брать голос и настройки из voice.json")
    o = a.parse_args()
    cfg_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "voice.json")
    if not o.no_defaults and os.path.exists(cfg_p):
        cfg = json.load(open(cfg_p, encoding="utf-8"))
        o.voice_id = o.voice_id or cfg.get("voice_id")
        o.model = o.model or cfg.get("model")
        for k in ("stability", "style", "speed"):
            if getattr(o, k) is None and k in cfg: setattr(o, k, cfg[k])
    o.model = o.model or "eleven_v4"
    if not o.voice_id: sys.exit("Нужен --voice-id или skills/uchi-showreel-5-voiceover/voice.json")
    text = open(o.text_file, encoding="utf-8").read().strip()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{o.voice_id}/with-timestamps"
    body = {"text": text, "model_id": o.model}
    vs = {k: v for k, v in (("stability", o.stability), ("style", o.style), ("speed", o.speed)) if v is not None}
    if vs: body["voice_settings"] = {**vs, "similarity_boost": 0.8}
    if o.dry_run:
        print("POST", url); print(json.dumps(body, ensure_ascii=False, indent=2)); return
    key = _load_key()
    if not key: sys.exit("Ключ ElevenLabs не найден. Скопируйте .env.example в .env и впишите ELEVENLABS_API_KEY=... (или задайте переменную окружения). Проверка: skills/uchi-showreel-1-preflight/scripts/check_key.py")
    req = urllib.request.Request(url, method="POST", data=json.dumps(body).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.loads(r.read().decode())
    os.makedirs(os.path.dirname(o.out) or ".", exist_ok=True)
    open(o.out, "wb").write(base64.b64decode(data["audio_base64"]))
    al = data.get("alignment") or data.get("normalized_alignment") or {}
    words, cur, start, prev_e = [], "", None, 0.0
    for ch, s, e in zip(al.get("characters", []), al.get("character_start_times_seconds", []), al.get("character_end_times_seconds", [])):
        if ch.isspace():
            if cur: words.append({"word": cur, "start": start, "end": prev_e}); cur, start = "", None
            continue
        if start is None: start = s
        cur += ch; prev_e = e
    if cur: words.append({"word": cur, "start": start, "end": prev_e})
    json.dump(words, open(os.path.splitext(o.out)[0] + ".words.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("Аудио:", o.out, "слов с таймкодами:", len(words))

if __name__ == "__main__":
    main()
