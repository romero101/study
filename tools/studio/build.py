#!/usr/bin/env python3
"""Страницы услуг сайта студии: tools/studio/pages.py -> dist/formasaita/<slug>/index.html

Стили берём из главной (dist/formasaita/index.html), чтобы не расходились,
дописываем extra.css и кладём одним файлом в assets/ с хешем в имени:
на хостинге css/js кэшируются на 45 дней.
Запуск: python3 tools/studio/build.py
"""
import hashlib, html, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / 'dist' / 'formasaita'
SITE = 'https://formasaita.ru'
sys.path.insert(0, str(HERE))
from pages import PAGES, SERVICES  # noqa: E402

e = html.escape


def asset(name, text):
    (OUT / 'assets').mkdir(exist_ok=True)
    stem, ext = name.rsplit('.', 1)
    for old in (OUT / 'assets').glob(f'{stem}.*.{ext}'):
        old.unlink()
    h = hashlib.md5(text.encode()).hexdigest()[:8]
    (OUT / 'assets' / f'{stem}.{h}.{ext}').write_text(text, encoding='utf-8')
    return f'/assets/{stem}.{h}.{ext}'


def head(tag, h2, lead=''):
    lead = f'<p>{lead}</p>' if lead else ''
    return f'<div class="head"><div><div class="tag">{tag}</div><h2>{h2}</h2></div>{lead}</div>'


def b_cards(b):
    items = ''.join(f'<article class="card"><h3>{h}</h3><p>{p}</p></article>' for h, p in b['items'])
    return head(b['tag'], b['h2'], b.get('lead', '')) + f'<div class="grid">{items}</div>'


def b_steps(b):
    items = ''.join(f'<div><h3>{h}</h3><p>{p}</p></div>' for h, p in b['items'])
    return head(b['tag'], b['h2'], b.get('lead', '')) + f'<div class="steps">{items}</div>'


def b_nums(b):
    rows = ''.join(f'<tr><td>{w}</td><td>{a}</td><td>{z}</td></tr>' for w, a, z in b['rows'])
    c1, c2, c3 = b.get('cols', ('Сайт', 'Было', 'Стало'))
    note = f'<p class="note">{b["note"]}</p>' if b.get('note') else ''
    return (head(b['tag'], b['h2'], b.get('lead', ''))
            + f'<table class="nums"><thead><tr><th>{c1}</th><th>{c2}</th><th>{c3}</th></tr></thead><tbody>{rows}</tbody></table>{note}')


def b_price(b):
    items = ''.join(f'<li><div><b>{n}</b><small>{s}</small></div><div class="pr">{p}</div></li>' for n, s, p in b['items'])
    note = f'<p class="note">{b["note"]} <a href="/#prices">Весь прайс →</a></p>'
    return head(b['tag'], b['h2'], b.get('lead', '')) + f'<ul class="plist plist--box">{items}</ul>{note}'


def b_text(b):
    body = ''.join(f'<p>{p}</p>' for p in b['text'])
    return f'<div class="faq"><div><div class="tag">{b["tag"]}</div><h2>{b["h2"]}</h2></div><div class="prose">{body}</div></div>'


def b_faq(b):
    items = ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in b['items'])
    return f'<div class="faq"><div><div class="tag">Вопросы</div><h2>{b["h2"]}</h2></div><div>{items}</div></div>'


def b_widget(b):
    body = (HERE / 'widgets' / f'{b["widget"]}.html').read_text(encoding='utf-8')
    return head(b['tag'], b['h2'], b.get('lead', '')) + body


BLOCKS = {'cards': b_cards, 'steps': b_steps, 'nums': b_nums, 'price': b_price,
          'text': b_text, 'faq': b_faq, 'widget': b_widget}


def faq_ld(page):
    qa = [x for b in page['blocks'] if b['type'] == 'faq' for x in b['items']]
    if not qa:
        return ''
    strip = lambda s: re.sub(r'<[^>]+>', '', s)
    data = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': strip(q), 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}} for q, a in qa]}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + '</script>'


def render(page, css, js, by_slug):
    url = f'{SITE}/{page["slug"]}/'
    sections = []
    for i, b in enumerate(page['blocks']):
        cls = ' class="alt"' if i % 2 == 0 else ''
        sections.append(f'<section{cls}><div class="wrap">{BLOCKS[b["type"]](b)}</div></section>')
    facts = ''.join(f'<div><b>{x}</b><span>{y}</span></div>' for x, y in page['facts'])
    rel = ''.join(f'<a href="/{s}/"><b>{by_slug[s]["nav"]}</b><span>{by_slug[s]["short"]}</span></a>' for s in page['related'])
    options = ''.join(f'<option{" selected" if s == page["service"] else ""}>{e(s)}</option>' for s in SERVICES)
    foot = ''.join(f'<a href="/{p["slug"]}/">{p["nav"]}</a>' for p in PAGES)
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(page["title"])}</title>
<meta name="description" content="{e(page["desc"])}">
<meta name="theme-color" content="#172333">
<meta property="og:title" content="{e(page["title"])}">
<meta property="og:description" content="{e(page["desc"])}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<link rel="canonical" href="{url}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%23172333'/%3E%3Ccircle cx='32' cy='32' r='12' fill='%234558ed'/%3E%3C/svg%3E">
<link rel="stylesheet" href="{css}">
{faq_ld(page)}
</head>
<body class="sub">
<header><div class="wrap">
  <a class="logo" href="/">форма<span>сайта.</span></a>
  <nav aria-label="Разделы"><a href="/#services">Услуги</a><a href="/#prices">Цены</a><a href="/#process">Как работаем</a><a href="/#faq">Вопросы</a></nav>
  <a class="button button--sm" href="#request">Обсудить сайт</a>
</div></header>

<main id="top">
<section class="hero"><div class="wrap">
  <p class="crumbs"><a href="/">Главная</a> · {page["nav"]}</p>
  <div class="tag">{page["tag"]}</div>
  <h1>{page["h1"]}</h1>
  <p class="intro">{page["intro"]}</p>
  <div class="hero-actions">
    <a class="button" href="#request">{page["cta"]} ↗</a>
    <a class="button button--ghost" href="/#prices">Посмотреть цены</a>
  </div>
  <div class="facts">{facts}</div>
</div></section>

{chr(10).join(sections)}

<section><div class="wrap">
  <div class="head"><div><div class="tag">Рядом по теме</div><h2>Что ещё смотрят.</h2></div></div>
  <div class="rel">{rel}</div>
</div></section>

<div class="wrap"><section class="lead" id="request">
  <div>
    <div class="tag">Заявка</div>
    <h2>{page["form_h2"]}</h2>
    <p>Оставьте телефон и адрес текущего сайта, если он есть.</p>
    <ol>{''.join(f"<li>{x}</li>" for x in page["form_steps"])}</ol>
  </div>
  <form id="lead-form" action="/send.php" method="post" novalidate>
    <input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
    <input type="hidden" name="page" value="/{page["slug"]}/">
    <div class="row">
      <label>Телефон<input name="phone" id="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" required></label>
      <label>Имя <i>· необязательно</i><input name="name" autocomplete="given-name" maxlength="80" placeholder="Как к вам обращаться"></label>
    </div>
    <label>Что нужно<select name="service" id="service">{options}</select></label>
    <label>Текущий сайт или название компании <i>· необязательно</i><input name="site" maxlength="300" placeholder="example.ru" autocapitalize="none"></label>
    <label>Задача <i>· необязательно</i><textarea name="message" id="message" maxlength="2000" placeholder="{e(page["placeholder"])}"></textarea></label>
    <button class="button" type="submit">{page["cta"]} ↗</button>
    <p id="form-status" role="status"></p>
    <p class="consent">Нажимая кнопку, вы соглашаетесь с <a href="/policy.html" target="_blank" rel="noopener">политикой обработки персональных данных</a>.</p>
  </form>
</section></div>
</main>

<footer><div class="wrap">
  <span>© Форма сайта, 2026 · formasaita.ru</span>
  <nav aria-label="Услуги">{foot}</nav>
  <nav aria-label="Служебные ссылки"><a href="/policy.html">Политика обработки данных</a></nav>
</div></footer>
<script src="{js}" defer></script>
</body>
</html>
'''


def main():
    index = (OUT / 'index.html').read_text(encoding='utf-8')
    base = re.search(r'<style>(.*?)</style>', index, re.S).group(1)
    css = asset('site.css', base + (HERE / 'extra.css').read_text(encoding='utf-8'))
    js = asset('site.js', (HERE / 'site.js').read_text(encoding='utf-8'))
    by_slug = {p['slug']: p for p in PAGES}
    for p in PAGES:
        d = OUT / p['slug']
        d.mkdir(parents=True, exist_ok=True)
        (d / 'index.html').write_text(render(p, css, js, by_slug), encoding='utf-8')
        print('ok', p['slug'])
    urls = [f'{SITE}/'] + [f'{SITE}/{p["slug"]}/' for p in PAGES]
    (OUT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'<url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n', encoding='utf-8')
    # ссылки на услуги в подвале главной — между маркерами, чтобы пересборка не плодила дубли
    links = '<!--svc--><nav aria-label="Услуги">' + ''.join(f'<a href="/{p["slug"]}/">{p["nav"]}</a>' for p in PAGES) + '</nav><!--/svc-->'
    if '<!--svc-->' in index:
        index = re.sub(r'<!--svc-->.*?<!--/svc-->', links, index, flags=re.S)
    else:
        index = index.replace('  <nav aria-label="Служебные ссылки">', '  ' + links + '\n  <nav aria-label="Служебные ссылки">', 1)
    (OUT / 'index.html').write_text(index, encoding='utf-8')


if __name__ == '__main__':
    main()
