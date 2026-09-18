# -*- coding: utf-8 -*-
"""Сборка одного лендинга из данных площадки. Один файл на выходе:
критический CSS и JS встроены, внешних блокирующих запросов нет."""
import json, html, re
from css import CSS
from js import JS

def esc(s): return html.escape(str(s), quote=True)

ICONS = {
 "check": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M20 6 9 17l-5-5" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
 "phone": '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M6.6 2.8h3l1.5 3.8-2 1.4a12 12 0 0 0 5.9 5.9l1.4-2 3.8 1.5v3a1.8 1.8 0 0 1-2 1.8A16.5 16.5 0 0 1 4.8 4.8a1.8 1.8 0 0 1 1.8-2Z" stroke="currentColor" stroke-width="1.9" stroke-linejoin="round"/></svg>',
 "wa": '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm5.3 14c-.2.6-1.3 1.2-1.8 1.2-.5 0-2.4-.3-4.6-2.3-2.2-2-2.8-3.8-2.8-4.4 0-.5.6-1.6 1.2-1.8.2-.1.5-.1.7 0l.9 1.8c.1.2 0 .4-.1.6l-.5.6c-.1.2-.2.4 0 .6.5.9 1.6 1.9 2.4 2.3.2.1.4 0 .6-.1l.6-.6c.2-.2.4-.2.6-.1l1.8.9c.1.2.1.5 0 .7Z"/></svg>',
 "doc": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M14 3H6a1.8 1.8 0 0 0-1.8 1.8v14.4A1.8 1.8 0 0 0 6 21h12a1.8 1.8 0 0 0 1.8-1.8V9L14 3Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M13.6 3.2V9h5.9" stroke="currentColor" stroke-width="1.8"/></svg>',
 "shield": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 2.6 4.6 5.3v6c0 4.5 3 8.3 7.4 9.9 4.4-1.6 7.4-5.4 7.4-9.9v-6L12 2.6Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="m8.9 12 2.2 2.2 4-4.2" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/></svg>',
 "clock": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.8"/><path d="M12 7.2V12l3.2 2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
 "ruble": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M8.5 20V4h4.2a4.2 4.2 0 0 1 0 8.4H8.5M6.6 15.6h8.1" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/></svg>',
 "pin": '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 21s6.4-5.2 6.4-10.2A6.4 6.4 0 0 0 5.6 10.8C5.6 15.8 12 21 12 21Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><circle cx="12" cy="10.4" r="2.4" stroke="currentColor" stroke-width="1.8"/></svg>',
 "ext": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M14 4h6v6M20 4l-8.4 8.4M17 14.5V19a1.8 1.8 0 0 1-1.8 1.8H5A1.8 1.8 0 0 1 3.2 19V8.8A1.8 1.8 0 0 1 5 7h4.6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}

def ico(name): return ICONS.get(name, ICONS["check"])

# --------------------------------------------------------------- секции

def head(s):
    ld = {
        "@context": "https://schema.org", "@type": "LocalBusiness",
        "name": s["brand"], "description": s["meta_desc"],
        "telephone": s["tel_raw"], "areaServed": s["city"],
        "address": {"@type": "PostalAddress", "addressLocality": s["city"]},
        "priceRange": s["price_range"],
    }
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in s["faq"]]}
    css = CSS
    for k, v in s["theme"].items():
        css = css.replace("__%s__" % k, v)
    robots = ('<meta name="robots" content="noindex,nofollow">\n  '
              '<!-- ЗАПУСК: удалить строку выше и Disallow в robots.txt -->'
              if s["demo"] else '<meta name="robots" content="index,follow">')
    return f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{esc(s['title'])}</title>
  <meta name="description" content="{esc(s['meta_desc'])}">
  {robots}
  <meta name="theme-color" content="{s['theme']['HERO_A']}">
  <link rel="canonical" href="{esc(s['canonical'])}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(s['title'])}">
  <meta property="og:description" content="{esc(s['meta_desc'])}">
  <meta property="og:url" content="{esc(s['canonical'])}">
  <link rel="icon" href="data:image/svg+xml,{esc(s['favicon'])}">
  <link rel="preload" as="image" href="img/hero.jpg" fetchpriority="high">
  <style>{css}</style>
  <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
  <script type="application/ld+json">{json.dumps(faq, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#calc">Перейти к расчёту стоимости</a>
<!-- ДЕМО: строку ниже удалить при передаче клиенту -->
{'<div class="demo"><b>Демонстрационная версия.</b> Тарифы и тексты требуют согласования, заявки уходят в тестовый канал.</div>' if s['demo'] else ''}
<!-- КОНФИГ: {esc(s['cfg_note'])} -->
"""

def header(s):
    nav = "".join(f'<a href="#{i}">{esc(t)}</a>' for i, t in s["nav"])
    return f"""
<header class="hdr">
  <div class="wrap hdr__in">
    <a class="logo" href="#top">{s['logo_svg']}{esc(s['brand'])}</a>
    <nav class="nav" aria-label="Разделы">{nav}</nav>
    <a class="hdr__tel" href="tel:{s['tel_raw']}" data-place="header">
      <b>{esc(s['tel_text'])}</b><span>{esc(s['hours'])}</span>
    </a>
    <a class="btn btn--main" href="#calc">Рассчитать стоимость</a>
  </div>
</header>
"""

def hero(s):
    trust = "".join(f'<li>{ico(i)}<span>{esc(t)}</span></li>' for i, t in s["trust"])
    return f"""
<main id="top">
<section class="hero">
  <div class="wrap hero__grid">
    <div>
      <h1>{esc(s['h1'])}</h1>
      <p class="lead">{esc(s['hero_lead'])}</p>
      <div class="price-anchor">
        <b>{esc(s['price_from'])}</b><span>{esc(s['price_cond'])}</span>
      </div>
      <div class="btn-row">
        <a class="btn btn--main" href="#calc">{esc(s['cta_main'])}</a>
        <a class="btn btn--ghost" href="tel:{s['tel_raw']}" data-place="hero">{ico('phone')}{esc(s['tel_text'])}</a>
      </div>
      <ul class="trust">{trust}</ul>
    </div>
    <div class="hero-media">
      <img src="img/hero.jpg" alt="{esc(s['hero_alt'])}" width="900" height="675"
           fetchpriority="high" decoding="async"
           onerror="this.closest('.hero-media').classList.add('no-img')">
    </div>
  </div>
</section>
"""

def calc(s):
    c = s["calc"]
    def rub(n): return format(int(n), ",d").replace(",", "\u00A0")
    rates = "".join(
        f'<label class="chip"><input type="radio" name="kind" value="{esc(r["label"])}" '
        f'data-rate="{r["rate"]}" data-label="{esc(r["label"])}"{" checked" if i==0 else ""}>'
        f'<span>{esc(r["label"])} · <i class="nw">{rub(r["rate"])} ₽/м</i></span></label>'
        for i, r in enumerate(c["rates"]))
    extras = "".join(
        f'<label class="chip"><input type="checkbox" name="extra" value="{esc(x["label"])}" '
        f'data-label="{esc(x["label"])}" '
        + (f'data-pct="{x["pct"]}"' if "pct" in x else f'data-price="{x["price"]}"')
        + f'><span>{esc(x["label"])} · <i class="nw">{esc(x["hint"])}</i></span></label>'
        for x in c["extras"])
    return f"""
<section class="sec sec--alt" id="calc">
  <div class="wrap">
    <span class="eyebrow">Расчёт без звонка</span>
    <h2>{esc(c['title'])}</h2>
    <p class="lead">{esc(c['sub'])}</p>
    <div class="calc" style="margin-top:26px" id="calc-box">
      <div class="calc__row">
        <div class="calc__lab"><label for="c-depth">{esc(c['depth_label'])}</label>
          <span class="calc__val" id="c-depth-out">{c['depth_default']} м</span></div>
        <input type="range" id="c-depth" min="{c['depth_min']}" max="{c['depth_max']}"
               step="{c['depth_step']}" value="{c['depth_default']}">
      </div>
      <div class="calc__row">
        <div class="calc__lab"><span>{esc(c['kind_label'])}</span></div>
        <div class="chips">{rates}</div>
      </div>
      <div class="calc__row">
        <div class="calc__lab"><span>Добавить к работам</span></div>
        <div class="chips">{extras}</div>
      </div>
      <div class="calc__out">
        <div class="calc__sum" id="c-sum">—</div>
        <ul class="calc__break" id="c-break"></ul>
        <p class="calc__note">{esc(c['note'])}</p>
      </div>
      <form data-lead="calc" style="margin-top:22px">
        <input type="hidden" name="Расчёт" data-calc-carry value="">
        <div class="fld">
          <label for="calc-tel">Телефон для подтверждения сметы</label>
          <input id="calc-tel" type="tel" name="Телефон" inputmode="tel" autocomplete="tel"
                 placeholder="+7 (___) ___-__-__" required>
          <span class="err">Введите номер полностью — 11 цифр</span>
        </div>
        <input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
        <button class="btn btn--main btn--wide" type="submit">Прислать точную смету</button>
        <p class="consent">Нажимая кнопку, вы соглашаетесь на обработку персональных данных.</p>
        <div class="formmsg" role="status" aria-live="polite"></div>
      </form>
    </div>
  </div>
</section>
"""

def services(s):
    cards = "".join(f"""
      <article class="card">
        <div class="card__scheme">{sv['scheme']}</div>
        <h3>{esc(sv['title'])}</h3>
        <p style="color:#42505f;font-size:15.5px">{esc(sv['desc'])}</p>
        <ul>{''.join(f'<li>{esc(x)}</li>' for x in sv['items'])}</ul>
        <div class="card__price">{esc(sv['price'])}</div>
      </article>""" for sv in s["services"])
    return f"""
<section class="sec sec--lazy" id="services">
  <div class="wrap">
    <span class="eyebrow">Услуги</span>
    <h2>{esc(s['services_title'])}</h2>
    <div class="cards cards--3" style="margin-top:26px">{cards}</div>
  </div>
</section>
"""

def steps(s):
    li = "".join(f'<li><b>{esc(t)}</b><span>{esc(d)}</span></li>' for t, d in s["steps"])
    return f"""
<section class="sec sec--alt sec--lazy" id="how">
  <div class="wrap">
    <span class="eyebrow">Как проходит работа</span>
    <h2>{esc(s['steps_title'])}</h2>
    <ol class="steps" style="margin-top:30px">{li}</ol>
  </div>
</section>
"""

def gallery(s):
    figs = "".join(f"""
      <figure><img src="img/{g['file']}" alt="{esc(g['alt'])}" width="800" height="600"
        loading="lazy" decoding="async" onerror="this.style.visibility='hidden'">
        <figcaption>{esc(g['cap'])}</figcaption></figure>""" for g in s["gallery"])
    return f"""
<section class="sec sec--lazy" id="objects">
  <div class="wrap">
    <span class="eyebrow">Объекты</span>
    <h2>{esc(s['gallery_title'])}</h2>
    <div class="gal" style="margin-top:26px">{figs}</div>
  </div>
</section>
"""

def reviews(s):
    rv = "".join(f"""
      <figure class="rev"><blockquote>{esc(r['text'])}</blockquote>
      <figcaption><b>{esc(r['name'])}</b>{esc(r['place'])}</figcaption></figure>""" for r in s["reviews"])
    return f"""
<section class="sec sec--alt sec--lazy" id="reviews">
  <div class="wrap">
    <span class="eyebrow">Отзывы</span>
    <h2>Что пишут заказчики</h2>
    <div class="cards cards--3" style="margin-top:26px">{rv}</div>
    <a class="src" href="{esc(s['reviews_src'])}" target="_blank" rel="noopener nofollow">
      {ico('ext')} Все отзывы — источник</a>
  </div>
</section>
"""

def quiz(s):
    q = s["quiz"]
    out = []
    for n, st in enumerate(q["steps"]):
        opts = "".join(
            f'<label class="chip" style="width:100%"><input type="radio" name="q{n}" '
            f'data-label="{esc(o)}"{" checked" if k==0 else ""}><span>{esc(o)}</span></label>'
            for k, o in enumerate(st["options"]))
        out.append(f"""
      <div class="quiz__step" data-q="{esc(st['q'])}"{' hidden' if n else ''}>
        <h3>{esc(st['q'])}</h3>
        <div class="chips" style="flex-direction:column;align-items:stretch">{opts}</div>
        <div class="quiz__nav">
          <button class="btn btn--main" type="button" data-next>Далее</button>
          {'<button class="quiz__back" type="button">Назад</button>' if n else ''}
        </div>
      </div>""")
    last = len(q["steps"])
    out.append(f"""
      <div class="quiz__step" data-q="finish" hidden>
        <h3>{esc(q['final_title'])}</h3>
        <p style="color:#42505f">{esc(q['final_sub'])}</p>
        <form data-lead="quiz">
          <input type="hidden" name="Ответы квиза" data-quiz-carry value="">
          <div class="fld">
            <label for="q-name">Как к вам обращаться</label>
            <input id="q-name" type="text" name="Имя" autocomplete="name" placeholder="Имя">
          </div>
          <div class="fld">
            <label for="q-tel">Телефон</label>
            <input id="q-tel" type="tel" name="Телефон" inputmode="tel" autocomplete="tel"
                   placeholder="+7 (___) ___-__-__" required>
            <span class="err">Введите номер полностью — 11 цифр</span>
          </div>
          <input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
          <button class="btn btn--main btn--wide" type="submit">{esc(q['final_cta'])}</button>
          <p class="consent">Перезвоним в рабочее время. Без рассылок и передачи номера третьим лицам.</p>
          <div class="formmsg" role="status" aria-live="polite"></div>
        </form>
        <div class="quiz__nav"><button class="quiz__back" type="button">Назад</button></div>
      </div>""")
    return f"""
<section class="sec sec--lazy" id="quiz-sec">
  <div class="wrap">
    <span class="eyebrow">Подбор решения</span>
    <h2>{esc(q['title'])}</h2>
    <p class="lead">{esc(q['sub'])}</p>
    <div class="quiz" id="quiz" style="margin-top:26px">
      <div class="quiz__bar"><i></i></div>
      <div class="quiz__cnt">Шаг 1 из {last+1}</div>
      {''.join(out)}
    </div>
  </div>
</section>
"""

def guarantees(s):
    cards = "".join(f"""
      <article class="card"><div style="color:{s['theme']['ACCENT_DK']};margin-bottom:12px">{ico(g[0])}</div>
      <h3>{esc(g[1])}</h3><p style="color:#42505f;font-size:15.5px;margin:0">{esc(g[2])}</p></article>"""
      for g in s["guarantees"])
    return f"""
<section class="sec sec--alt sec--lazy" id="guarantee">
  <div class="wrap">
    <span class="eyebrow">Документы и гарантии</span>
    <h2>{esc(s['guar_title'])}</h2>
    <div class="cards cards--3" style="margin-top:26px">{cards}</div>
  </div>
</section>
"""

def faq(s):
    d = "".join(f"""
      <details><summary>{esc(q)}</summary><div class="faq__a">{esc(a)}</div></details>"""
      for q, a in s["faq"])
    return f"""
<section class="sec sec--lazy" id="faq">
  <div class="wrap">
    <span class="eyebrow">Вопросы</span>
    <h2>Отвечаем до звонка</h2>
    <div class="faq" style="margin-top:22px">{d}</div>
  </div>
</section>
"""

def contacts(s):
    tels = "".join(f'<div><dt>Телефон</dt><dd><a href="tel:{t[0]}" data-place="contacts">{esc(t[1])}</a></dd></div>'
                   for t in s["tels"])
    return f"""
<section class="sec sec--alt sec--lazy" id="contacts">
  <div class="wrap">
    <span class="eyebrow">Контакты</span>
    <h2>Связаться напрямую</h2>
    <div class="contacts" style="margin-top:26px">
      <dl class="dl">
        {tels}
        <div><dt>Почта</dt><dd><a href="mailto:{esc(s['email'])}">{esc(s['email'])}</a></dd></div>
        <div><dt>Район работ</dt><dd>{esc(s['area'])}</dd></div>
        <div><dt>Часы</dt><dd>{esc(s['hours'])}</dd></div>
        <div><dt>Адрес</dt><dd>{esc(s['address'])}</dd></div>
      </dl>
      <div>
        <div class="btn-row" style="margin-top:0;flex-direction:column">
          <a class="btn btn--main btn--wide" href="tel:{s['tel_raw']}" data-place="contacts">{ico('phone')}Позвонить</a>
          <a class="btn btn--wa btn--wide" href="{esc(s['wa'])}" data-place="contacts"
             target="_blank" rel="noopener">{ico('wa')}Написать в WhatsApp</a>
          <a class="btn btn--ghost btn--wide" href="{esc(s['map'])}" target="_blank" rel="noopener nofollow">
             {ico('pin')}Открыть на карте</a>
        </div>
        <p class="consent" style="margin-top:14px">{esc(s['contacts_note'])}</p>
      </div>
    </div>
  </div>
</section>
</main>
"""

def footer(s):
    return f"""
<footer class="ftr">
  <div class="wrap ftr__in">
    <div>
      <div style="color:#fff;font-weight:800;font-size:17px;margin-bottom:6px">{esc(s['brand'])}</div>
      <div>{esc(s['legal'])}</div>
      <div style="margin-top:10px"><a href="{esc(s['policy'])}">Политика обработки персональных данных</a></div>
    </div>
    <div>
      <div><a href="tel:{s['tel_raw']}">{esc(s['tel_text'])}</a></div>
      <div><a href="mailto:{esc(s['email'])}">{esc(s['email'])}</a></div>
      <div style="margin-top:10px">{esc(s['hours'])}</div>
    </div>
  </div>
</footer>

<div class="dock">
  <a class="btn btn--main" href="tel:{s['tel_raw']}" data-place="dock">{ico('phone')}Позвонить</a>
  <a class="btn btn--wa" href="{esc(s['wa'])}" data-place="dock" target="_blank" rel="noopener">{ico('wa')}WhatsApp</a>
</div>
"""

def build(s):
    cfg = json.dumps({
        "endpoint": s["endpoint"], "ym": s.get("ym") or 0,
        "wa": s["wa"], "telRaw": s["tel_raw"], "telText": s["tel_text"],
        "okText": "Заявка принята. Перезвоним в рабочее время и подтвердим расчёт.",
        "calc": {"baseRate": s["calc"]["rates"][0]["rate"]},
    }, ensure_ascii=False)
    parts = [head(s), header(s), hero(s), calc(s), services(s), steps(s),
             gallery(s), reviews(s), quiz(s), guarantees(s), faq(s),
             contacts(s), footer(s),
             "<script>" + JS.replace("__CFG__", cfg) + "</script>\n</body>\n</html>\n"]
    doc = "".join(parts)
    doc = re.sub(r"\n{3,}", "\n\n", doc)
    return doc
