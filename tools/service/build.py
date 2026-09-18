#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Движок лендингов для подрядчиков, у которых цена считается от длины или площади:
заборы, кровля, штукатурка и стяжка, септики. Один шаблон, один скрипт (tools/fence/app.js), клиент — JSON.

    python3 tools/service/build.py <slug>     # собрать dist/<slug>/
    python3 tools/service/build.py            # всех клиентов из tools/service/clients/*.json

Фото клиента — jpg/png в tools/service/clients/<slug>/. Правила студии зашиты в шаблон: первый экран — результат;
полоса фактов не повторяет карточки; цена видна до телефона; отзывы дословно с источником; расчёт — только в MAX.
"""
import json
import re
import shutil
import subprocess
import sys
from html import escape as e
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
V = "1"


def width(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", str(path)], capture_output=True, text=True).stdout
    return int(re.search(r"pixelWidth: (\d+)", out).group(1))


def webp(src_dir, out_dir):
    res = {}
    for f in sorted(list(src_dir.glob("*.jpg")) + list(src_dir.glob("*.jpeg")) + list(src_dir.glob("*.png"))):
        if f.stem == "logo":
            continue
        w = width(f)
        items = []
        for label in (640, 1280):  # имена фиксированные — их ждёт галерея в app.js; ширина не больше исходной
            tw, name = min(label, w), f"{f.stem}-{label}.webp"
            subprocess.run(["cwebp", "-quiet", "-q", "74", "-resize", str(tw), "0", str(f), "-o", str(out_dir / name)], check=True)
            items.append((f"img/{name}", tw))
        res[f.stem] = items
    return res


def pic(img, key, alt, sizes, cls="", eager=False):
    v = img[key]
    srcset = ", ".join(f"{n} {w}w" for n, w in v)
    attrs = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}"><img{c} src="{v[0][0]}" alt="{e(alt)}" {attrs}></picture>'


def tel(p):
    return "+" + re.sub(r"\D", "", p)


def build(slug):
    c = json.loads((HERE / "clients" / f"{slug}.json").read_text(encoding="utf-8"))
    out = ROOT / "dist" / slug
    if out.exists():
        shutil.rmtree(out)
    (out / "img").mkdir(parents=True)
    src = HERE / "clients" / slug
    img = webp(src, out / "img")
    logo = src / "logo.png"
    if logo.exists():
        shutil.copy2(logo, out / "img/logo.png")
    demo, phones, brand, calc = c["demo"], c["phones"], c["brand"], c["calc"]
    phone = phones[0]
    logo_tag = '<img src="img/logo.png" alt="" width="44" height="44">' if logo.exists() else f'<b class="mark">{e(c.get("mark", brand[:2].upper()))}</b>'
    hero_set = ", ".join(f"{n} {w}w" for n, w in img[c["hero"]["image"]])

    trust = "".join(f"<li><b>{e(b)}</b><span>{t}</span></li>" for b, t in c["trust"])
    cards = ""
    for t in c["cards"]:
        lis = "".join(f"<li>{e(x)}</li>" for x in t["points"])
        price = f'<p class="price">{e(t["price"])}<small>{e(t.get("per", ""))}</small></p>' if t.get("price") else ""
        cards += (f'<article class="type">{pic(img, t["image"], t["alt"], "(max-width:760px) 84vw, 33vw", "render" if t.get("render") else "")}'
                  f'<div><h3>{e(t["title"])}</h3>{price}<ul>{lis}</ul>'
                  f'<button class="button ghost" type="button" data-pick="{t["key"]}">Рассчитать ↗</button></div></article>')

    chips = "".join(f'<label><input type="radio" name="type" value="{k}"{" checked" if i == 0 else ""}><span>{e(t["chip"])}</span></label>'
                    for i, (k, t) in enumerate(calc["types"].items()))
    heights = ""
    if calc.get("heights"):
        hs = "".join(f'<label><input type="radio" name="height" value="{e(h)}"{" checked" if h == calc["heights"]["default"] else ""}><span>{e(h)}</span></label>'
                     for h in calc["heights"]["options"])
        heights = f'<fieldset class="chips"><legend>{e(calc["heights"]["legend"])}</legend>{hs}</fieldset>'
    extras = "".join(f'<label class="check"><input type="checkbox" id="{x["id"]}"><span>{e(x["label"])}</span></label>' for x in calc["extras"])
    color_box = ('<div id="color-box"><p class="legend">Цвет <span id="color-name"></span></p><div class="fence" aria-hidden="true">'
                 '<svg viewBox="0 0 320 90" preserveAspectRatio="none" id="fence-svg"></svg></div><div class="swatches" id="swatches" role="radiogroup" aria-label="Цвет"></div></div>'
                 if calc.get("colors") else "")
    plot = ('<button type="button" class="link" id="plot-help">Не знаю длину — посчитать по соткам</button>' if calc.get("by_plot") else f'<span>{e(calc.get("range_hint", ""))}</span>')
    plot_box = ('<div id="plot-box" hidden><label class="field" for="sotki">Участок, соток<input id="sotki" type="number" min="1" max="100" value="6" inputmode="decimal"></label>'
                '<p class="hint" id="plot-hint"></p></div>' if calc.get("by_plot") else "")
    max_btn = "Отправить расчёт в MAX" if c.get("max") else "Скопировать расчёт"

    feature = ""
    if c.get("feature"):
        f = c["feature"]
        photos = "".join(pic(img, k, f["title"], "(max-width:760px) 45vw, 25vw") for k in f["images"])
        facts = "".join(f"<div><b>{e(b)}</b>{e(t)}</div>" for b, t in f.get("facts", []))
        feature = (f'<section id="feature" class="tint"><div class="piles"><div class="piles-photos">{photos}</div><div><p class="eyebrow">{e(f["eyebrow"])}</p>'
                   f'<h2>{e(f["title"])}</h2><ul>{"".join(f"<li>{e(x)}</li>" for x in f["points"])}</ul><div class="depth">{facts}</div>'
                   f'<a class="button primary" href="#calc">{e(f["button"])} ↗</a></div></div></section>')

    filters = "".join(f'<button role="tab" aria-selected="false" data-filter="{k}">{e(n)}</button>' for k, n in c["works"]["filters"])
    steps = "".join(f"<li><h3>{e(t)}</h3><p>{e(p)}</p></li>" for t, p in c["steps"])
    guar = ""
    if c.get("guarantees"):
        guar = ('<section id="guarantee"><div class="head"><div><p class="eyebrow">ГАРАНТИИ</p><h2>' + e(c["guarantees"]["title"]) + '</h2></div></div><div class="guar">' +
                "".join(f'<div><b>0{i} / {e(g[0])}</b><h3>{e(g[1])}</h3><p>{e(g[2])}</p></div>' for i, g in enumerate(c["guarantees"]["items"], 1)) + "</div></section>")
    reviews = ""
    if c.get("reviews"):
        r = c["reviews"]
        quotes = "".join(f'<blockquote><p>{e(q["text"])}</p><footer><span class="ava">{e(q["name"][0].upper())}</span><span>{e(q["name"])}'
                         f'<small>{e(q["meta"])}</small></span></footer></blockquote>' for q in r["items"])
        reviews = (f'<section id="reviews" class="tint"><div class="head"><div><p class="eyebrow">ОТЗЫВЫ</p><h2>{e(r["title"])}</h2></div>'
                   f'<p>Приведены дословно, орфография авторов сохранена. Источник: <a href="{e(r["url"])}" target="_blank" rel="noopener">{e(r["source"])}</a>.</p></div>'
                   f'<div class="reviews">{quotes}</div></section>')
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in c["faq"])
    phones_html = "".join(f'<a class="big-phone" href="tel:{tel(p)}" data-goal="call">{e(p)}</a>' for p in phones)
    max_link = f'<a class="mail" href="{e(c["max"])}" target="_blank" rel="noopener" data-goal="max">Написать в MAX</a><br>' if c.get("max") else ""
    nav_reviews = '<a href="#reviews">Отзывы</a>' if reviews else ""
    demo_bar = '<div class="demo">Концепция нового сайта <span>Демонстрация · заявки получает студия «Форма сайта»</span></div>' if demo else ""
    form_note = "Демо-версия: заявка придёт в студию «Форма сайта», а не в компанию." if demo else "Перезвоним в рабочее время. Без обязательств."
    foot = ('<p>Концепция для обсуждения с компанией.<br>Не официальный сайт и не публичная оферта.</p>'
            f'<a href="{e(c["old_site"])}" target="_blank" rel="noopener">Действующий сайт ↗</a>' if demo else f'<p>{e(c.get("legal", ""))}</p>')

    html = f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(c["title"])}</title><meta name="description" content="{e(c["description"])}">
{'<meta name="robots" content="noindex,nofollow">' if demo else ""}<meta name="theme-color" content="{c["palette"]["ink"]}"><meta name="format-detection" content="telephone=no">
{'<link rel="icon" href="img/logo.png">' if logo.exists() else ""}
<link rel="preload" as="image" type="image/webp" imagesrcset="{hero_set}" imagesizes="100vw" fetchpriority="high">
<link rel="stylesheet" href="style.css?v={V}"></head>
<body>{demo_bar}
<header class="header"><a class="brand" href="#top">{logo_tag}<span>{e(brand.upper())}<small>{e(c["tagline"])}</small></span></a>
<nav aria-label="Разделы"><a href="#types">{e(c["nav_types"])}</a><a href="#calc">Калькулятор</a><a href="#works">Работы</a>{nav_reviews}<a href="#faq">Вопросы</a></nav>
<a class="header-phone" href="tel:{tel(phone)}" data-goal="call">{e(phone)}<small>{e(c["region"])}</small></a></header>
<main id="top">
<section class="hero">{pic(img, c["hero"]["image"], c["hero"]["alt"], "100vw", "hero-bg", True)}
<div class="hero-copy"><p class="eyebrow">{e(c["hero"]["eyebrow"])}</p><h1>{c["hero"]["h1"]}</h1><p class="intro">{c["hero"]["intro"]}</p>
<div class="actions"><a class="button primary" href="#calc">{e(c["hero"]["button"])} ↗</a><button class="text-button" type="button" data-start-quiz>{e(c["hero"]["quiz"])}</button></div></div></section>
<ul class="trust">{trust}</ul>

<section id="types"><div class="head"><div><p class="eyebrow">{e(c["types_eyebrow"])}</p><h2>{e(c["types_title"])}</h2></div><p>{e(c["types_note"])}</p></div>
<div class="types">{cards}</div>{f'<p class="also">{c["also"]} <a href="#request">Спросить цену →</a></p>' if c.get("also") else ""}</section>

<section id="calc" class="dark"><div class="head"><div><p class="eyebrow">КАЛЬКУЛЯТОР</p><h2>{e(calc["title"])}</h2></div>
<p>Двигайте ползунок — цена считается сразу. Телефон спросим только если захотите точную смету.</p></div>
<div class="calc"><div class="calc-in"><div class="tabs" role="tablist" aria-label="Способ расчёта">
<button role="tab" id="tab-calc" aria-selected="true" aria-controls="panel-calc">Знаю, что нужно</button><button role="tab" id="tab-quiz" aria-selected="false" aria-controls="panel-quiz" tabindex="-1">Помогите выбрать</button></div>
<div id="panel-calc" role="tabpanel" aria-labelledby="tab-calc"><fieldset class="chips" id="type-chips"><legend>{e(calc["type_legend"])}</legend>{chips}</fieldset>
<div class="field-title"><label for="len">{e(calc["len_label"])}</label><span class="number"><input id="len" type="number" min="{calc["min"]}" max="{calc["max"]}" value="{calc["default"]}" inputmode="numeric" aria-label="{e(calc["len_label"])}"> {e(calc["unit"])}</span></div>
<input id="len-range" type="range" min="{calc["min"]}" max="{calc["max"]}" value="{calc["default"]}" aria-label="{e(calc["len_label"])}">
<div class="range-label"><span>{calc["min"]} {e(calc["unit"])}</span>{plot}<span>{calc["max"]} {e(calc["unit"])}</span></div>{plot_box}{heights}
<fieldset class="checks"><legend>Что ещё нужно</legend>{extras}</fieldset>{color_box}</div>
<div id="panel-quiz" role="tabpanel" aria-labelledby="tab-quiz" hidden><div class="quiz-progress"><span id="quiz-step"></span><span>Подбор решения</span></div><div class="progress"><span id="quiz-fill"></span></div>
<form id="quiz-form" novalidate><div id="quiz-body"></div><div class="quiz-nav"><button class="link" type="button" id="quiz-back" hidden>← Назад</button><button class="button light" type="submit" id="quiz-next">Далее →</button></div>
<p class="error" id="quiz-error" role="alert"></p></form></div></div>
<aside class="calc-out" aria-live="polite"><span class="out-label" id="out-label">ПРЕДВАРИТЕЛЬНО</span><div class="out-price" id="out-price"></div><p id="out-formula"></p><div class="gift" id="gift"></div>
<ul class="included" id="out-list"></ul><p class="out-note">{e(calc["note"])}</p>
<button class="button primary" type="button" id="to-lead">Получить точную смету ↗</button><button class="button chat" type="button" id="share-calc">{max_btn}</button>
<p class="share-note" id="share-note" role="status"></p></aside></div></section>
{feature}
<section id="works"><div class="head"><div><p class="eyebrow">НАШИ РАБОТЫ</p><h2>{e(c["works"]["title"])}</h2></div><p>{e(c["works"]["note"])}</p></div>
<div class="filters" role="tablist" aria-label="Фильтр работ"><button role="tab" aria-selected="true" data-filter="all">Все</button>{filters}</div><div class="gallery" id="gallery"></div></section>

<section id="process" class="tint"><div class="head"><div><p class="eyebrow">КАК МЫ РАБОТАЕМ</p><h2>{e(c["steps_title"])}</h2></div></div><ol class="steps">{steps}</ol></section>
{guar}{reviews}
<section id="faq"{"" if reviews else ' class="tint"'}><div class="faq"><div><p class="eyebrow">ВОПРОСЫ</p><h2>Спрашивают до заказа.</h2></div><div>{faq}</div></div></section>

<section id="request" class="lead"><div><p class="eyebrow">ЗАЯВКА</p><h2>{e(c["lead"]["title"])}</h2><p>{e(c["lead"]["text"])}</p>{phones_html}{max_link}
<a class="mail" href="mailto:{e(c["email"])}">{e(c["email"])}</a><p class="addr">{e(c["address"])}</p></div>
<form id="lead-form" action="send.php" method="post" novalidate><input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
<label class="field" for="phone">Телефон<input id="phone" name="Телефон" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" required></label>
<label class="field" for="name">Имя <i>· необязательно</i><input id="name" name="Имя" maxlength="80" autocomplete="given-name" placeholder="Как к вам обращаться"></label>
<label class="field" for="place">{e(c["lead"]["place_label"])} <i>· необязательно</i><input id="place" name="Объект" maxlength="120" placeholder="{e(c["lead"]["place_hint"])}"></label>
<label class="field" for="summary">Расчёт<textarea id="summary" name="Параметры" rows="4" maxlength="2000"></textarea></label>
<button class="button primary" type="submit">{e(c["lead"]["button"])} ↗</button><p class="hint">{form_note}</p><p class="error" id="form-error" role="alert"></p>
<p class="consent">Нажимая кнопку, вы соглашаетесь с <a href="policy.html" target="_blank" rel="noopener">политикой обработки персональных данных</a>.</p></form></section></main>

<footer><a class="brand" href="#top">{logo_tag}<span>{e(brand.upper())}<small>{e(c["region"])}</small></span></a>{foot}</footer>
<div class="mobile-bar"><a href="tel:{tel(phone)}" data-goal="call">Позвонить</a><a href="#request" id="bar-chat">Заявка</a><a href="#calc">Цена ↗</a></div>
<dialog id="lead-dialog"><button class="close" type="button" data-close aria-label="Закрыть">×</button><p class="eyebrow" id="lead-state"></p><h2 id="lead-title"></h2><p id="lead-note"></p><pre id="lead-text"></pre></dialog>
<dialog id="photo-dialog"><button class="close" type="button" data-close aria-label="Закрыть фото">×</button><img id="photo-large" alt=""><p id="photo-caption"></p></dialog>
<script src="config.js?v={V}"></script><script src="app.js?v={V}" defer></script></body></html>
'''
    (out / "index.html").write_text(html, encoding="utf-8")

    site = {"demo": demo, "max": c.get("max", ""), "phone": phone,
            "types": {k: {"name": t["name"], "rate": t["rate"], "draw": t.get("draw", "prof")} for k, t in calc["types"].items()},
            "gifts": calc.get("gifts", []), "rows": calc["rows"], "colors": calc.get("colors", []), "questions": c["quiz"],
            "shots": c["works"]["shots"],
            "calc": {"unit": calc["unit"], "noun": calc["noun"], "min": calc["min"], "max": calc["max"], "posts": bool(calc.get("posts")),
                     "per": calc["per"], "hello": calc["hello"], "askLen": calc.get("ask_len", "Укажите размер"), "heightLabel": calc.get("height_label", "высота")}}
    (out / "config.js").write_text("/* Собрано tools/service/build.py из clients/%s.json — руками не править. */\nwindow.SITE = %s;\n"
                                   % (slug, json.dumps(site, ensure_ascii=False, indent=1)), encoding="utf-8")
    shutil.copy2(ROOT / "tools/fence/app.js", out / "app.js")

    css = (HERE / "style.css").read_text(encoding="utf-8")
    p = c["palette"]
    css = re.sub(r":root\{[^}]*\}", ":root{--ink:%s;--ink2:%s;--muted:%s;--acc:%s;--acc-d:%s;--paper:%s;--line:%s;--green:%s;--r:12px}"
                 % (p["ink"], p["ink2"], p["muted"], p["acc"], p["acc_d"], p["paper"], p["line"], p["accent2"]), css, count=1)
    css += ".brand .mark{display:grid;place-items:center;width:44px;height:44px;border-radius:10px;background:var(--ink);color:var(--acc);font-size:17px;letter-spacing:-.04em}\n"
    css += ".hero-bg{object-position:%s}\n@media(max-width:760px){.hero-bg{object-position:%s}}\n" % (c["hero"].get("position", "center"), c["hero"].get("mobile_position", "center"))
    if len(c["cards"]) == 4:
        css += "@media(min-width:1081px){.types{grid-template-columns:repeat(4,1fr)}}\n"
    (out / "style.css").write_text(css, encoding="utf-8")

    def fill(t, email):
        return (t.replace("__BRAND__", brand).replace("__CITY__", c["city"]).replace("__EMAIL__", email)
                .replace("__DISALLOW__", "Disallow: /" if demo else "Allow: /").replace("__CANONICAL__", c["canonical"]))
    (out / "send.php").write_text(fill((ROOT / "tools/shared/send.php").read_text(encoding="utf-8"), c.get("leads_email", "")), encoding="utf-8")
    (out / "policy.html").write_text(fill((ROOT / "builder/shared/policy.html").read_text(encoding="utf-8"), c["email"]), encoding="utf-8")
    for n in ("robots.txt", ".htaccess"):
        (out / n).write_text(fill((ROOT / "builder/shared" / n).read_text(encoding="utf-8"), ""), encoding="utf-8")
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file()) // 1024
    print(f"dist/{slug}: {size} КБ, html {len(html) // 1024} КБ, картинок {len(img)}")


if __name__ == "__main__":
    for s in (sys.argv[1:] or [p.stem for p in (HERE / "clients").glob("*.json")]):
        build(s)
