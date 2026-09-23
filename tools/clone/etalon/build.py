#!/usr/bin/env python3
"""Копия сайта клиента под новым брендом «Эталон-Ремонт» (просьба клиента: его сайт, новый бренд).
Берёт src/index.html (страница Tilda как есть), меняет название, логотип, фото людей и брендированные
картинки, кладёт результат в dist/etalon/. Всё прочее — вёрстка, тексты, скрипты Tilda — один в один.

    python3 tools/clone/etalon/build.py
"""
import re
import shutil
from pathlib import Path
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
OUT = ROOT / "dist" / "etalon"
ORIG = Path("/tmp/cs/all")          # исходные картинки страницы (скачаны по ссылкам из src/index.html)
GEN, EDIT, AS = HERE / "gen", HERE / "edit" / "out", HERE / "assets"

# --- фон убираем заливкой от краёв: для портретов на однотонном фоне
def cutout(src, tol=26):
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    px = im.load()
    ref = [px[0, 0], px[w - 1, 0]]
    seen = bytearray(w * h)
    stack = [(x, 0) for x in range(w)] + [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    def near(c):
        return any(abs(c[0] - r[0]) + abs(c[1] - r[1]) + abs(c[2] - r[2]) < tol * 3 for r in ref)
    mask = Image.new("L", (w, h), 255)
    mp = mask.load()
    while stack:
        x, y = stack.pop()
        i = y * w + x
        if seen[i]:
            continue
        seen[i] = 1
        if not near(px[x, y]):
            continue
        mp[x, y] = 0
        if x > 0: stack.append((x - 1, y))
        if x < w - 1: stack.append((x + 1, y))
        if y > 0: stack.append((x, y - 1))
        if y < h - 1: stack.append((x, y + 1))
    im.putalpha(mask.filter(ImageFilter.GaussianBlur(1.2)))
    return im


def cover(im, size, focus=(0.5, 0.35)):
    w, h = size
    s = max(w / im.width, h / im.height)
    r = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    x = round((r.width - w) * focus[0]); y = round((r.height - h) * focus[1])
    return r.crop((x, y, x + w, y + h))


def contain_bottom(im, orig, top=False):
    """вырезка человека на прозрачный холст исходного размера — туда же, где стоял человек в оригинале (по его альфа-каналу)"""
    size = orig.size
    a = orig.convert("RGBA").getchannel("A").point(lambda v: 255 if v > 200 else 0)   # только плотные пиксели: тени и подложки не считаем
    box = a.getbbox() or (0, 0, *size)
    bw, bh = box[2] - box[0], box[3] - box[1]
    s = bw / im.width if top else min(bw / im.width, bh / im.height)
    r = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    c = Image.new("RGBA", size, (0, 0, 0, 0))
    # top — поясной портрет на место ростового: во всю ширину, к верху; иначе к правому краю (подписи в макете слева)
    c.alpha_composite(r, (box[0], box[1]) if top else (box[2] - r.width, box[3] - r.height))
    return c


def fill_knees(im, orig, part=0.72):
    """фигура по колено на всю рамку оригинала: верхние part высоты фигуры, масштаб по высоте рамки, к низу, лишнее по бокам — срезать"""
    size = orig.size
    a = orig.convert("RGBA").getchannel("A").point(lambda v: 255 if v > 200 else 0)
    box = a.getbbox() or (0, 0, *size)
    bw, bh = box[2] - box[0], box[3] - box[1]
    fb = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
    fig = im.crop((fb[0], fb[1], fb[2], fb[1] + round((fb[3] - fb[1]) * part)))
    s = bh / fig.height
    r = fig.resize((round(fig.width * s), bh), Image.LANCZOS)
    if r.width > bw:
        x0 = (r.width - bw) // 2; r = r.crop((x0, 0, x0 + bw, bh))
    c = Image.new("RGBA", size, (0, 0, 0, 0))
    c.alpha_composite(r, (box[0] + (bw - r.width) // 2, box[1]))
    return c


def on_white(im, size, right_margin=60):
    """вырезанные люди на белом холсте исходного размера: во всю высоту, у правого края (в оригинале так же)"""
    w, h = size
    fb = im.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
    fig = im.crop(fb)
    sc = min((h * 0.97) / fig.height, (w * 0.62) / fig.width)
    r = fig.resize((round(fig.width * sc), round(fig.height * sc)), Image.LANCZOS)
    c = Image.new("RGBA", size, (255, 255, 255, 255))
    c.alpha_composite(r, (w - right_margin - r.width, h - r.height))
    return c.convert("RGB")


def fade_left(im, size):
    """как этапы на сайте: фото справа, слева уходит в белый"""
    w, h = size
    base = Image.new("RGB", size, "white")
    part = cover(im.convert("RGB"), (int(w * 0.62), h))
    grad = Image.linear_gradient("L").rotate(90, expand=True).resize((int(w * 0.62), h))  # слева 0 → справа 255
    grad = grad.point(lambda v: min(255, v * 2))
    base.paste(part, (w - part.width, 0), grad)
    return base


P = lambda n: Image.open(GEN / f"{n}.png")
# имя исходника (как в /tmp/cs/all: tildXXXX_имя) → как сделать замену
MAP = {
    # команда
    "tild6338_1_3-min.jpg": ("cover", "foreman"),          # руководитель строительного департамента
    "tild6138_2-min_2.jpg": ("cover", "architect"),        # архитектор
    "tild3632_3_1-min.jpg": ("cover", "engineer"),         # главный инженер
    "tild3430_4_1-min.jpg": ("cover", "designer"),         # главный дизайнер
    "tild6162_-min.png": ("knees", "director_full"),              # основатель
    "tild6339_-min.png": ("cut", "m_leader"),              # цитата руководителя (тот же человек, что в команде)
    "tild6235_Group_16_1-min.png": ("cut", "manager"),     # специалист по работе с клиентами
    "tild6636_-min_3.png": ("cut", "l_guarantee"),         # гарантии: двое мастеров
    # блок «Никаких сомнительных бригад»: три карточки
    "tild3932__2024-07-26_11170437.png": ("cover", "worker"),
    "tild3965__2024-07-26_11171753.png": ("cover", "a_pair"),
    "tild6238__2024-07-26_11172895.png": ("cover", "b_group"),
    # контакты: фото прораба и офиса
    "tild3464_photo.jpg": ("cover", "site1"), "tild3030_photo.jpg": ("cover", "site2"),
    "tild3265_1_1-min.jpg": ("cover", "office1"), "tild6237__2.jpg": ("cover", "office2"),
    # услуги и этапы — у каждого места свой снимок
    "tild3062__-min.jpg": ("cover", "d_design"),           # дизайн-проект
    "tild3431__-min.jpg": ("cover", "c_furniture"),        # комплектация мебелью
    "tild3430_photo.jpg": ("cover", "e_tiles"),            # карточка «Закупка материалов»
    "tild3831___.jpg": ("cover", "f_drill"),               # карточка «Ремонт под ключ»
    "tild6161__.jpg": ("fade", "h_survey"),                # этап 1: выезд прораба
    "tild6535__2024-07-20_22475627.png": ("fade", "k_supply"),   # этап 3: закупка
    "tild6566__2024-07-20_22545316.png": ("fade", "j_report"),   # этап 4: отчёты
    "tild6435__2024-07-20_23004039.png": ("fade", "n_quality"),  # этап 5: контроль качества
    "tild3135__2024-07-20_23155432.png": ("fade", "g_handover"), # этап 7: сдача
    # фирменный знак
    "tild3638__.jpg": ("mark", "black"), "tild6334____180.png": ("mark", "blue"), "tild6563_WhatsApp_Image_2022-.jpeg": ("mark", "blue"),
}


def save(im, stem):
    """Сохраняем компактно: без прозрачности — JPG до 1280 px, с прозрачностью — PNG до 1000 px в 256 цветов"""
    import hashlib
    alpha = im.mode == "RGBA" and im.getchannel("A").getextrema()[0] < 255
    if alpha:
        im = im.copy(); im.thumbnail((1000, 1000), Image.LANCZOS)
        out = OUT / "img" / f"{stem}.png"
        im.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(out, optimize=True)
    else:
        im = im.convert("RGB"); im.thumbnail((1280, 1280), Image.LANCZOS)
        out = OUT / "img" / f"{stem}.jpg"
        im.save(out, quality=80, optimize=True, progressive=True)
    final = out.with_name(f"{out.stem}-{hashlib.md5(out.read_bytes()).hexdigest()[:6]}{out.suffix}")  # хеш в имени: хостинг кэширует картинки надолго
    out.rename(final)
    return f"{BASE}img/{final.name}"   # абсолютный путь: картинки общие для главной и вложенных страниц


def make(name, how, what):
    size = Image.open(ORIG / name).size
    if how == "cover":
        im = cover(P(what).convert("RGB"), size)
    elif how in ("cut", "cut_top"):
        im = contain_bottom(Image.open(HERE / "cut" / f"{what}.png").convert("RGBA"), Image.open(ORIG / name), how == "cut_top")   # вырезано Vision (cut/cutout.swift)
    elif how == "knees":
        im = fill_knees(Image.open(HERE / "cut" / f"{what}.png").convert("RGBA"), Image.open(ORIG / name))
    elif how == "fade":
        im = on_white(Image.open(HERE / "cut" / f"{what}.png").convert("RGBA"), size)
    elif how == "mark":
        m = Image.open(AS / f"mark-{what}.png").convert("RGBA").resize(size, Image.LANCZOS)
        im = m if name.endswith(".png") else Image.alpha_composite(Image.new("RGBA", size, "white"), m).convert("RGB")
    return save(im, Path(name).stem)


POLISH_CSS = """<style id="etalon-polish">
/* только гибкие блоки Tilda: зеро-блоки расставлены по пикселям, их кегли трогать нельзя — текст наезжает */
.t-submit,.t-btn,.t-form__submit .t-submit{font-size:16px!important;min-height:56px!important;letter-spacing:.02em}
.t-descr_xxs{font-size:14px}.t-descr_xs{font-size:16px}
.t-input{font-size:16px!important}
</style>"""


def polish(html):
    return html.replace("</head>", POLISH_CSS + "</head>", 1)


# 3. страницы копии: файл в src → папка в dist
PAGES = {"index.html": "", "project.html": "project/", "terms.html": "terms/"}
BASE = "/demo/etalon/"


def relink(html):
    html = re.sub(r'href=(["\'])/(project|terms)\1', lambda m: f"href={m.group(1)}{BASE}{m.group(2)}/{m.group(1)}", html)
    html = re.sub(r'href=(["\'])/(#[^"\']*)?\1', lambda m: f"href={m.group(1)}{BASE}{m.group(2) or ''}{m.group(1)}", html)
    return html.replace('href="https://xn-----7kcpdogkc1bbaponda3s.xn--p1ai"', f'href="{BASE}"')


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "img").mkdir(parents=True)
    local = {n: make(n, *v) for n, v in MAP.items()}
    for f in sorted(EDIT.glob("*")) if EDIT.exists() else []:        # картинки, где логотип заменил Codex
        if f.name in local or f.name.startswith("_"):
            continue
        orig = Image.open(ORIG / f.name)
        im = Image.open(f).convert("RGBA")
        im = im.resize(orig.size, Image.LANCZOS) if im.size != orig.size else im
        local[f.name] = save(im, Path(f.name).stem)
    shutil.copy2(AS / "logo.svg", OUT / "img" / "logo.svg")
    if (AS / "shot.png").exists():                                    # мокап «сайт на ноутбуке»: снимок первого экрана копии
        local["tild3933__2024-07-16_21100170.png"] = save(Image.open(AS / "shot.png"), "tild3933__2024-07-16_21100170")

    url = re.compile(r"https://(?:static|thb|optim)\.tildacdn\.com/(tild[0-9a-f]{4})[0-9a-f-]*/(?:-/[a-z]+/(?:[0-9x]+/)?)*([^'\"\s)?]+)")
    n = 0
    for src_name, sub in PAGES.items():
        s = (HERE / "src" / src_name).read_text(encoding="utf-8")
        s, k = url.subn(lambda m: local.get(f"{m.group(1)}_{m.group(2)}", m.group(0)), s); n += k
        s = s.replace("https://static.tildacdn.com/tild3237-3461-4435-b666-666161616637/-Black.svg", BASE + "img/logo.svg")
        for a, b in [
            ("«Экспресс-дизайн» \u00a0— это наш бренд", "«Эталон-Ремонт» — это наш бренд"),
            ("Экспресс Дизайн", "Эталон-Ремонт"), ("Экспресс-дизайн", "Эталон-Ремонт"),
            ("Федеральная сеть студий дизайна и ремонта №1 в России и СНГ", "Студия дизайна и ремонта в Нижнем Новгороде"),
            ("Сайт экспресс-дизайн-нн носит", "Сайт носит"),
            ("Разработали дизайн-проект почти в каждой пятой новостройке Москвы и области", "Ведём объекты в Нижнем Новгороде и области"),
        ]:
            s = s.replace(a, b)
        s = re.sub(r"«Эталон-Ремонт»\s*—&nbsp;это наш бренд.*?работать качественно",
                   "«Эталон-Ремонт» —&nbsp;это наш новый бренд. Эталон —&nbsp;образец, по&nbsp;которому сверяют качество: "
                   "так мы и&nbsp;работаем —&nbsp;фиксируем смету и&nbsp;сроки в&nbsp;договоре, принимаем каждый этап вместе с&nbsp;вами "
                   "и&nbsp;отвечаем за&nbsp;результат гарантией до&nbsp;5&nbsp;лет", s, flags=re.S)
        s = s.replace('href="https://journal.express-diz.ru/"', 'href="#"')
        s = s.replace("ООО «Эталон-Ремонт»", "ООО «Экспресс Дизайн»")  # ИНН и ОГРН настоящие — название юрлица не выдумываем
        s = s.replace("<head>", '<head><meta name="robots" content="noindex,nofollow">', 1)
        s = polish(relink(s))
        d = OUT / sub
        d.mkdir(parents=True, exist_ok=True)
        (d / "page.html").write_text(s, encoding="utf-8")
        shutil.copy2(HERE / "gate" / ("index.php" if not sub else "sub.php"), d / "index.php")
    for f in ("gate.php", ".htaccess"):
        shutil.copy2(HERE / "gate" / f, OUT / f)
    s = (OUT / "page.html").read_text(encoding="utf-8")
    left = sorted(set(re.findall(r"[Ээ]кспресс[ -][Дд]изайн[^<\"']{0,20}", s)))
    print(f"ссылок на картинки заменено: {n}; своих файлов: {len(local)}; старое название осталось: {left or 'нет'}")


if __name__ == "__main__":
    main()
