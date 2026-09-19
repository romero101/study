#!/usr/bin/env python3
"""Страницы услуг и статьи сайта студии.

  tools/studio/pages.py        -> dist/formasaita/<slug>/index.html
  content/stati/<slug>.md      -> dist/formasaita/stati/<slug>/index.html  (+ список /stati/)

Стили берём из главной (dist/formasaita/index.html), чтобы не расходились,
дописываем extra.css и кладём одним файлом в assets/ с хешем в имени:
на хостинге css/js кэшируются на 45 дней.
Запуск: python3 tools/studio/build.py
"""
import hashlib, html, json, re, shutil, sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / 'dist' / 'formasaita'
ARTICLES = ROOT / 'content' / 'stati'
SITE = 'https://formasaita.ru'
sys.path.insert(0, str(HERE))
from pages import PAGES, SERVICES  # noqa: E402
import md  # noqa: E402

e = html.escape
MONTHS = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа',
          'сентября', 'октября', 'ноября', 'декабря']
ICON = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='15' fill='%234558ed'/%3E%3Cpath d='M27 18h-5a14 14 0 0 0 0 28h5z' fill='%23fff'/%3E%3Cpath d='M37 18h5a14 14 0 0 1 0 28h-5z' fill='%23fff' opacity='.55'/%3E%3Crect x='29' y='10' width='6' height='44' rx='3' fill='%23fff'/%3E%3C/svg%3E"
LOGO_MARK = '<svg class="logo-mark" aria-hidden="true" viewBox="0 0 64 64"><rect width="64" height="64" rx="15" fill="#4558ed"/><path d="M27 18h-5a14 14 0 0 0 0 28h5z" fill="#fff"/><path d="M37 18h5a14 14 0 0 1 0 28h-5z" fill="#fff" opacity=".55"/><rect x="29" y="10" width="6" height="44" rx="3" fill="#fff"/></svg>'


def asset(name, text):
    (OUT / 'assets').mkdir(exist_ok=True)
    stem, ext = name.rsplit('.', 1)
    for old in (OUT / 'assets').glob(f'{stem}.*.{ext}'):
        old.unlink()
    h = hashlib.md5(text.encode()).hexdigest()[:8]
    (OUT / 'assets' / f'{stem}.{h}.{ext}').write_text(text, encoding='utf-8')
    return f'/assets/{stem}.{h}.{ext}'


def ru_date(iso):
    d = date.fromisoformat(iso)
    return f'{d.day} {MONTHS[d.month - 1]} {d.year}'


# ---------- общий каркас ----------

def shell(*, title, desc, path, css, js, body, ld='', og='website'):
    url = f'{SITE}{path}'
    foot = ''.join(f'<a href="/{p["slug"]}/">{p["nav"]}</a>' for p in PAGES)
    return f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="theme-color" content="#172333">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="{og}">
<meta property="og:url" content="{url}">
<link rel="canonical" href="{url}">
<link rel="icon" href="{ICON}">
<link rel="apple-touch-icon" href="/img/icon-180.png">
<meta property="og:image" content="https://formasaita.ru/img/og.png">
<link rel="stylesheet" href="{css}">
{ld}
</head>
<body class="sub">
<header><div class="wrap">
  <a class="logo" href="/" aria-label="Форма сайта">{LOGO_MARK}<b>форма<span>сайта</span></b></a>
  <nav aria-label="Разделы"><a href="/#services">Услуги</a><a href="/#prices">Цены</a><a href="/stati/">Статьи</a><a href="/#faq">Вопросы</a></nav>
  <a class="button button--sm" href="#request">Обсудить сайт</a>
  <details class="mnav"><summary aria-label="Меню"></summary><div><a href="/#services">Услуги</a><a href="/#prices">Цены</a><a href="/stati/">Статьи</a><a href="/#faq">Вопросы</a><a href="/">Главная</a></div></details>
</div></header>

<main id="top">
{body}
</main>

<footer><div class="wrap">
  <span>© Форма сайта, 2026 · formasaita.ru</span>
  <nav aria-label="Услуги">{foot}<a href="/stati/">Статьи</a></nav>
  <nav aria-label="Служебные ссылки"><a href="/policy.html">Политика обработки данных</a></nav>
</div></footer>
<script src="{js}" defer></script>
</body>
</html>
'''


def lead_form(*, h2, steps, service, placeholder, cta, page_path):
    options = ''.join(f'<option{" selected" if s == service else ""}>{e(s)}</option>' for s in SERVICES)
    return f'''<div class="wrap"><section class="lead" id="request">
  <div>
    <div class="tag">Заявка</div>
    <h2>{h2}</h2>
    <p>Оставьте телефон и адрес текущего сайта, если он есть.</p>
    <ol>{''.join(f"<li>{x}</li>" for x in steps)}</ol>
  </div>
  <form id="lead-form" action="/send.php" method="post" novalidate>
    <input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
    <input type="hidden" name="page" value="{e(page_path)}">
    <div class="row">
      <label>Телефон<input name="phone" id="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" required></label>
      <label>Имя <i>· необязательно</i><input name="name" autocomplete="given-name" maxlength="80" placeholder="Как к вам обращаться"></label>
    </div>
    <label>Что нужно<select name="service" id="service">{options}</select></label>
    <label>Текущий сайт или название компании <i>· необязательно</i><input name="site" maxlength="300" placeholder="example.ru" autocapitalize="none"></label>
    <label>Задача <i>· необязательно</i><textarea name="message" id="message" maxlength="2000" placeholder="{e(placeholder)}"></textarea></label>
    <button class="button" type="submit">{cta} ↗</button>
    <p id="form-status" role="status"></p>
    <p class="consent">Нажимая кнопку, вы соглашаетесь с <a href="/policy.html" target="_blank" rel="noopener">политикой обработки персональных данных</a>.</p>
  </form>
</section></div>'''


# ---------- блоки страниц услуг ----------

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


def art_cards(arts):
    return '<div class="arts">' + ''.join(
        f'<a href="/stati/{a["slug"]}/"><span class="a-cl">{e(a["cluster"])}</span><b>{e(a["h1"])}</b>'
        f'<span class="a-mt">{a["minutes"]} мин</span></a>' for a in arts) + '</div>'


SHOT_H = {'calc-zabor': 1835, 'calc-septik': 1468, 'calc-skvazhina': 1567, 'calc-krovlya': 1713, 'quiz-zabor-2': 1365,
          'quiz-septik-1': 1315, 'hero-septik': 540, 'hero-krovlya': 566, 'form-zabor': 1219, 'process-zabor': 1085}


def hero_vis(v):
    if not v:
        return ''
    shot = (f'<div class="ph ph--shot"><div class="ph-scr"><img src="/stati/img/{v["shot"]}.webp" alt="{e(v["alt"])}" '
            f'width="390" height="{SHOT_H[v["shot"]]}"></div></div>')
    tip = f'<div class="tip"><b>{v["tip"][0]}</b>{v["tip"][1]}</div>' if v.get('tip') else ''
    if v.get('photo'):
        n = v['photo']
        return (f'<div class="hero-vis"><span class="pic"><img src="/img/{n}-1200.webp" srcset="/img/{n}-640.webp 640w, /img/{n}-1200.webp 1200w" '
                f'sizes="(max-width:980px) 90vw, 480px" alt="{e(v["photo_alt"])}" width="1200" height="800" fetchpriority="high"></span>{shot}{tip}</div>')
    return f'<div class="hero-vis hero-vis--solo">{shot}{tip}</div>'


def render_page(page, css, js, by_slug, arts):
    sections = []
    for i, b in enumerate(page['blocks']):
        cls = ' class="alt"' if i % 2 == 0 else ''
        sections.append(f'<section{cls}><div class="wrap">{BLOCKS[b["type"]](b)}</div></section>')
    about = [a for a in arts if a['leads_to'] == f'/{page["slug"]}/'][:6]
    if about:
        sections.append('<section><div class="wrap">' + head('Статьи', 'Разобрали подробно.') + art_cards(about) + '</div></section>')
    facts = ''.join(f'<div><b>{x}</b><span>{y}</span></div>' for x, y in page['facts'])
    rel = ''.join(f'<a href="/{s}/"><b>{by_slug[s]["nav"]}</b><span>{by_slug[s]["short"]}</span></a>' for s in page['related'])
    body = f'''<section class="hero"><div class="wrap">
  <p class="crumbs"><a href="/">Главная</a> · {page["nav"]}</p>
 <div class="hero-grid"><div>
  <div class="tag">{page["tag"]}</div>
  <h1>{page["h1"]}</h1>
  <p class="intro">{page["intro"]}</p>
  <div class="hero-actions">
    <a class="button" href="#request">{page["cta"]} ↗</a>
    <a class="button button--ghost" href="/#prices">Посмотреть цены</a>
  </div>
 </div>{hero_vis(page.get("vis"))}</div>
  <div class="facts">{facts}</div>
</div></section>

{chr(10).join(sections)}

<section{' class="alt"' if len(sections) % 2 == 0 else ''}><div class="wrap">
  <div class="head"><div><div class="tag">Рядом по теме</div><h2>Что ещё смотрят.</h2></div></div>
  <div class="rel">{rel}</div>
</div></section>

''' + lead_form(h2=page['form_h2'], steps=page['form_steps'], service=page['service'],
                 placeholder=page['placeholder'], cta=page['cta'], page_path=f'/{page["slug"]}/')
    return shell(title=page['title'], desc=page['desc'], path=f'/{page["slug"]}/', css=css, js=js,
                 body=body, ld=faq_ld(page))


# ---------- статьи ----------

SERVICE_OF = {'/' + p['slug'] + '/': p for p in PAGES}
REQUIRED = ('n', 'title', 'h1', 'desc', 'query', 'leads_to', 'cluster', 'date')


FIGS = ARTICLES / 'fig'
FIG_BAD = re.compile(r'<script|<img(?! src="/stati/img/[a-z0-9-]+\.webp")|<iframe|<link|https?://|\son\w+=|style="(?!--[vw]:[\d.]+%;?")', re.I)


def include_factory(fname, problems):
    def include(name, caption):
        if name.startswith('widget:'):
            f = HERE / 'widgets' / (name[7:] + '.html')
            if not f.exists():
                problems.append(f'{fname}: нет виджета {name}'); return ''
            return f.read_text(encoding='utf-8')
        f = FIGS / (name + '.html')
        if not f.exists():
            problems.append(f'{fname}: нет иллюстрации {name}'); return ''
        body = f.read_text(encoding='utf-8').strip()
        m = FIG_BAD.search(body)
        if m:
            problems.append(f'{fname}: в иллюстрации {name} запрещённое: {m.group(0)[:30]}')
        cap = f'<figcaption>{caption}</figcaption>' if caption else ''
        return f'<figure class="fig"><div class="fig-body">{body}</div>{cap}</figure>'
    return include


def load_articles():
    arts, problems = [], []
    for f in sorted(ARTICLES.glob('*.md')):
        if f.name.startswith('_'):
            continue
        meta, body = md.meta_and_body(f.read_text(encoding='utf-8'))
        miss = [k for k in REQUIRED if not meta.get(k)]
        if miss:
            problems.append(f'{f.name}: нет {", ".join(miss)}')
            continue
        htm, toc, chars = md.render(body, include_factory(f.name, problems))
        for href in re.findall(r'href="(/[^"#]*)', htm):
            if not (href == '/' or href.startswith('/stati/') or href in SERVICE_OF or href == '/policy.html'):
                problems.append(f'{f.name}: ссылка на несуществующую страницу {href}')
        arts.append(dict(meta, slug=f.stem, html=htm, toc=toc, chars=chars, n=int(meta['n']),
                         minutes=max(2, round(chars / 1300))))
    slugs = {a['slug'] for a in arts}
    for a in arts:
        for s in re.findall(r'href="/stati/([^/"]+)/', a['html']):
            if s not in slugs:
                problems.append(f'{a["slug"]}: ссылка на статью, которой нет: {s}')
    arts.sort(key=lambda a: a['n'])
    return arts, problems


def render_article(a, arts, css, js):
    svc = SERVICE_OF.get(a['leads_to'])
    near = [x for x in arts if x['cluster'] == a['cluster'] and x['slug'] != a['slug']]
    near += [x for x in arts if x['leads_to'] == a['leads_to'] and x not in near and x['slug'] != a['slug']]
    near = near[:3]
    toc = ''
    if len(a['toc']) >= 3:
        toc = '<nav class="toc" aria-label="Содержание"><b>Содержание</b><ol>' + ''.join(
            f'<li><a href="#{i}">{e(t)}</a></li>' for i, t in a['toc']) + '</ol></nav>'
    if svc:
        cta = (f'<aside class="a-cta"><div><span class="tag">Услуга студии</span><b>{e(svc["nav"])}</b>'
               f'<p>{e(svc["short"])}.</p></div><a class="button" href="{a["leads_to"]}">Подробнее и цены →</a></aside>')
        service, form_cta = svc['service'], svc['cta']
    else:
        cta = ('<aside class="a-cta"><div><span class="tag">Форма сайта</span><b>Сначала показываем готовый сайт</b>'
               '<p>Соберём демо вашего сайта на ваших фото и ценах — бесплатно, до договора.</p></div>'
               '<a class="button" href="/#prices">Цены и пакеты →</a></aside>')
        service, form_cta = 'Пока не знаю, нужен совет', 'Получить демо своего сайта'
    more = ('<section class="alt"><div class="wrap">' + head('Читайте также', 'По этой теме.') + art_cards(near)
            + '</div></section>') if near else ''
    ld = {'@context': 'https://schema.org', '@type': 'Article', 'headline': a['h1'], 'description': a['desc'],
          'datePublished': a['date'], 'dateModified': a.get('updated', a['date']), 'inLanguage': 'ru',
          'mainEntityOfPage': f'{SITE}/stati/{a["slug"]}/',
          'author': {'@type': 'Organization', 'name': 'Форма сайта', 'url': SITE + '/'},
          'publisher': {'@type': 'Organization', 'name': 'Форма сайта', 'url': SITE + '/'}}
    crumbs = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Главная', 'item': SITE + '/'},
        {'@type': 'ListItem', 'position': 2, 'name': 'Статьи', 'item': SITE + '/stati/'},
        {'@type': 'ListItem', 'position': 3, 'name': a['h1']}]}
    ld_html = ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False) + '</script>' for x in (ld, crumbs))
    body = f'''<article class="post"><div class="wrap">
  <p class="crumbs"><a href="/">Главная</a> · <a href="/stati/">Статьи</a> · {e(a["cluster"])}</p>
  <h1>{e(a["h1"])}</h1>
  <p class="a-meta"><time datetime="{a["date"]}">{ru_date(a["date"])}</time> · {a["minutes"]} мин чтения</p>
  {toc}
  <div class="md">{a["html"]}</div>
  {cta}
</div></article>
{more}
''' + lead_form(h2='Покажем, каким может быть ваш сайт.', steps=[
        'Перезвоним в рабочий день, зададим 3–4 вопроса.', 'Соберём демо на ваших материалах.',
        'Пришлём ссылку — посмотрите на телефоне.'], service=service,
        placeholder='Например: бурим скважины в Самаре, сайт старый, заявок с него нет',
        cta=form_cta, page_path=f'/stati/{a["slug"]}/')
    return shell(title=a['title'] + (' | Форма сайта' if len(a['title']) <= 58 else ''), desc=a['desc'], path=f'/stati/{a["slug"]}/',
                 css=css, js=js, body=body, ld=ld_html, og='article')


def render_index(arts, css, js):
    clusters = []
    for a in arts:
        if a['cluster'] not in clusters:
            clusters.append(a['cluster'])
    chips = '<button type="button" class="on" data-c="">Все · ' + str(len(arts)) + '</button>' + ''.join(
        f'<button type="button" data-c="{e(c)}">{e(c)} · {sum(1 for a in arts if a["cluster"] == c)}</button>' for c in clusters)
    items = ''.join(
        f'<a href="/stati/{a["slug"]}/" data-c="{e(a["cluster"])}"><span class="a-cl">{e(a["cluster"])}</span>'
        f'<b>{e(a["h1"])}</b><span class="a-ds">{e(a["desc"])}</span><span class="a-mt">{a["minutes"]} мин</span></a>' for a in arts)
    body = f'''<section class="hero"><div class="wrap">
  <p class="crumbs"><a href="/">Главная</a> · Статьи</p>
  <div class="tag">Статьи</div>
  <h1>Как подрядчику получать заявки <span>с сайта и рекламы.</span></h1>
  <p class="intro">Разборы для владельцев строительных и монтажных компаний: Директ, сайт, цена заявки, скорость. С цифрами из наших замеров и ссылками на источники.</p>
  <div class="chips" id="chips">{chips}</div>
  <div class="arts arts--all" id="arts">{items}</div>
</div></section>
''' + lead_form(h2='Покажем, каким может быть ваш сайт.', steps=[
        'Перезвоним в рабочий день, зададим 3–4 вопроса.', 'Соберём демо на ваших материалах.',
        'Пришлём ссылку — посмотрите на телефоне.'], service='Пока не знаю, нужен совет',
        placeholder='Например: бурим скважины в Самаре, сайт старый, заявок с него нет',
        cta='Получить демо своего сайта', page_path='/stati/')
    return shell(title='Статьи для подрядчиков: сайт, Яндекс Директ, заявки | Форма сайта',
                 desc='Разборы для подрядчиков: почему с сайта нет заявок, сколько стоит заявка в Директе, как ускорить сайт и сколько стоит лендинг. С цифрами и источниками.',
                 path='/stati/', css=css, js=js, body=body)


# ---------- сборка ----------

def main():
    index = (OUT / 'index.html').read_text(encoding='utf-8')
    base = re.search(r'<style>(.*?)</style>', index, re.S).group(1)
    css = asset('site.css', base + (HERE / 'extra.css').read_text(encoding='utf-8')
                + (HERE / 'figures.css').read_text(encoding='utf-8'))
    js = asset('site.js', (HERE / 'site.js').read_text(encoding='utf-8'))
    arts, problems = load_articles()
    for p in problems:
        print('!!', p)
    by_slug = {p['slug']: p for p in PAGES}
    for p in PAGES:
        d = OUT / p['slug']
        d.mkdir(parents=True, exist_ok=True)
        (d / 'index.html').write_text(render_page(p, css, js, by_slug, arts), encoding='utf-8')
    print('услуг:', len(PAGES))

    if (ROOT / 'content' / 'site-img').exists():
        shutil.copytree(ROOT / 'content' / 'site-img', OUT / 'img', dirs_exist_ok=True)

    sdir = OUT / 'stati'
    if sdir.exists():
        shutil.rmtree(sdir)
    sdir.mkdir()
    if (ARTICLES / 'img').exists():
        shutil.copytree(ARTICLES / 'img', sdir / 'img')
    (sdir / 'index.html').write_text(render_index(arts, css, js), encoding='utf-8')
    for a in arts:
        (sdir / a['slug']).mkdir()
        (sdir / a['slug'] / 'index.html').write_text(render_article(a, arts, css, js), encoding='utf-8')
    print('статей:', len(arts), '· знаков всего:', sum(a['chars'] for a in arts))

    urls = [f'{SITE}/'] + [f'{SITE}/{p["slug"]}/' for p in PAGES] + [f'{SITE}/stati/'] + \
           [f'{SITE}/stati/{a["slug"]}/' for a in arts]
    (OUT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'<url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n', encoding='utf-8')

    # главная: ссылки на услуги в подвале и «Статьи» в шапке — между маркерами, пересборка не плодит дубли
    links = ('<!--svc--><nav aria-label="Услуги">' + ''.join(f'<a href="/{p["slug"]}/">{p["nav"]}</a>' for p in PAGES)
             + '<a href="/stati/">Статьи</a></nav><!--/svc-->')
    index = re.sub(r'<!--svc-->.*?<!--/svc-->', links, index, flags=re.S) if '<!--svc-->' in index else \
        index.replace('  <nav aria-label="Служебные ссылки">', '  ' + links + '\n  <nav aria-label="Служебные ссылки">', 1)
    if '/stati/' not in index.split('</header>')[0]:
        index = index.replace('<a href="#process">Как работаем</a>', '<a href="#process">Как работаем</a><a href="/stati/">Статьи</a>', 1)
    (OUT / 'index.html').write_text(index, encoding='utf-8')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
