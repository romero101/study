#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Движок лендингов для буровых компаний (скважины на воду).

Дизайн и логика — одобренный заказчиком вариант ТопДриллРус; всё, что отличает клиента, лежит в
tools/well/clients/<slug>.json, фотографии — в tools/well/clients/<slug>/ (jpg).

    python3 tools/well/build.py <slug>      # собрать dist/well-<slug>/
    python3 tools/well/build.py             # собрать всех клиентов

Правила студии, зашитые в шаблон: первый экран — результат, а не стройплощадка; полоса фактов не
повторяет карточки услуг; отзывы — дословно с источником; альбомы работ листаются на странице;
расчёт цены виден до телефона; заявки уходят в send.php; мессенджер — только MAX.
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
SHARED = ROOT / "builder/shared"
V = "20260918"


def width(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", str(path)], capture_output=True, text=True).stdout
    return int(re.search(r"pixelWidth: (\d+)", out).group(1))


def webp(src_dir, out_dir):
    """Каждый jpg клиента -> webp 640 и до 1280. Возвращает {имя без расширения: [(файл, ширина), ...]}."""
    res = {}
    for jpg in sorted(src_dir.glob("*.jpg")):
        w = width(jpg)
        items = []
        for tw in sorted({min(640, w), min(1280, w)}):
            name = f"{jpg.stem}-{tw}.webp"
            subprocess.run(["cwebp", "-quiet", "-q", "74", "-resize", str(tw), "0", str(jpg), "-o", str(out_dir / name)], check=True)
            items.append((name, tw))
        res[jpg.stem] = items
    return res


def picture(img, key, alt, sizes, cls="", eager=False):
    v = img[key]
    srcset = ", ".join(f"{n} {w}w" for n, w in v)
    attrs = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
            f'<img{c} src="{v[-1][0]}" alt="{e(alt)}" {attrs}></picture>')


def tel(phone):
    return "+" + re.sub(r"\D", "", phone)


def build(slug):
    c = json.loads((HERE / "clients" / f"{slug}.json").read_text(encoding="utf-8"))
    out = ROOT / "dist" / f"well-{slug}"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    img = webp(HERE / "clients" / slug, out)
    demo, phone, brand = c["demo"], c["phone"], c["brand"]
    hero_set = ", ".join(f"{n} {w}w" for n, w in img[c["hero"]["image"]])

    trust = "".join(f"<div><strong>{e(b)}</strong><span>{t}</span></div>" for b, t in c["trust"])
    cards = ""
    for i, card in enumerate(c["cards"], 1):
        action = ('<a href="#calculator">Рассчитать бурение ↗</a>' if i == 1 else
                  f'<button class="text-button" data-package="{"pump" if i == 2 else "house"}">Добавить в заявку ↗</button>')
        cards += f'<article><span class="index">0{i} / {e(card["tag"])}</span><h3>{e(card["title"])}</h3><p>{e(card["text"])}</p>{action}</article>'
    options = "".join(f'<option value="{k}">{e(r["label"])} · до {r["limit"]} м</option>' for k, r in c["rates"].items())
    first = next(iter(c["rates"].values()))
    depth0 = min(40, first["limit"])
    estimate = (f'{depth0 * first["min"]:,}'.replace(",", " ") + (f'–{depth0 * first["max"]:,}'.replace(",", " ") if first.get("max") else "")) if first.get("min") else "По запросу"

    albums = ""
    for a in c["albums"]:
        files = [img[k] for k in a["photos"]]
        albums += (f'<article class="work-card"><button class="work-image" data-album="{",".join(f[-1][0] for f in files)}" '
                   f'data-caption="{e(a["title"])} — {e(a["sub"])}" aria-label="Открыть альбом: {e(a["title"])}, {len(files)} фото">'
                   f'{picture(img, a["photos"][0], a["title"] + ": " + a["sub"], "(max-width:760px) 80vw, 34vw")}'
                   f'<span class="album-count">{len(files)} фото</span></button><div><h3>{e(a["title"])}</h3><p>{e(a["sub"])}</p></div></article>')

    steps = "".join(f'<li><span>0{i}</span><div><h3>{e(t)}</h3><p>{e(p)}</p></div></li>' for i, (t, p) in enumerate(c["steps"], 1))
    r = c["reviews"]
    quotes = "".join(
        f'<article class="review-card"><div class="review-person"><span class="avatar">{e(q["name"][0])}</span><div><b>{e(q["name"])}</b>'
        f'<small>{e(q["date"])}</small></div><span class="review-platform">{e(r["badge"])}</span></div>'
        f'<div class="review-stars" aria-label="Оценка {q.get("stars", 5)} из 5">{"★" * q.get("stars", 5)}</div>'
        f'<p class="review-quote">«{e(q["text"])}»</p><a href="{e(r["url"])}" target="_blank" rel="noopener">Прочитать оригинал ↗</a></article>'
        for q in r["items"])
    faq = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in c["faq"])
    chat = (f'<a href="{e(c["max"])}" target="_blank" rel="noopener" data-goal="max">Написать в MAX</a>' if c.get("max") else "")
    demo_bar = ('<div class="demo">Концепция нового сайта <span>Демонстрация · заявки получает студия «Форма сайта»</span></div>' if demo else "")
    form_note = ("Демо-версия: заявка придёт в студию «Форма сайта», а не в компанию." if demo else "Перезвоним в рабочее время. Без обязательств.")
    footer_note = ("<p>Концепция для обсуждения с компанией.<br>Не официальный сайт и не коммерческое предложение.</p>"
                   f'<a href="{e(c["old_site"])}" target="_blank" rel="noopener">Действующий сайт ↗</a>' if demo else f"<p>© {e(brand)}</p>")
    site = {"demo": demo, "rates": c["rates"], "priceNote": c["calc"]["note_short"], "place": c["place"]}

    html = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(c["title"])}</title><meta name="description" content="{e(c["description"])}">
{'<meta name="robots" content="noindex,nofollow">' if demo else ""}<meta name="theme-color" content="#102c40"><meta name="format-detection" content="telephone=no">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23142735'/%3E%3Cpath d='M14 17h36v9H37v25H27V26H14z' fill='%23d9f477'/%3E%3C/svg%3E">
<link rel="preload" as="image" type="image/webp" imagesrcset="{hero_set}" imagesizes="100vw" fetchpriority="high">
<link rel="stylesheet" href="style.css?v={V}"></head><body>{demo_bar}
<header class="header"><a class="brand" href="#"><b class="mark">{e(c["mark"])}<span>↘</span></b><span>{e(brand.upper())}<small>{e(c["tagline"])}</small></span></a>
<nav aria-label="Основная навигация"><a href="#solutions">Решения</a><a href="#calculator">Расчёт</a><a href="#works">Наши работы</a><a href="#reviews">Отзывы</a></nav>
<a class="header-phone" href="tel:{tel(phone)}">{e(phone)}<small>{e(c["region"])}</small></a></header>
<main><section class="hero hero-new">{picture(img, c["hero"]["image"], c["hero"]["alt"], "100vw", "hero-bg", True)}
<div class="hero-copy"><p class="eyebrow">{e(c["region"].upper())}</p><h1>{c["hero"]["h1"]}</h1><p class="intro">{c["hero"]["intro"]}</p>
<div class="actions"><a class="button primary" href="#calculator">Рассчитать мой участок ↗</a><button class="text-button" data-start-quiz>Помогите выбрать решение</button></div></div>
<div class="hero-bottom"><span></span><a href="#works">Посмотреть работы ↓</a></div></section>
<div class="trust-strip"><a href="#reviews"><strong>{e(r["rating"])} <span>★</span></strong><span>{e(r["source"])} <br>{e(r["count"])}</span></a>{trust}</div>

<section class="solutions" id="solutions"><div class="section-head"><div><p class="eyebrow">РЕШЕНИЯ ДЛЯ ВАШЕГО УЧАСТКА</p><h2>{c["solutions_h2"]}</h2></div>
<p>Выберите нужный объём.<br>Комплектацию уточняет специалист.</p></div>
<div class="system-visual">{picture(img, c["scheme"], "Условный разрез: насос подаёт воду из скважины к оборудованию в доме", "(max-width:760px) 100vw, 60vw")}
<div class="system-caption"><span>КАК ЭТО УСТРОЕНО</span><p>Скважина <b>→</b> Насос <b>→</b> Автоматика <b>→</b> Ваш дом</p><small>Условная схема. Конструкцию и глубину подбирают под участок.</small></div></div>
<div class="solution-grid">{cards}</div></section>

<section class="calculator-section" id="calculator"><div class="section-head"><div><p class="eyebrow">ПРЕДВАРИТЕЛЬНАЯ ОЦЕНКА</p><h2>Сначала — параметры.<br>Потом — решение.</h2></div>
<p>Посмотрите, из чего складывается бюджет.<br>Телефон для расчёта не нужен.</p></div>
<div class="calc-shell"><div class="calc-input"><div class="tabs" role="tablist" aria-label="Способ расчёта">
<button role="tab" id="tab-calc" aria-selected="true" aria-controls="calc-panel">Знаю параметры</button><button role="tab" id="tab-quiz" aria-selected="false" aria-controls="quiz-panel" tabindex="-1">Помогите подобрать</button></div>
<div id="calc-panel" role="tabpanel" aria-labelledby="tab-calc"><div class="field-title"><label for="depth">Предполагаемая глубина</label>
<span class="number"><input id="depth" type="number" min="10" max="{c["calc"]["max_depth"]}" step="1" value="{depth0}" inputmode="numeric" aria-label="Глубина в метрах"> м</span></div>
<input id="depth-range" type="range" min="10" max="{c["calc"]["max_depth"]}" value="{depth0}" aria-label="Предполагаемая глубина скважины">
<div class="range-label"><span>10 м</span><span>{c["calc"]["max_depth"]} м</span></div>
<p class="hint">Это ваше предположение, а не прогноз глубины. Фактическая глубина определяется при бурении.</p>
<label class="field" for="construction">Конструкция скважины<select id="construction">{options}</select></label><p id="depth-warning" class="warning" hidden></p>
<fieldset><legend>Что нужно кроме бурения?</legend><label class="check"><input type="checkbox" id="pump"><span>Насос и автоматика</span></label>
<label class="check"><input type="checkbox" id="house"><span>Подвести воду в дом</span></label></fieldset>
<button class="text-button" data-start-quiz>Не знаете глубину или конструкцию? Пройдите подбор →</button></div>
<div id="quiz-panel" role="tabpanel" aria-labelledby="tab-quiz" hidden><div class="quiz-progress"><span id="quiz-step">Вопрос 1 из 4</span><span>О вашем участке</span></div>
<div class="progress"><span id="progress-fill"></span></div><form id="quiz-form"><div id="quiz-content"></div>
<div class="quiz-nav"><button class="text-button" type="button" id="quiz-back" hidden>← Назад</button><button class="button dark" id="quiz-next" type="submit">Далее →</button></div>
<p class="hint" id="quiz-error" role="alert"></p></form></div></div>
<aside class="calc-result" aria-live="polite"><span class="result-label" id="result-label">БУРЕНИЕ / ПРИМЕР РАСЧЁТА</span><div id="calc-result-content">
<div class="price" id="estimate">{estimate} <span>₽</span></div><p id="formula"></p><hr><ul class="included">{"".join(f"<li>{e(x)}</li>" for x in c["calc"]["included"])}</ul><div id="extras"></div>
<p class="price-note">{e(c["calc"]["note"])}</p></div>
<div id="quiz-result-content" hidden><h3>Подберём решение<br>под ваш участок.</h3><p>Четыре коротких вопроса — и параметры для специалиста готовы.</p><dl id="quiz-summary"></dl></div>
<button class="button primary" id="prepare-lead">Подготовить заявку <span>↗</span></button><p class="hint">Без обязательств. Параметры подставятся в заявку — останется указать телефон.</p></aside></div></section>

<section class="works" id="works"><div class="section-head"><div><p class="eyebrow">НАШИ РАБОТЫ</p><h2>За каждым участком —<br>своя история.</h2></div>
<p>Фотографии с объектов компании.<br>Откройте альбом, чтобы пролистать.</p></div><div class="work-grid">{albums}</div></section>

<section class="process" id="process"><div><p class="eyebrow">КАК ЭТО ПРОИСХОДИТ</p><h2>Понятный следующий<br>шаг на каждом этапе.</h2><a href="#calculator" class="button primary">Начать с расчёта ↗</a></div><ol>{steps}</ol></section>

<section class="reviews" id="reviews"><div class="section-head"><div><p class="eyebrow">ОПЫТ ЗАКАЗЧИКОВ</p><h2>Отзывы, которые<br>можно проверить.</h2></div>
<a class="review-source" href="{e(r["url"])}" target="_blank" rel="noopener"><span class="yandex-mark">{e(r["badge"])}</span><span><b>{e(r["source"])}</b><small>Открыть все отзывы ↗</small></span></a></div>
<div class="review-layout"><aside class="rating-panel"><span>ОЦЕНКА КОМПАНИИ</span><strong>{e(r["rating"])}<small>/ 5</small></strong><p>{e(r["count"])}</p>
<small>Проверено {e(r["checked"])}</small><a href="{e(r["url"])}" target="_blank" rel="noopener">Смотреть в источнике ↗</a></aside><div class="review-cards">{quotes}</div></div>
<p class="hint">Отзывы приведены дословно, орфография авторов сохранена. Общий рейтинг учитывает все оценки.</p></section>

<section class="faq" id="questions"><div><p class="eyebrow">ПЕРЕД НАЧАЛОМ РАБОТ</p><h2>Важные вопросы.<br>Прямые ответы.</h2></div><div>{faq}</div></section>

<section class="lead-section" id="request"><div><p class="eyebrow">ВАШ СЛЕДУЮЩИЙ ШАГ</p><h2>Расскажите<br>о своём участке.</h2>
<p>Соберите параметры в одну заявку.<br>Так специалисту проще подготовить предложение.</p>
<a class="contact-phone" href="tel:{tel(phone)}">{e(phone)} ↗</a><a class="contact-mail" href="mailto:{e(c["email"])}">{e(c["email"])}</a></div>
<form id="lead-form" action="send.php" method="post" novalidate><input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
<label class="field" for="location">Населённый пункт<input id="location" name="Участок" autocomplete="address-level2" placeholder="Например, {e(c["place"])}" maxlength="120" required></label>
<div class="form-row"><label class="field" for="name">Имя <span class="muted">· необязательно</span><input id="name" name="Имя" placeholder="Как к вам обращаться" maxlength="80" autocomplete="given-name"></label>
<label class="field" for="phone">Телефон<input id="phone" name="Телефон" type="tel" inputmode="tel" placeholder="+7 (___) ___-__-__" autocomplete="tel" required></label></div>
<label class="field" for="lead-summary">Параметры заявки<textarea id="lead-summary" name="Параметры" rows="4" maxlength="2000"></textarea></label>
<button class="button dark" type="submit">Отправить заявку <span>↗</span></button><p class="hint">{form_note}</p>
<p class="consent">Нажимая кнопку, вы соглашаетесь с <a href="policy.html" target="_blank" rel="noopener">политикой обработки персональных данных</a>.</p><p id="form-error" role="alert"></p></form></section></main>

<footer><a class="brand" href="#"><b class="mark">{e(c["mark"])}<span>↘</span></b><span>{e(brand.upper())}<small>{e(c["region"])}</small></span></a>{footer_note}</footer>
<div class="mobile-bar"><a data-goal="call" href="tel:{tel(phone)}">Позвонить</a><a href="#request" data-open-contact>Перезвоните</a><a href="#calculator">Рассчитать ↗</a></div>
<button class="chat-toggle" id="contact-toggle" aria-label="Открыть способы связи" aria-expanded="false" aria-controls="contact-panel">Обсудить участок <span>↗</span></button>
<aside id="contact-panel" hidden><button class="close" id="contact-close" aria-label="Закрыть способы связи">×</button><h3>Есть вопрос?</h3><p>Позвоните в компанию или оставьте номер — перезвоним.</p>
<a href="tel:{tel(phone)}">{e(phone)}</a>{chat}<a href="#request" id="contact-request">Подготовить заявку →</a>
<form class="callback" id="callback-form" novalidate><input type="tel" name="Телефон" id="callback-phone" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" aria-label="Ваш телефон" required><button type="submit">Перезвоните мне</button></form>
<p id="callback-status" role="status"></p></aside>
<dialog id="lead-dialog"><button class="close" id="dialog-close" aria-label="Закрыть заявку">×</button><p class="eyebrow" id="lead-state">ЗАЯВКА ОТПРАВЛЕНА</p><h2 id="lead-title">Спасибо!<br>Мы перезвоним.</h2>
<p id="lead-note">Вот что мы получили:</p><pre id="final-summary"></pre><button class="button dark" id="copy-lead">Скопировать текст</button><p id="copy-status" role="status"></p></dialog>
<dialog id="photo-dialog"><button class="close" id="photo-close" aria-label="Закрыть фотографию">×</button><img id="photo-large" alt=""><p id="photo-caption"></p></dialog>
<script>window.SITE={json.dumps(site, ensure_ascii=False)};</script><script src="app.js?v={V}" defer></script></body></html>
'''
    (out / "index.html").write_text(html, encoding="utf-8")
    css = (HERE / "style.css").read_text(encoding="utf-8")
    if c["hero"].get("mobile_position"):
        css += "@media(max-width:760px){.hero-bg{object-position:%s!important}}\n" % c["hero"]["mobile_position"]
    (out / "style.css").write_text(css, encoding="utf-8")
    shutil.copy2(HERE / "app.js", out / "app.js")

    def fill(t, email):
        return (t.replace("__BRAND__", brand).replace("__CITY__", c["city"]).replace("__EMAIL__", email)
                .replace("__DISALLOW__", "Disallow: /" if demo else "Allow: /").replace("__CANONICAL__", c["canonical"]))
    (out / "send.php").write_text(fill((ROOT / "tools/shared/send.php").read_text(encoding="utf-8"), c.get("leads_email", "")), encoding="utf-8")
    (out / "policy.html").write_text(fill((SHARED / "policy.html").read_text(encoding="utf-8"), c["email"]), encoding="utf-8")
    for n in ("robots.txt", ".htaccess"):
        (out / n).write_text(fill((SHARED / n).read_text(encoding="utf-8"), ""), encoding="utf-8")
    size = sum(f.stat().st_size for f in out.iterdir() if f.is_file()) // 1024
    print(f"dist/well-{slug}: {size} КБ, html {len(html) // 1024} КБ, картинок {len(img)}")


if __name__ == "__main__":
    for s in (sys.argv[1:] or [p.stem for p in (HERE / "clients").glob("*.json")]):
        build(s)
