#!/usr/bin/env python3
"""Генерация изображения через ElevenLabs POST /v1/flows/image с опросом результата.
Ключ берётся только из переменной окружения ELEVENLABS_API_KEY.
Опрашивает GET /v1/flows/image/{id} и скачивает готовое изображение в --out (по content_url, без ключа)."""
import argparse, json, os, sys, time, urllib.request

BASE = "https://api.elevenlabs.io"

def call(method, path, key, body=None):
    req = urllib.request.Request(BASE + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"xi-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

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
    a.add_argument("--model", default="gemini-3.1-flash-image", help="model_id; для прозрачного фона gpt-image-1.5"); a.add_argument("--prompt", required=True)
    a.add_argument("--aspect"); a.add_argument("--resolution"); a.add_argument("--seed", type=int)
    a.add_argument("--quality"); a.add_argument("--background")
    a.add_argument("--status-path", default="/v1/flows/image/{id}")
    a.add_argument("--out", required=True); a.add_argument("--timeout", type=int, default=300)
    a.add_argument("--dry-run", action="store_true")
    o = a.parse_args()
    body = {"model_id": o.model, "prompt": o.prompt}
    if o.seed is not None and o.model.startswith("gpt-image"):
        print("Внимание: gpt-image-* не принимает seed (API отвечает 422), параметр пропущен", file=sys.stderr); o.seed = None
    for k, v in (("aspect_ratio", o.aspect), ("resolution", o.resolution), ("seed", o.seed),
                 ("quality", o.quality), ("background", o.background)):
        if v is not None: body[k] = v
    if o.dry_run:
        print("POST", BASE + "/v1/flows/image"); print(json.dumps(body, ensure_ascii=False, indent=2)); return
    key = _load_key()
    if not key: sys.exit("Ключ ElevenLabs не найден. Скопируйте .env.example в .env и впишите ELEVENLABS_API_KEY=... (или задайте переменную окружения). Проверка: skills/uchi-showreel-1-preflight/scripts/check_key.py")
    gen = call("POST", "/v1/flows/image", key, body)
    gid = gen["id"]; print("id:", gid, "status:", gen.get("status"))
    end = time.time() + o.timeout
    while time.time() < end:
        time.sleep(3)
        st = call("GET", o.status_path.replace("{id}", gid), key)
        s = st.get("status")
        print("status:", s)
        if s == "failed": sys.exit("Генерация не удалась: " + str(st.get("failure_reason")) + " " + str(st.get("error_message")))
        if s == "completed":
            os.makedirs(os.path.dirname(o.out) or ".", exist_ok=True)
            ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}.get(st.get("content_mime_type"), "")
            out = o.out if (not ext or o.out.lower().endswith(ext) or (ext == ".jpg" and o.out.lower().endswith(".jpeg"))) else os.path.splitext(o.out)[0] + ext
            with urllib.request.urlopen(st["content_url"], timeout=120) as r, open(out, "wb") as f:
                f.write(r.read())
            json.dump({k: v for k, v in st.items() if k != "content_url"}, open(out + ".response.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
            print("Сохранено:", out); return
    sys.exit("Таймаут ожидания генерации")

main()
