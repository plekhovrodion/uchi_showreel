#!/usr/bin/env python3
"""Сводит озвучку, музыку и звуки переходов; считает границы сцен по словам диктора и пишет timing.json.
Запуск: python3 skills/uchi-showreel-5-voiceover/scripts/build_audio.py showreel/<slug>
Нужны в папке проекта: voiceover.txt (одна строка на сцену), audio/voice.mp3 и audio/voice.words.json (из tts.py),
audio/sfx-whoosh.wav, audio/music.mp3 (по желанию). Повторный запуск после смены голоса: сам берёт сырые слова из voice.words.raw.json."""
import json, os, subprocess, sys, wave, struct, math, shutil
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "uchi-showreel", "scripts"))
from mediatools import ffmpeg
if len(sys.argv) < 2: sys.exit(__doc__)
os.chdir(sys.argv[1])
FPS, TAIL, MIN_SCENE = 60, 1.5, 3.2
raw_ok = os.path.exists('audio/voice.words.raw.json') and os.path.getmtime('audio/voice.words.raw.json') >= os.path.getmtime('audio/voice.mp3')  # сырые слова старше голоса: голос перегенерирован
words = json.load(open('audio/voice.words.raw.json', encoding='utf-8')) if raw_ok else None
if words is None:
    words = json.load(open('audio/voice.words.json', encoding='utf-8'))
    json.dump(words, open('audio/voice.words.raw.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
lines = [l.split() for l in open('voiceover.txt', encoding='utf-8').read().strip().splitlines()]
spans, i = [], 0
for l in lines:
    seg = words[i:i + len(l)]; i += len(l); spans.append((seg[0]['start'], seg[-1]['end']))
voice_end = spans[-1][1]
# границы: середина паузы между сценами; если сцена короче MIN_SCENE, вставляем тишину
raw_b = [(spans[k][1] + spans[k + 1][0]) / 2 for k in range(len(spans) - 1)]
shift, gaps, bounds, prev = 0.0, [], [], 0.0
for k, b in enumerate(raw_b):
    dur = (b + shift) - prev
    if dur < MIN_SCENE:
        g = MIN_SCENE - dur; gaps.append((b, g)); shift += g
    bounds.append(b + shift); prev = b + shift
total = voice_end + shift + TAIL
# слова со сдвигом
sw = []
for w in words:
    s = sum(g for (b, g) in gaps if w['start'] >= b)
    sw.append({**w, 'start': w['start'] + s, 'end': w['end'] + s})
json.dump(sw, open('audio/voice.words.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
# ffmpeg
parts, fc, labels, last = [], '', [], 0.0
for n, (b, g) in enumerate(gaps + [(1e6, 0)]):
    fc += f"[0:a]atrim={last}:{b if b < 1e5 else voice_end + 1},asetpts=PTS-STARTPTS[p{n}];"; labels.append(f'[p{n}]'); last = b
    if g:
        fc += f"anullsrc=r=44100:cl=mono,atrim=0:{g}[g{n}];"; labels.append(f'[g{n}]')
fc += ''.join(labels) + f"concat=n={len(labels)}:v=0:a=1,aresample=44100,pan=mono|c0=c0,loudnorm=I=-16:TP=-3:LRA=11,aresample=44100[v];"
for k, b in enumerate(bounds):
    fc += f"[1:a]volume=0.05,adelay={int(max(0, b - 0.55) * 1000)}[w{k}];"
fc += f"[2:a]aresample=44100,pan=mono|c0=0.5*c0+0.5*c1,volume='0.16*min(1,t/2)*min(1,({total - 0.2:.2f}-t)/2.5)':eval=frame[mu];"
fc += '[v]' + ''.join(f'[w{k}]' for k in range(len(bounds))) + f"[mu]amix=inputs={len(bounds) + 2}:normalize=0,volume=-1.5dB,apad=pad_dur=2[m]"
r = subprocess.run(ffmpeg() + ['-y', '-i', 'audio/voice.mp3', '-i', 'audio/sfx-whoosh.wav', '-i', 'audio/music.mp3',
                    '-filter_complex', fc, '-map', '[m]', '-t', f'{total + 0.1:.2f}', '-ar', '44100', 'audio/mix.wav'], capture_output=True, text=True)
if r.returncode: raise SystemExit(r.stderr[-600:])
w = wave.open('audio/mix.wav'); n = w.getnframes(); d = struct.unpack('<%dh' % n, w.readframes(n))
peak = 20 * math.log10(max(abs(x) for x in d) / 32768)
bf = [round(b * FPS) for b in bounds]
timing = {'fps': FPS, 'boundaries': bf, 'total': round(total * FPS), 'duration_s': round(total, 2), 'gaps': gaps, 'peak_dbfs': round(peak, 2),
          'scenes': [{'scene': k + 1, 'start_frame': ([0] + bf)[k], 'end_frame': (bf + [round(total * FPS)])[k]} for k in range(len(bf) + 1)]}
json.dump(timing, open('timing.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
for src_, dst_ in (('timing.json', 'src/timing.json'), ('audio/voice.words.json', 'src/words.json'), ('audio/mix.wav', 'public/audio/mix.wav')):
    if os.path.isdir(os.path.dirname(dst_)): shutil.copy(src_, dst_)
print('boundaries', bf, 'total', timing['total'], 'peak', timing['peak_dbfs'])
print('min scene s', min(s['end_frame'] - s['start_frame'] for s in timing['scenes']) / FPS)
