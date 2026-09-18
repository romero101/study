# -*- coding: utf-8 -*-
"""Аккуратные заглушки под фото: страница не даёт 404 и выглядит законченной,
а имена файлов совпадают с будущими реальными снимками — достаточно перезаписать."""
import os, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sites import ALL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def font(sz):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"):
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def hx(c): c = c.lstrip("#"); return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

def make(path, w, h, a, b, caption, sub):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    ca, cb = hx(a), hx(b)
    for y in range(h):                       # вертикальный градиент
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(ca[i] + (cb[i] - ca[i]) * t) for i in range(3)))
    step = max(28, w // 26)                  # лёгкая диагональная штриховка
    for x in range(-h, w + h, step):
        d.line([(x, 0), (x + h, h)], fill=tuple(min(255, c + 12) for c in cb), width=1)
    f1, f2 = font(max(20, w // 26)), font(max(14, w // 48))
    tw = d.textlength(caption, font=f1)
    d.text(((w - tw) / 2, h / 2 - w / 30), caption, font=f1, fill=(255, 255, 255))
    tw2 = d.textlength(sub, font=f2)
    d.text(((w - tw2) / 2, h / 2 + w / 60), sub, font=f2, fill=(255, 255, 255, 200))
    d.rectangle([6, 6, w - 7, h - 7], outline=tuple(min(255, c + 40) for c in cb), width=3)
    im.save(path, "JPEG", quality=70, optimize=True, progressive=True)
    return os.path.getsize(path)

total = 0
for s in ALL:
    out = os.path.join(ROOT, "dist", s["slug"], "img")
    os.makedirs(out, exist_ok=True)
    a, b = s["theme"]["HERO_A"], s["theme"]["HERO_B"]
    total += make(os.path.join(out, "hero.jpg"), 1600, 1200, a, b,
                  "hero.jpg", "заменить на главное фото объекта")
    for i, g in enumerate(s["gallery"], 1):
        total += make(os.path.join(out, g["file"]), 1200, 900, b, a,
                      g["file"], g["alt"][:54])
    print("%-14s заглушки готовы" % s["slug"])
print("итого %.0f КБ" % (total / 1024))
