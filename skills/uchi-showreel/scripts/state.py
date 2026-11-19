#!/usr/bin/env python3
"""Состояние и гейты проекта ролика. Использование: state.py <init|status|start|done|approve|skip|reset> <папка> [этап]"""
import argparse, datetime, json, os, sys

STAGES = ["preflight", "script", "gate_script", "assets", "gate_assets", "images", "voiceover", "animation"]
GATES = {"gate_script": "script", "gate_assets": "assets"}
SKIPPABLE = {"images"}

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
