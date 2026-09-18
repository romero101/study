#!/usr/bin/env python3
"""Точечная доработка исходных лендингов с хостинга.

Берёт dist/<slug>-original/ (снимок того, что лежит на REG.RU) и собирает
dist/<slug>-v2/: те же вёрстка, фото и отзывы, плюс
  - картинки в WebP двух размеров, srcset, preload первого экрана;
  - мобильные правки (tools/enhance.css дописывается в конец style.css);
  - форма реально отправляет заявку в send.php, быстрый «перезвоните мне»;
  - send.php, policy.html, robots.txt, .htaccess.
Оригинал не меняется. Запуск: python3 tools/upgrade.py
"""
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
TOOLS = ROOT / "tools"

SITES = {
    "topdrillrus": {
        "brand": "ТопДриллРус", "demo": True, "email": "",
        "hero": "drilling-enhanced.jpg", "city": "Санкт-Петербург", "contact": "info@topdrill.ru",
    },
    "skvazhina-ekb": {
        "brand": "Скважина-вода", "demo": True, "email": "",
        "hero": "hero.jpg", "city": "Екатеринбург", "contact": "skvagina-voda@mail.ru",
    },
}
SMALL, LARGE = 640, 1280


def px_width(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", str(path)], capture_output=True, text=True).stdout
    return int(re.search(r"pixelWidth: (\d+)", out).group(1))


def make_images(src_dir, out_dir):
    """jpg -> облегчённый jpg (запасной) + webp 640 и до 1280. Возвращает {имя: [(файл, ширина)]}."""
    variants = {}
    for jpg in sorted(src_dir.glob("*.jpg")):
        w = px_width(jpg)
        big = min(w, LARGE)
        dst = out_dir / jpg.name
        subprocess.run(["sips", "-Z", str(max(big, 1)), "-s", "format", "jpeg", "-s", "formatOptions", "72",
                        str(jpg), "--out", str(dst)], capture_output=True, check=True)
        if px_width(dst) > big:  # -Z режет по большей стороне; для вертикальных кадров дожимаем по ширине
            subprocess.run(["sips", "--resampleWidth", str(big), str(dst)], capture_output=True, check=True)
        items = []
        for tw in sorted({min(SMALL, w), big}):
            name = f"{jpg.stem}-{tw}.webp"
            subprocess.run(["cwebp", "-quiet", "-q", "74", "-resize", str(tw), "0", str(jpg), "-o", str(out_dir / name)],
                           check=True)
            items.append((name, tw))
        variants[jpg.name] = items
    return variants


def must_sub(text, old, new, count=1):
    if old not in text:
        raise SystemExit(f"не найден фрагмент для замены: {old[:70]!r}")
    return text.replace(old, new, count)


def patch_html(html, cfg, variants):
    demo = cfg["demo"]

    def picture(m):
        tag, src = m.group(0), m.group(1)
        if src not in variants:
            return tag
        hero = src == cfg["hero"]
        sizes = "100vw" if hero else "(max-width:760px) 80vw, (max-width:1100px) 50vw, 34vw"
        srcset = ", ".join(f"{n} {w}w" for n, w in variants[src])
        if "decoding=" not in tag:
            tag = tag[:-1] + ' decoding="async">'
        return f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}">{tag}</picture>'

    html = re.sub(r'<img[^>]*\ssrc="([^"]+\.jpg)"[^>]*>', picture, html)
    # лайтбокс открывает большой webp, а не тяжёлый jpg
    html = re.sub(r'data-photo="([^"]+)\.jpg"',
                  lambda m: f'data-photo="{variants[m.group(1) + ".jpg"][-1][0]}"' if m.group(1) + ".jpg" in variants else m.group(0),
                  html)

    hero_set = ", ".join(f"{n} {w}w" for n, w in variants[cfg["hero"]])
    head = (f'<link rel="preload" as="image" type="image/webp" imagesrcset="{hero_set}" imagesizes="100vw" fetchpriority="high">'
            '<meta name="theme-color" content="#102c40"><meta name="format-detection" content="telephone=no">')
    if demo:
        head += '<meta name="robots" content="noindex,nofollow">'
    html = must_sub(html, '<link rel="stylesheet" href="style.css', head + '<link rel="stylesheet" href="style.css')
    html = re.sub(r'href="style\.css(\?v=\d+)?"', 'href="style.css?v=20260918"', html)
    html = must_sub(html, '<script src="app.js"></script>', '<script src="app.js?v=20260918" defer></script>')

    html = must_sub(html, 'Демонстрация · заявки не отправляются',
                    'Демонстрация · заявки получает студия «Форма сайта»' if demo else '')

    # форма: имена полей, ловушка для ботов, согласие, честная подпись
    html = must_sub(html, '<form id="lead-form">',
                    '<form id="lead-form" action="send.php" method="post" novalidate>'
                    '<input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">')
    html = must_sub(html, '<input id="location" ', '<input id="location" name="Участок" autocomplete="address-level2" ')
    html = must_sub(html, '<input id="name" ', '<input id="name" name="Имя" ')
    html = must_sub(html, '<input id="phone" type="tel" ', '<input id="phone" name="Телефон" type="tel" inputmode="tel" ')
    html = must_sub(html, '<textarea id="lead-summary" ', '<textarea id="lead-summary" name="Параметры" ')
    html = must_sub(html, 'Посмотреть готовую заявку <span>↗</span>', 'Отправить заявку <span>↗</span>')
    note = ('Демо-версия: заявка придёт в студию «Форма сайта», а не в компанию.' if demo
            else 'Перезвоним в рабочее время. Без обязательств.')
    html = must_sub(html, '<p class="hint">Демонстрационная форма: ничего не отправляет и не сохраняет на сервере.</p>',
                    f'<p class="hint">{note}</p><p class="consent">Нажимая кнопку, вы соглашаетесь с '
                    '<a href="policy.html" target="_blank" rel="noopener">политикой обработки персональных данных</a>.</p>')
    html = must_sub(html, 'Без обязательств. В демо данные останутся в браузере до закрытия страницы.',
                    'Без обязательств. Параметры подставятся в заявку — останется указать телефон.')

    # окно после отправки
    html = must_sub(html, '<p class="eyebrow">ЗАЯВКА ПОДГОТОВЛЕНА</p><h2>Всё нужное —<br>в одном сообщении.</h2>'
                          '<p>Это предпросмотр. Заявка не отправлена.</p>',
                    '<p class="eyebrow" id="lead-state">ЗАЯВКА ОТПРАВЛЕНА</p><h2 id="lead-title">Спасибо!<br>Мы перезвоним.</h2>'
                    '<p id="lead-note">Вот что мы получили:</p>')

    # панель связи: перезвоните мне — один телефон, без остальной формы
    html = must_sub(html, '<small>В этой концепции онлайн-чат ещё не подключён.</small>',
                    '<form class="callback" id="callback-form" novalidate>'
                    '<input type="tel" name="Телефон" id="callback-phone" inputmode="tel" autocomplete="tel" '
                    'placeholder="+7 (___) ___-__-__" aria-label="Ваш телефон" required>'
                    '<button type="submit">Перезвоните мне</button></form>'
                    '<p id="callback-status" role="status"></p>')
    html = must_sub(html, '<div class="mobile-bar"><a href="tel:', '<div class="mobile-bar"><a data-goal="call" href="tel:')
    html = html.replace('<a href="#calculator">Рассчитать ↗</a></div>',
                        '<a href="#request" data-open-contact>Перезвоните</a><a href="#calculator">Рассчитать ↗</a></div>')
    return html


def patch_js(js, cfg):
    js = must_sub(js, "$('final-summary').textContent=text;$('copy-status').textContent='';$('lead-dialog').showModal();});",
                  "sendLead(event.target,text);});")
    js = must_sub(js, "'Текст скопирован. Заявка не отправлена.'", "'Текст скопирован.'")
    return js + (TOOLS / "lead.js").read_text(encoding="utf-8").replace("__DEMO__", "true" if cfg["demo"] else "false")


def fill(text, cfg, slug):
    if "<html" in text:  # в политике __EMAIL__ — контакт оператора, в send.php — адрес для копий заявок
        text = text.replace("__EMAIL__", cfg["contact"]).replace("__CITY__", cfg["city"])
    return (text.replace("__BRAND__", cfg["brand"]).replace("__EMAIL__", cfg["email"])
            .replace("__DISALLOW__", "Disallow: /" if cfg["demo"] else "Allow: /")
            .replace("__CANONICAL__", f"https://{slug}.formasaita.ru/"))


def build(slug, cfg):
    src, out = DIST / f"{slug}-original", DIST / f"{slug}-v2"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for f in src.iterdir():
        if f.suffix not in (".jpg", ".css", ".js") and f.name != "index.html":
            shutil.copy2(f, out / f.name)
    variants = make_images(src, out)

    html = patch_html((src / "index.html").read_text(encoding="utf-8"), cfg, variants)
    (out / "index.html").write_text(html, encoding="utf-8")
    # <img> теперь внутри <picture>, поэтому правила вида «.hero-photo>img» переводим на потомка
    css = (src / "style.css").read_text(encoding="utf-8").replace(">img", " img") + (TOOLS / "enhance.css").read_text(encoding="utf-8")
    (out / "style.css").write_text(css, encoding="utf-8")
    (out / "app.js").write_text(patch_js((src / "app.js").read_text(encoding="utf-8"), cfg), encoding="utf-8")

    (out / "send.php").write_text(fill((TOOLS / "shared/send.php").read_text(encoding="utf-8"), cfg, slug), encoding="utf-8")
    for name in ("policy.html", "robots.txt", ".htaccess"):
        (out / name).write_text(fill((ROOT / "builder/shared" / name).read_text(encoding="utf-8"), cfg, slug), encoding="utf-8")

    size = lambda d: sum(f.stat().st_size for f in d.iterdir() if f.is_file())
    first = lambda d, names: sum((d / n).stat().st_size for n in names)
    print(f"{slug}: папка {size(src) // 1024} КБ -> {size(out) // 1024} КБ; "
          f"первый экран (html+css+js+фото) {first(src, ['index.html', 'style.css', 'app.js', cfg['hero']]) // 1024} КБ -> "
          f"{first(out, ['index.html', 'style.css', 'app.js', variants[cfg['hero']][0][0]]) // 1024} КБ на телефоне")


if __name__ == "__main__":
    for slug, cfg in SITES.items():
        build(slug, cfg)
