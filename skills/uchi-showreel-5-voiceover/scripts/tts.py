#!/usr/bin/env python3
"""Озвучка текста через ElevenLabs (синтез с таймкодами). Ключ: ELEVENLABS_API_KEY."""
import argparse, base64, json, os, sys, urllib.request

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--voice-id", required=True); a.add_argument("--text-file", required=True)
    a.add_argument("--out", required=True); a.add_argument("--model", default="eleven_multilingual_v2")
    a.add_argument("--dry-run", action="store_true")
    o = a.parse_args()
    text = open(o.text_file, encoding="utf-8").read().strip()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{o.voice_id}/with-timestamps"
    body = {"text": text, "model_id": o.model}
    if o.dry_run:
        print("POST", url); print(json.dumps(body, ensure_ascii=False, indent=2)); return
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key: sys.exit("ELEVENLABS_API_KEY не задан в окружении")
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

main()
