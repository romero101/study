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
        # Первый экран показывает результат (дом, газон, вода), а не грязь на стройплощадке:
        # замечание заказчика 18.09. Картинка сгенерирована; подпись убрана по просьбе заказчика.
        "swap": [("drilling-enhanced.jpg", "hero-result.jpg"),
                 ('alt="Буровая установка ТопДриллРус у загородного дома"', 'alt="Загородный дом, зелёный газон и вода из крана на участке"'),
                 ("<span>Фото компании · ИИ-ретушь</span>", "<span></span>")],
        "mobile_hero_pos": "72% center",
        "trust": [("1 829", "домов получили воду<br>в 2022 году"), ("до 5 лет", "гарантия<br>на скважину"), ("Pedrollo", "официальный дилер<br>насосов")],
        "cards": [("Бурение скважины", "Инженер бесплатно определяет место на участке. В цену метра входят трубы, бурение и прокачка. Четыре конструкции — от пластика до 50 м до бесшовной стали до 200 м. Гарантия 2–5 лет и паспорт скважины."),
                  ("Насос и автоматика", "ТопДриллРус — официальный дилер итальянских насосов Pedrollo. Подбор, поставка и монтаж — одна компания, без посредников. Расчёт оборудования под вашу скважину бесплатный."),
                  ("Подводка и очистка", "Водонапорная труба от скважины в дом, подключение системы. Фильтрацию подбирают по анализу воды. Через несколько дней после бурения инженер приезжает проверить, как работает скважина.")],

        "hero": "hero-result.jpg", "city": "Санкт-Петербург", "contact": "info@topdrill.ru",
    },
    "skvazhina-ekb": {
        "brand": "Скважина-вода", "demo": True, "email": "",
        "hero": "hero.jpg", "city": "Екатеринбург", "contact": "skvagina-voda@mail.ru",
        "trust": [("1 день", "на скважину<br>70–90 метров"), ("до 120 м", "малогабаритной<br>установкой"), ("0 ₽", "разберём и соберём<br>ваш забор")],
        "cards": [("Бурение скважины", "От 1 700 ₽ за метр малогабаритной установкой, глубина до 120 м. Скважину 70–90 м бурят за один день, работы начинаются сразу после заезда. Забор для заезда разберут и соберут бесплатно."),
                  ("Обустройство скважины", "От 20 000 ₽: монтаж кессона и насоса, обвязка и автоматика. Водоподъёмная труба с усиленной стенкой, обвязка внутри кессона — полипропиленом."),
                  ("Вода в доме и канализация", "Трубопровод от скважины в дом. Там же можно заказать автономную канализацию: септики Eurolos с монтажом и обслуживанием.")],

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


def rewrite_blocks(html, cfg):
    """Замечание заказчика 18.09: после первого экрана трижды подряд шла одна и та же тройка
    «бурение — насос — вода в дом» (полоса, подпись к схеме, карточки). Теперь полоса — это факты
    о компании с её сайта, схема показана один раз, а карточки раскрывают суть: что входит и почём."""
    html = re.sub(r'(<div class="trust-strip">.*?</a>)', lambda m: m.group(1).replace("<br>", " <br>"), html, count=1, flags=re.S)
    facts = cfg.get("trust")
    if facts:
        items = "".join(f"<div><strong>{b}</strong><span>{t.replace('<br>', ' <br>')}</span></div>" for b, t in facts)
        html, n = re.subn(r'(<div class="trust-strip"><a .*?</a>)(?:<div><strong>0\d</strong>.*?</div>){3}', lambda m: m.group(1) + items, html, count=1, flags=re.S)
        if n != 1:
            raise SystemExit("не нашёл полосу доверия")
    for i, (title, text) in enumerate(cfg.get("cards", []), 1):
        html, n = re.subn(r'(<span class="index">0%d / [^<]*</span>)<h3>.*?</h3><p>.*?</p>' % i,
                          lambda m: f"{m.group(1)}<h3>{title}</h3><p>{text}</p>", html, count=1, flags=re.S)
        if n != 1:
            raise SystemExit(f"не нашёл карточку решения {i}")
    if cfg.get("cards"):
        html = must_sub(html, "<span>ВОДА ПРОХОДИТ ПОНЯТНЫЙ ПУТЬ</span>", "<span>КАК ЭТО УСТРОЕНО</span>")
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
    over = TOOLS / "overrides" / slug
    if over.exists():
        variants.update(make_images(over, out))

    html = (src / "index.html").read_text(encoding="utf-8")
    for old, new in cfg.get("swap", []):
        html = must_sub(html, old, new)
    html = patch_html(rewrite_blocks(html, cfg), cfg, variants)
    (out / "index.html").write_text(html, encoding="utf-8")
    # <img> теперь внутри <picture>, поэтому правила вида «.hero-photo>img» переводим на потомка
    css = (src / "style.css").read_text(encoding="utf-8").replace(">img", " img") + (TOOLS / "enhance.css").read_text(encoding="utf-8")
    if cfg.get("mobile_hero_pos"):
        css += "@media(max-width:760px){.hero-bg{object-position:%s!important}}\n" % cfg["mobile_hero_pos"]
    (out / "style.css").write_text(css, encoding="utf-8")
    (out / "app.js").write_text(patch_js((src / "app.js").read_text(encoding="utf-8"), cfg), encoding="utf-8")

    (out / "send.php").write_text(fill((TOOLS / "shared/send.php").read_text(encoding="utf-8"), cfg, slug), encoding="utf-8")
    for name in ("policy.html", "robots.txt", ".htaccess"):
        (out / name).write_text(fill((ROOT / "builder/shared" / name).read_text(encoding="utf-8"), cfg, slug), encoding="utf-8")

    size = lambda d: sum(f.stat().st_size for f in d.iterdir() if f.is_file())
    first = lambda d, names: sum((d / n).stat().st_size for n in names if (d / n).exists())
    print(f"{slug}: папка {size(src) // 1024} КБ -> {size(out) // 1024} КБ; "
          f"первый экран (html+css+js+фото) {first(src, ['index.html', 'style.css', 'app.js', cfg['hero']]) // 1024} КБ -> "
          f"{first(out, ['index.html', 'style.css', 'app.js', variants[cfg['hero']][0][0]]) // 1024} КБ на телефоне")


if __name__ == "__main__":
    for slug, cfg in SITES.items():
        build(slug, cfg)
