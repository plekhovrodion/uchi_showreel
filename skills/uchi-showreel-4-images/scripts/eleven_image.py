#!/usr/bin/env python3
"""Генерация изображения через ElevenLabs POST /v1/flows/image с опросом результата.
Ключ берётся только из переменной окружения ELEVENLABS_API_KEY.
Путь GET-запроса результата задаётся --status-path (смотри документацию ElevenLabs)."""
import argparse, json, os, sys, time, urllib.request

BASE = "https://api.elevenlabs.io"

def call(method, path, key, body=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

def main():
    a = argparse.ArgumentParser()
    a.add_argument("--model", required=True); a.add_argument("--prompt", required=True)
    a.add_argument("--aspect"); a.add_argument("--resolution"); a.add_argument("--seed", type=int)
    a.add_argument("--quality"); a.add_argument("--background")
    a.add_argument("--status-path", required=True, help="например /v1/flows/image/{id}; уточни в документации")
    a.add_argument("--out", required=True); a.add_argument("--timeout", type=int, default=300)
    a.add_argument("--dry-run", action="store_true")
    o = a.parse_args()
    body = {"model_id": o.model, "prompt": o.prompt}
    for k, v in (("aspect_ratio", o.aspect), ("resolution", o.resolution), ("seed", o.seed),
                 ("quality", o.quality), ("background", o.background)):
        if v is not None: body[k] = v
    if o.dry_run:
        print("POST", BASE + "/v1/flows/image"); print(json.dumps(body, ensure_ascii=False, indent=2)); return
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key: sys.exit("ELEVENLABS_API_KEY не задан в окружении")
    gen = call("POST", "/v1/flows/image", key, body)
    gid = gen["id"]; print("id:", gid, "status:", gen.get("status"))
    end = time.time() + o.timeout
    while time.time() < end:
        time.sleep(3)
        st = call("GET", o.status_path.replace("{id}", gid), key)
        s = st.get("status")
        print("status:", s)
        if s in ("failed", "error"): sys.exit("Генерация не удалась: " + json.dumps(st, ensure_ascii=False)[:500])
        if s in ("completed", "done", "succeeded", "ready"):
            os.makedirs(os.path.dirname(o.out) or ".", exist_ok=True)
            json.dump(st, open(o.out + ".response.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            print("Ответ сохранён в", o.out + ".response.json")
            print("Скачай изображение по ссылке из ответа в", o.out, "(структура ответа см. в документации GET)")
            return
    sys.exit("Таймаут ожидания генерации")

main()
