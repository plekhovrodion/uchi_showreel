#!/usr/bin/env python3
"""Проверка ключа ElevenLabs. Ключ никогда не печатается.

Где ищется ключ (по порядку): переменная окружения ELEVENLABS_API_KEY, затем файл .env в
папке проекта, в текущей папке и её родителях (до 4 уровней), в ~/.config/uchi_showreel/.
Запуск: check_key.py [папка_проекта] [--offline]. Код выхода 0 только если ключ найден и не отклонён.
"""
import json, os, sys, urllib.error, urllib.request

NAME = "ELEVENLABS_API_KEY"

def find_key(extra_dirs=()):
    k = os.environ.get(NAME, "").strip()
    if k: return k, "переменная окружения"
    dirs = [d for d in extra_dirs if d]
    cur = os.path.abspath(os.getcwd())
    for _ in range(5):
        dirs.append(cur); cur = os.path.dirname(cur)
    dirs.append(os.path.expanduser("~/.config/uchi_showreel"))
    for d in dirs:
        p = os.path.join(d, ".env")
        if not os.path.isfile(p): continue
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line.startswith(NAME + "="):
                v = line.split("=", 1)[1].strip().strip("\"'")
                if v: return v, p
    return "", None

def check(extra_dirs=(), offline=False):
    key, src = find_key(extra_dirs)
    r = {"found": bool(key), "source": src, "format_ok": None, "valid": None, "message": ""}
    if not key:
        r["message"] = f"ключ не найден: впишите его в файл .env ({NAME}=...), образец в .env.example"
        return r
    r["format_ok"] = key.startswith("sk_") and len(key) >= 20 and " " not in key
    if not r["format_ok"]:
        r["message"] = "значение не похоже на ключ ElevenLabs (должен начинаться с sk_); проверьте .env, возможно там заглушка"
        return r
    if offline:
        r["message"] = "формат верный, сам ключ не проверялся (офлайн)"; return r
    try:
        req = urllib.request.Request("https://api.elevenlabs.io/v1/user", headers={"xi-api-key": key})
        urllib.request.urlopen(req, timeout=10); r["valid"] = True; r["message"] = "ключ принят ElevenLabs"
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            r["valid"] = False; r["message"] = f"ElevenLabs отклонил ключ (HTTP {e.code}): проверьте его в .env"
        else:
            r["message"] = f"ответ ElevenLabs {e.code}, ключ не подтверждён"
    except Exception:
        r["message"] = "до api.elevenlabs.io не достучаться, ключ не подтверждён (формат верный)"
    return r

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    res = check(args[:1], "--offline" in sys.argv)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    sys.exit(0 if res["found"] and res["format_ok"] and res["valid"] is not False else 1)
