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
    logo = next((src / n for n in ("logo.svg", "logo.png") if (src / n).exists()), src / "logo.png")
    if logo.exists():
        shutil.copy2(logo, out / "img" / logo.name)
    for v in src.glob("*.mp4"):                       # видео клиента (сжатое, для первого экрана)
        shutil.copy2(v, out / "img" / v.name)
    demo, phones, brand, calc = c["demo"], c["phones"], c["brand"], c["calc"]
    phone = phones[0]
    logo_tag = f'<img src="img/{logo.name}" alt="" class="logo-img">' if logo.exists() else f'<b class="mark">{e(c.get("mark", brand[:2].upper()))}</b>'
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

    TEAM_SIZES = "(max-width:760px) 45vw, 22vw"
    def note(block):
        return f'<p>{e(block["note"])}</p>' if block.get("note") else ""

    def card_grid(items, sizes="(max-width:760px) 84vw, 33vw"):
        return "".join(f'<article class="why">{pic(img, im, t, sizes)}<div><h3>{e(t)}</h3><p>{e(x)}</p></div></article>' for im, t, x in items)
    why = ""
    if c.get("why"):
        w = c["why"]
        why = (f'<section id="why"><div class="head"><div><p class="eyebrow">{e(w["eyebrow"])}</p><h2>{e(w["title"])}</h2></div>'
               f'{note(w)}</div><div class="whys">{card_grid(w["items"])}</div></section>')
    quote = ""
    if c.get("quote"):
        q = c["quote"]
        quote = (f'<section id="quote" class="tint"><div class="quote">{pic(img, q["image"], q["name"], "(max-width:760px) 90vw, 30vw")}'
                 f'<div><p class="eyebrow">{e(q["eyebrow"])}</p><blockquote class="big"><p>{e(q["text"])}</p></blockquote>'
                 f'<ul>{"".join(f"<li>{e(x)}</li>" for x in q.get("points", []))}</ul><p class="who"><b>{e(q["name"])}</b><small>{e(q["role"])}</small></p></div></div></section>')
    team = ""
    if c.get("team"):
        t = c["team"]
        team = (f'<section id="team"><div class="head"><div><p class="eyebrow">КОМАНДА</p><h2>{e(t["title"])}</h2></div>{note(t)}</div>'
                f'<div class="team">{"".join(f"<figure>{pic(img, im, n, TEAM_SIZES)}<figcaption><b>{e(n)}</b><small>{e(r)}</small></figcaption></figure>" for im, n, r in t["items"])}</div></section>')
    messengers = ""
    if c.get("messengers"):
        m = c["messengers"]
        links = "".join(f'<a class="button {cls}" href="{e(u)}" target="_blank" rel="noopener" data-goal="{g}">{e(lbl)}</a>' for cls, u, g, lbl in
                        ([("chat", c["max"], "max", "Написать в MAX")] if c.get("max") else []) + ([("ghost", m["telegram"], "tg", "Написать в Telegram")] if m.get("telegram") else []))
        messengers = (f'<section id="messengers" class="tint"><div class="msgr">{pic(img, m["image"], m["name"], "(max-width:760px) 60vw, 20vw")}'
                      f'<div><h2>{e(m["title"])}</h2><p>{e(m["text"])}</p><p class="who"><b>{e(m["name"])}</b><small>{e(m["role"])}</small></p><div class="actions">{links}</div></div></div></section>')
    place = ""
    if c.get("place"):
        pl = c["place"]
        photos = "".join(pic(img, k, cap, "(max-width:760px) 92vw, 30vw") for k, cap in pl["images"])
        facts = "".join(f"<li><b>{e(a)}</b><span>{e(x)}</span></li>" for a, x in pl.get("facts", []))
        mapf = (f'<iframe class="map" src="{e(pl["map"])}" loading="lazy" title="Карта: {e(pl.get("address", ""))}" allowfullscreen></iframe>' if pl.get("map") else "")
        place = (f'<section id="place" class="tint"><div class="head"><div><p class="eyebrow">{e(pl.get("eyebrow", "ГДЕ МЫ"))}</p><h2>{e(pl["title"])}</h2></div>{note(pl)}</div>'
                 f'<div class="place"><div class="place-map">{mapf}</div><div class="place-photos">{photos}</div><ul class="place-facts">{facts}</ul></div></section>')
    embeds = ""
    if c.get("embeds"):
        ev = c["embeds"]
        items = "".join(f'<figure class="embed"><button type="button" class="embed-face" data-embed="{e(it["id"])}" aria-label="Смотреть: {e(it["title"])}">{pic(img, it["poster"], it["title"], "(max-width:760px) 92vw, 30vw")}<span class="play" aria-hidden="true"></span></button>'
                        f'<figcaption><b>{e(it["title"])}</b>{f"<small>{e(it[chr(109)+chr(101)+chr(116)+chr(97)])}</small>" if it.get("meta") else ""}</figcaption></figure>' for it in ev["items"])
        embeds = (f'<section id="videos" class="tint"><div class="head"><div><p class="eyebrow">{e(ev.get("eyebrow", "ВИДЕО"))}</p><h2>{e(ev["title"])}</h2></div>{note(ev)}</div><div class="embeds">{items}</div></section>')
    videos = ""
    if c.get("videos"):
        vv = c["videos"]
        items = "".join(f'<figure class="vid"><video controls preload="none" playsinline poster="{img[po][0][0]}"><source src="img/{f}" type="video/mp4"></video>'
                        f'<figcaption><b>{e(n)}</b><small>{e(m)}</small></figcaption></figure>' for f, po, n, m in vv["items"])
        videos = (f'<section id="videos" class="tint"><div class="head"><div><p class="eyebrow">ВИДЕООТЗЫВЫ</p><h2>{e(vv["title"])}</h2></div>{note(vv)}</div>'
                  f'<div class="vids">{items}</div></section>')
    proofs = "".join(f'<div class="proof"><b>{e(b)}</b><span>{e(t)}</span></div>' for b, t in c["hero"].get("proofs", []))
    proofs = f'<div class="proofs">{proofs}</div>' if proofs else ""

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

    SEC = {
        'trust': f'''<ul class="trust">{trust}</ul>''',
        'types': f'''<section id="types"><div class="head"><div><p class="eyebrow">{e(c["types_eyebrow"])}</p><h2>{e(c["types_title"])}</h2></div><p>{e(c["types_note"])}</p></div>
<div class="types">{cards}</div>{f'<p class="also">{c["also"]} <a href="#request">Спросить цену →</a></p>' if c.get("also") else ""}</section>''',
        'calc': f'''<section id="calc" class="dark"><div class="head"><div><p class="eyebrow">КАЛЬКУЛЯТОР</p><h2>{e(calc["title"])}</h2></div>
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
<p class="share-note" id="share-note" role="status"></p></aside></div></section>''',
        'works': f'''<section id="works"><div class="head"><div><p class="eyebrow">НАШИ РАБОТЫ</p><h2>{e(c["works"]["title"])}</h2></div><p>{e(c["works"]["note"])}</p></div>
<div class="filters" role="tablist" aria-label="Фильтр работ"><button role="tab" aria-selected="true" data-filter="all">Все</button>{filters}</div><div class="gallery" id="gallery"></div></section>''',
        'process': f'''<section id="process" class="tint"><div class="head"><div><p class="eyebrow">КАК МЫ РАБОТАЕМ</p><h2>{e(c["steps_title"])}</h2></div></div><ol class="steps">{steps}</ol></section>''',
        'faq': f'''<section id="faq"{"" if reviews else ' class="tint"'}><div class="faq"><div><p class="eyebrow">ВОПРОСЫ</p><h2>Спрашивают до заказа.</h2></div><div>{faq}</div></div></section>''',
        'request': f'''<section id="request" class="lead"><div><p class="eyebrow">ЗАЯВКА</p><h2>{e(c["lead"]["title"])}</h2><p>{e(c["lead"]["text"])}</p>{phones_html}{max_link}
<a class="mail" href="mailto:{e(c["email"])}">{e(c["email"])}</a><p class="addr">{e(c["address"])}</p></div>
<form id="lead-form" action="send.php" method="post" novalidate><input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
<label class="field" for="phone">Телефон<input id="phone" name="Телефон" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" required></label>
<label class="field" for="name">Имя <i>· необязательно</i><input id="name" name="Имя" maxlength="80" autocomplete="given-name" placeholder="Как к вам обращаться"></label>
<label class="field" for="place">{e(c["lead"]["place_label"])} <i>· необязательно</i><input id="place" name="Объект" maxlength="120" placeholder="{e(c["lead"]["place_hint"])}"></label>
<label class="field" for="summary">Расчёт<textarea id="summary" name="Параметры" rows="4" maxlength="2000"></textarea></label>
<button class="button primary" type="submit">{e(c["lead"]["button"])} ↗</button><p class="hint">{form_note}</p><p class="error" id="form-error" role="alert"></p>
<p class="consent">Нажимая кнопку, вы соглашаетесь с <a href="policy.html" target="_blank" rel="noopener">политикой обработки персональных данных</a>.</p></form></section>''',
        'feature': feature, 'guarantee': guar, 'reviews': reviews, 'why': why, 'quote': quote, 'team': team, 'messengers': messengers, 'videos': videos, 'place': place, 'embeds': embeds,
    }
    ORDER = c.get('order', ['trust', 'types', 'calc', 'feature', 'works', 'process', 'guarantee', 'reviews', 'faq', 'request'])
    main_html = ''.join(SEC[k] for k in ORDER if SEC.get(k))

    html = f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(c["title"])}</title><meta name="description" content="{e(c["description"])}">
{'<meta name="robots" content="noindex,nofollow">' if demo else ""}<meta name="theme-color" content="{c["palette"]["ink"]}"><meta name="format-detection" content="telephone=no">
{f'<link rel="icon" href="img/{logo.name}">' if logo.exists() else ""}
<link rel="preload" as="image" type="image/webp" imagesrcset="{hero_set}" imagesizes="100vw" fetchpriority="high">
<link rel="stylesheet" href="style.css?v={V}"></head>
<body>{demo_bar}
<header class="header"><a class="brand{' brand--logo' if c.get('logo_only') else ''}" href="#top">{logo_tag}<span>{e(brand.upper())}<small>{e(c["tagline"])}</small></span></a>
<nav aria-label="Разделы"><a href="#types">{e(c["nav_types"])}</a><a href="#calc">Калькулятор</a><a href="#works">Работы</a>{nav_reviews}<a href="#faq">Вопросы</a></nav>
<a class="header-phone" href="tel:{tel(phone)}" data-goal="call">{e(phone)}<small>{e(c["region"])}</small></a></header>
<main id="top">
<section class="hero">{pic(img, c["hero"]["image"], c["hero"]["alt"], "100vw", "hero-bg", True)}{f'<video class="hero-video" autoplay muted loop playsinline preload="metadata" poster="{img[c["hero"]["image"]][0][0]}" aria-hidden="true"><source src="{c["hero"]["video"]}" type="video/mp4"></video>' if c["hero"].get("video") else ""}
<div class="hero-copy"><p class="eyebrow">{e(c["hero"]["eyebrow"])}</p><h1>{c["hero"]["h1"]}</h1><p class="intro">{c["hero"]["intro"]}</p>
<div class="actions"><a class="button primary" href="{c["hero"].get("href", "#request")}">{e(c["hero"]["button"])} ↗</a>{f'<button class="text-button" type="button" data-start-quiz>{e(c["hero"]["quiz"])}</button>' if c["hero"].get("quiz") else ""}</div>{proofs}</div></section>
{main_html}
</main>

<footer><a class="brand{' brand--logo' if c.get('logo_only') else ''}" href="#top">{logo_tag}<span>{e(brand.upper())}<small>{e(c["region"])}</small></span></a>{foot}</footer>
<div class="mobile-bar"><a href="tel:{tel(phone)}" data-goal="call">Позвонить</a><a href="#request" id="bar-chat">Заявка</a><a href="#calc">Расчёт ↗</a></div>
<dialog id="lead-dialog"><button class="close" type="button" data-close aria-label="Закрыть">×</button><p class="eyebrow" id="lead-state"></p><h2 id="lead-title"></h2><p id="lead-note"></p><pre id="lead-text"></pre></dialog>
<dialog id="photo-dialog"><button class="close" type="button" data-close aria-label="Закрыть фото">×</button><img id="photo-large" alt=""><p id="photo-caption"></p></dialog>
<script src="config.js?v={V}"></script><script src="app.js?v={V}" defer></script></body></html>
'''
    (out / "index.html").write_text(html, encoding="utf-8")

    site = {"demo": demo, "max": c.get("max", ""), "phone": phone,
            "types": {k: {kk: vv for kk, vv in {"name": v["name"], "rate": v.get("rate"), "draw": v.get("draw", "prof"), "steps": v.get("steps"), "install": v.get("install")}.items() if vv is not None or kk == "rate"} for k, v in calc["types"].items()},
            "gifts": calc.get("gifts", []), "filters": c["works"].get("filters", []), "rows": calc["rows"], "colors": calc.get("colors", []), "questions": c["quiz"],
            "shots": c["works"]["shots"], "extraRates": {x["id"]: x["rate"] for x in calc["extras"] if x.get("rate")},
            "extraFixed": {x["id"]: x["fixed"] for x in calc["extras"] if x.get("fixed")},
            "calc": {"unit": calc["unit"], "noun": calc["noun"], "min": calc["min"], "max": calc["max"], "posts": bool(calc.get("posts")),
                     "per": calc["per"], "hello": calc["hello"], "askLen": calc.get("ask_len", "Укажите размер"), "heightLabel": calc.get("height_label", "высота"), "lenPrefix": calc.get("len_prefix", "")}}
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
    import hashlib  # версии файлов по содержимому: css/js на хостинге кэшируются на 45 дней
    page = (out / "index.html").read_text(encoding="utf-8")
    for name in ("style.css", "app.js", "config.js"):
        page = page.replace(f"{name}?v={V}", f"{name}?v={hashlib.md5((out / name).read_bytes()).hexdigest()[:8]}")
    (out / "index.html").write_text(page, encoding="utf-8")
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file()) // 1024
    print(f"dist/{slug}: {size} КБ, html {len(html) // 1024} КБ, картинок {len(img)}")


if __name__ == "__main__":
    for s in (sys.argv[1:] or [p.stem for p in (HERE / "clients").glob("*.json")]):
        build(s)
