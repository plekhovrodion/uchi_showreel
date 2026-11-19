#!/usr/bin/env python3
"""Собственный звук перехода «вжух» (синтез шума, без внешних материалов и лицензий). Использование: make_sfx.py showreel/<slug>/audio"""
import math, random, struct, sys, wave
d = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
random.seed(7); sr = 44100; n = int(sr * 0.9); out = []; lp = 0.0
for i in range(n):
    t = i / n; env = math.sin(math.pi * t) ** 2
    a = 0.02 + 0.5 * t if t < 0.5 else 0.02 + 0.5 * (1 - t)
    lp += a * (random.uniform(-1, 1) - lp)
    out.append(int(max(-1, min(1, lp * env * 2.2)) * 32767 * 0.7))
w = wave.open(d.rstrip("/") + "/sfx-whoosh.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(struct.pack("<%dh" % n, *out)); w.close()
print("sfx-whoosh.wav готов")
