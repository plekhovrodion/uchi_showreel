#!/usr/bin/env python3
"""Проверка фирменных шрифтов Учи.ру у пользователя.
Ищет файлы в <проект>/assets/fonts, в --fonts-dir и в системе (fc-list), читает метаданные
и проверяет: семейство, начертание (вес), покрытие кириллицы. Пишет <проект>/fonts-check.json.
Код выхода: 0 — все шрифты подходят, 1 — чего-то не хватает или найдено не то начертание."""
import argparse, glob, json, os, re, shutil, subprocess, sys

EXT = {".otf", ".ttf", ".woff", ".woff2", ".ttc"}
CYR = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
NUM = "0123456789"
REQ = [
    {"role": "заголовки", "family": "Oceanic Grotesk Condensed", "style": "ExtraBold", "weight": 800},
    {"role": "подписи и основной текст", "family": "Factor A", "style": "Regular", "weight": 400},
]

def norm(s): return re.sub(r"[\s_\-]+", "", (s or "").lower())

def candidates(dirs):
    files = set()
    for d in dirs:
        for p in glob.glob(os.path.join(d, "**", "*"), recursive=True):
            if os.path.splitext(p)[1].lower() in EXT: files.add(p)
    if shutil.which("fc-list"):
        # шрифт может называться иначе, чем файл: ищем по семейству
        out = subprocess.run(["fc-list", "--format", "%{file}|%{family}\n"], capture_output=True, text=True).stdout
        for ln in out.splitlines():
            p, _, fam = ln.partition("|")
            if re.search(r"oceanic|factor", fam, re.I) and os.path.splitext(p)[1].lower() in EXT: files.add(p)
    return sorted(files)

def read(path):
    from fontTools.ttLib import TTFont, TTCollection
    res = []
    fonts = TTCollection(path).fonts if path.lower().endswith(".ttc") else [TTFont(path, lazy=True)]
    for f in fonts:
        nm = f["name"]
        g = lambda i: (nm.getDebugName(i) or "")
        fam = g(16) or g(1); sub = g(17) or g(2)
        w = f["OS/2"].usWeightClass if "OS/2" in f else None
        cmap = f.getBestCmap() or {}
        res.append({"file": path, "family": fam, "style": sub, "full": g(4), "weight": w,
                    "cyrillic": all(ord(c) in cmap for c in CYR), "digits": all(ord(c) in cmap for c in NUM)})
    return res

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?", default=".")
    ap.add_argument("--fonts-dir", action="append", default=[])
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    try:
        import fontTools  # noqa
    except ImportError:
        sys.exit("Нужен fontTools (pip install fonttools): без него нельзя проверить начертание и кириллицу")
    dirs = [os.path.join(a.project, "assets", "fonts")] + a.fonts_dir
    found, errors = [], []
    for p in candidates(dirs):
        try: found += read(p)
        except Exception as e: errors.append(f"{p}: {e}")
    report, ok_all = [], True
    for r in REQ:
        fam = [f for f in found if norm(r["family"]) in norm(f["family"]) or norm(r["family"]) in norm(f["full"])]
        exact = [f for f in fam if (f["weight"] == r["weight"] or norm(r["style"]) in norm(f["style"]) + norm(f["full"]))]
        item = {"role": r["role"], "required": f'{r["family"]} {r["style"]}'}
        if not fam:
            item.update(status="missing", message="Файл шрифта не найден"); ok_all = False
        elif not exact:
            item.update(status="wrong_style", message="Семейство есть, но нужного начертания нет. Найдено: " +
                        ", ".join(sorted({f'{f["style"] or "?"} (вес {f["weight"]})' for f in fam})), found=[f["file"] for f in fam]); ok_all = False
        else:
            good = [f for f in exact if f["cyrillic"] and f["digits"]]
            if not good:
                item.update(status="no_cyrillic", message="Нужное начертание найдено, но в нём нет полной кириллицы или цифр", found=[f["file"] for f in exact]); ok_all = False
            else:
                item.update(status="ok", file=good[0]["file"], message="Подходит")
        report.append(item)
    out = {"ok": ok_all, "fonts": report, "unreadable": errors}
    os.makedirs(a.project, exist_ok=True)
    json.dump(out, open(os.path.join(a.project, "fonts-check.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if not a.quiet:
        for i in report: print(f'{"OK " if i["status"]=="ok" else "ОШИБКА"} {i["required"]} ({i["role"]}): {i["message"]}' + (f' → {i["file"]}' if i.get("file") else ""))
        for e in errors: print("Не прочитан:", e)
        print("Шрифты:", "подходят" if ok_all else "НЕ ПОДХОДЯТ. Нужны OTF, TTF или WOFF2 в assets/fonts/ (скачать: гайдбук Учи.ру, раздел «Типографика», кнопка «Скачать шрифты»)")
    sys.exit(0 if ok_all else 1)

main()
