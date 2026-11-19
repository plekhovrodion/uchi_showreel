#!/usr/bin/env python3
"""Фоновая музыка через ElevenLabs Music (инструментал). Использование: make_music.py showreel/<slug>/audio/music.mp3 --seconds 45 [--prompt "..."]
Ключ из ELEVENLABS_API_KEY или .env. Длина должна быть чуть больше ролика."""
import argparse, json, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tts import _load_key
a = argparse.ArgumentParser(); a.add_argument("out"); a.add_argument("--seconds", type=float, default=45)
a.add_argument("--prompt", default="Calm, light, curious instrumental background music for an educational video. Soft piano and gentle pads, airy, slow tempo, no vocals, no drums, steady and unobtrusive.")
o = a.parse_args(); k = _load_key() or sys.exit("Нет ключа ElevenLabs")
r = urllib.request.Request("https://api.elevenlabs.io/v1/music", method="POST", headers={"xi-api-key": k, "Content-Type": "application/json"},
    data=json.dumps({"prompt": o.prompt, "music_length_ms": int(o.seconds * 1000), "force_instrumental": True}).encode())
os.makedirs(os.path.dirname(o.out) or ".", exist_ok=True); open(o.out, "wb").write(urllib.request.urlopen(r, timeout=300).read()); print("Музыка:", o.out)
