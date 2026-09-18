# -*- coding: utf-8 -*-
"""Сборка всех площадок: python3 builder/build.py -> dist/<slug>/"""
import os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import build
from sites import ALL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
SHARED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shared")

def main():
    for s in ALL:
        out = os.path.join(DIST, s["slug"])
        os.makedirs(os.path.join(out, "img"), exist_ok=True)
        html = build(s)
        with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
        for name in os.listdir(SHARED):
            src = os.path.join(SHARED, name)
            if os.path.isfile(src):
                dst = os.path.join(out, name)
                txt = open(src, encoding="utf-8").read()
                txt = txt.replace("__BRAND__", s["brand"]).replace("__EMAIL__", s["email"])
                txt = txt.replace("__CANONICAL__", s["canonical"]).replace("__CITY__", s["city"])
                txt = txt.replace("__DISALLOW__", "Disallow: /" if s["demo"] else "Allow: /")
                open(dst, "w", encoding="utf-8").write(txt)
        readme = os.path.join(out, "img", "ПОЛОЖИТЬ-СЮДА-ФОТО.txt")
        need = ["hero.jpg — главное фото, 1600×1200, до 250 КБ"] + [
            "%s — %s" % (g["file"], g["alt"]) for g in s["gallery"]]
        open(readme, "w", encoding="utf-8").write(
            "Файлы должны называться ровно так (jpg, sRGB, ширина 1600, качество 72):\n\n"
            + "\n".join("  " + n for n in need)
            + "\n\nЕсли файла нет — блок сам скрывается, страница не ломается.\n")
        print("%-14s %6.1f КБ  %s" % (s["slug"], len(html.encode()) / 1024, out))

if __name__ == "__main__":
    main()
