#!/usr/bin/env python3
"""Состояние и гейты проекта ролика. Использование: state.py <init|status|start|done|approve|skip|reset> <папка> [этап]"""
import argparse, datetime, json, os, sys

STAGES = ["preflight", "script", "gate_script", "voiceover", "assets", "gate_assets", "images", "animation"]  # озвучка сразу после гейта 1: от неё зависит тайминг сцен
GATES = {"gate_script": "script", "gate_assets": "assets"}
SKIPPABLE = {"images"}
FONT_STAGES = {"assets", "animation"}
KEY_STAGES = {"images", "voiceover"}

def fonts_gate(a, s):
    f = os.path.join(a.dir, "fonts-check.json")
    if not os.path.exists(f):
        sys.exit("Нет fonts-check.json. Сначала: python3 skills/uchi-showreel-1-preflight/scripts/check_fonts.py " + a.dir)
    rep = json.load(open(f, encoding="utf-8"))
    if rep.get("ok"):
        s.pop("preview_fonts", None); return
    bad = "; ".join(i["required"] + ": " + i["message"] for i in rep["fonts"] if i["status"] != "ok")
    if not (a.preview_fonts and a.by):
        sys.exit(f"Шрифты не подходят ({bad}). Запросите файлы у человека. Продолжить на временных шрифтах можно только так: "
                 f"state.py start {a.dir} {a.stage} --preview-fonts --by \"человек согласился на временные шрифты\"")
    s["preview_fonts"] = {"by": a.by, "problems": bad, "at": now()}

def key_gate(a, s):
    """Перед генерацией изображений и озвучкой проверяет ключ ElevenLabs (файл .env или окружение)."""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "uchi-showreel-1-preflight", "scripts"))
    try:
        from check_key import check
    except ImportError:
        sys.exit("Не найден uchi-showreel-1-preflight/scripts/check_key.py: ставьте скиллы вместе")
    r = check([a.dir])
    if r["found"] and r["format_ok"] and r["valid"] is not False:
        s.pop("no_key", None)
        if r["valid"] is None: print("Внимание:", r["message"])
        return
    if not (a.no_key and a.by):
        sys.exit(f"Ключ ElevenLabs не годится: {r['message']}. Скопируйте .env.example в .env и впишите ELEVENLABS_API_KEY=... "
                 f"Если ключа нет и человек согласен на готовую запись или пропуск: state.py start {a.dir} {a.stage} --no-key --by \"<как согласился>\"")
    s["no_key"] = {"by": a.by, "problem": r["message"], "at": now()}

def path(d): return os.path.join(d, "state.json")
def load(d):
    if not os.path.exists(path(d)): sys.exit("Нет state.json. Сначала: state.py init " + d)
    return json.load(open(path(d), encoding="utf-8"))
def save(d, s): json.dump(s, open(path(d), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
def prev_open(s, st):
    for p in STAGES[:STAGES.index(st)]:
        if s["stages"][p]["status"] not in ("done", "skipped"): return p
    return None

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("dir"); ap.add_argument("stage", nargs="?")
    ap.add_argument("--by"); ap.add_argument("--note", default="")
    ap.add_argument("--preview-fonts", action="store_true", help="разрешить временные шрифты (только с --by: человек согласился)")
    ap.add_argument("--no-key", action="store_true", help="продолжить без ключа ElevenLabs (только с --by: человек согласился)")
    a = ap.parse_args()
    if a.cmd == "init":
        os.makedirs(a.dir, exist_ok=True)
        if os.path.exists(path(a.dir)): sys.exit("state.json уже есть")
        save(a.dir, {"project": os.path.basename(os.path.abspath(a.dir)), "created": now(),
                     "stages": {k: {"status": "todo"} for k in STAGES}}); print("Создан", path(a.dir)); return
    s = load(a.dir)
    if a.cmd == "status":
        for k in STAGES:
            e = s["stages"][k]; x = e.get("by") or e.get("note")
            print(f"{k:12} {e['status']}" + (f" ({x})" if x else ""))
        return
    if a.stage not in STAGES: sys.exit("Этап: " + ", ".join(STAGES))
    st = s["stages"][a.stage]
    if a.cmd == "start":
        if a.stage in GATES: sys.exit("Гейт утверждается командой approve")
        p = prev_open(s, a.stage)
        if p: sys.exit(f"Нельзя начать {a.stage}: сначала завершите {p}")
        if a.stage in FONT_STAGES: fonts_gate(a, s)
        if a.stage in KEY_STAGES: key_gate(a, s)
        st.update(status="doing", at=now())
    elif a.cmd == "done":
        if a.stage in GATES: sys.exit("Гейт утверждается командой approve")
        if st["status"] == "todo": sys.exit(f"Сначала state.py start {a.stage}")
        st.update(status="done", at=now(), note=a.note)
    elif a.cmd == "approve":
        if a.stage not in GATES: sys.exit("Гейты: " + ", ".join(GATES))
        if not a.by: sys.exit("Укажите --by: как человек подтвердил")
        if s["stages"][GATES[a.stage]]["status"] != "done": sys.exit(f"Сначала завершите {GATES[a.stage]}")
        st.update(status="done", at=now(), by=a.by)
    elif a.cmd == "skip":
        if a.stage not in SKIPPABLE: sys.exit("Пропустить можно только: " + ", ".join(SKIPPABLE))
        if not a.note: sys.exit("Укажите --note: причина")
        p = prev_open(s, a.stage)
        if p: sys.exit(f"Нельзя пропустить {a.stage}: сначала завершите {p}")
        st.update(status="skipped", at=now(), note=a.note)
    elif a.cmd == "reset":
        for k in STAGES[STAGES.index(a.stage):]: s["stages"][k] = {"status": "todo"}
    else: sys.exit("Команды: init status start done approve skip reset")
    save(a.dir, s); print(a.cmd, a.stage, "ok")

main()
