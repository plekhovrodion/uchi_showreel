#!/usr/bin/env python3
"""Проверка SVG-иконки Учи.ру: палитра, запреты, число цветов, слои."""
import argparse, re, sys
import xml.etree.ElementTree as ET

BASE = {"#6656F7","#ADA4FF","#DFD9FF","#362F73","#FE5C57","#FF8A86","#FFC5C3","#741E1B",
        "#FFCF24","#FFE16C","#FFFFA3","#6B501A","#FFFFFF","#2B1B78","#442BAB"}
TEEN = {"#FF6ED1","#FFB8E9","#FFDAF3","#702759","#BDF829","#DDFF88","#F3FFD7","#495822",
        "#5CB6FF","#B1DCFF","#D5ECFF","#2C475C"}
BAD_TAGS = {"lineargradient","radialgradient","filter","text","image","style","mask","feGaussianBlur".lower()}

def norm(c):
    c = c.strip()
    if re.fullmatch(r"#[0-9a-fA-F]{3}", c):
        c = "#" + "".join(ch*2 for ch in c[1:])
    return c.upper()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("svg"); ap.add_argument("--segment", choices=["kids","teen"], required=True)
    ap.add_argument("--type", choices=["plate","illustration"], default="plate")
    a = ap.parse_args()
    allowed = BASE | (TEEN if a.segment == "teen" else set())
    errs, warns, colors = [], [], set()
    root = ET.parse(a.svg).getroot()
    if not root.get("viewBox"): errs.append("нет viewBox")
    ids = set()
    for el in root.iter():
        tag = el.tag.split("}")[-1].lower()
        if tag in BAD_TAGS: errs.append(f"запрещённый элемент <{tag}>")
        if el.get("id"): ids.add(el.get("id"))
        for attr in ("fill","stroke","stop-color"):
            v = el.get(attr)
            if v is None or v in ("none","transparent"): continue
            if v.startswith("url("): errs.append(f"{attr}={v}: градиент или паттерн запрещён"); continue
            if v.lower() in ("black","currentcolor"): errs.append(f"{attr}={v}: чёрный/currentColor запрещён"); continue
            if not v.startswith("#"): errs.append(f"{attr}={v}: используй hex из палитры"); continue
            c = norm(v)
            if c == "#000000": errs.append("чёрный #000000 запрещён")
            elif c not in allowed: errs.append(f"{c} вне палитры ({a.segment})")
            colors.add(c)
        if el.get("filter"): errs.append("filter запрещён")
        if "opacity" in el.attrib and el.get("opacity") not in ("1","1.0"):
            warns.append("opacity <1: проверь, что цвет не выходит за палитру")
    counted = colors - {"#FFFFFF"}
    if a.type == "plate" and len(counted) > 3:
        errs.append(f"{len(counted)} цветов, максимум 3 (без белого): {sorted(counted)}")
    accents = sorted(i for i in ids if re.fullmatch(r"accent-\d+", i))
    if len(accents) > 3: errs.append(f"{len(accents)} акцентов, максимум 3")
    need = {"plate","symbol"} if a.type == "plate" else {"body"}
    missing = need - ids
    if missing: errs.append(f"нет слоёв с id: {sorted(missing)}")
    if a.segment == "kids" and colors & TEEN: errs.append("доп. цвета подростков в иконке для детей")
    for w in warns: print("WARN:", w)
    for e in errs: print("ERROR:", e)
    if not errs: print(f"OK: {len(counted)} цветов, акцентов {len(accents)}")
    sys.exit(1 if errs else 0)
main()
