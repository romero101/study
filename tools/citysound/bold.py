# -*- coding: utf-8 -*-
"""Вариант 2 главной citysound.ru — дерзкий: гигантская типографика, красная лента-тикер, диагонали, портфолио лентой.
Данные и картинки берёт из build.py; собирается командой  python3 tools/citysound/build.py bold  ->  dist/citysound-bold/"""
from html import escape as e


def html_bold(B):
    pic, SRC = B.pic, B.SRC
    ticker = " · ".join(t.upper() for _, t, _ in B.PORTFOLIO)
    svc_big = "".join(f'<a class="bs" href="#request" data-svc="{e(t)}"><span class="bs-n">0{i+1}</span>{pic(k, t, "(max-width:760px) 92vw, 50vw")}<span class="bs-t"><b>{e(t)}</b><i>{e(g)}</i><small>{e(d)}</small></span></a>' for i, (k, t, g, d) in enumerate(B.SERVICES[:4]))
    svc_list = "".join(f'<li><a href="#request" data-svc="{e(t)}"><span>0{i+5}</span><b>{e(t)}</b><small>{e(d)}</small></a></li>' for i, (k, t, g, d) in enumerate(B.SERVICES[4:]))
    pf = "".join(f'<figure class="strip-item"><button type="button" data-full="{SRC[k][-1][0]}" aria-label="Увеличить: {e(t)}">{pic(k, t, "(max-width:760px) 78vw, 30vw")}</button><figcaption><b>{e(t)}</b><small>{e(sub)}</small></figcaption></figure>' for k, t, sub in B.PORTFOLIO)
    revs = "".join(f'<article class="rv"><p>«{e(x)}»</p><footer><div><b>{e(org)}</b><small>{e(who)}{(" · " + e(y)) if y else ""}</small></div><button type="button" class="rev-scan" data-full="{SRC[k][-1][0]}" aria-label="Открыть письмо: {e(org)}">{pic(k, org, "60px")}</button></footer></article>' for k, org, y, x, who in B.REVIEWS)
    methods = "".join(f'<div class="mt"><span>0{i+1}</span><h3>{e(t)}</h3><p>{e(x)}</p></div>' for i, (t, x) in enumerate(B.METHODS))
    logos = "".join(f'<li>{pic("logo_" + n, n, "120px")}</li>' for n in B.CLIENT_LOGOS)
    news = "".join(f'<article class="nw">{pic(k, t, "(max-width:760px) 92vw, 45vw")}<div><small>{e(d)}</small><h3>{e(t)}</h3><p>{e(x)}</p></div></article>' for k, t, d, x in B.NEWS)
    about = "".join(f"<p>{e(x)}</p>" for x in B.ABOUT[:4])
    hero_pic = pic("hero", "Сцена на фестивале — работа СитиСаунд", "100vw", "hero-bg", True)
    founder_pic = pic("founder", "Александр Косарев — фото-пример", "(max-width:760px) 92vw, 40vw")
    head = ("<!doctype html><html lang=\"ru\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>СитиСаунд — звук, свет, сцена. Нижний Новгород, с 1991 года</title>"
            "<meta name=\"description\" content=\"Вариант 2 концепции главной citysound.ru: техническое обеспечение концертов, фестивалей, форумов и городских праздников.\">"
            "<meta name=\"robots\" content=\"noindex,nofollow\"><link rel=\"icon\" href=\"img/" + B.LOGO + "\">"
            "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\"><link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>"
            "<link href=\"https://fonts.googleapis.com/css2?family=Unbounded:wght@700;900&display=swap\" rel=\"stylesheet\">"
            "<link rel=\"stylesheet\" href=\"style.css?v=" + B.STAMP + "\"></head><body>")
    body = f"""
<div class="demo"><span>Концепция новой главной · вариант 2</span><span>Демонстрация · заявки получает студия «Форма сайта»</span></div>
<header class="header"><a class="brand" href="#top"><img src="img/{B.LOGO}" alt="СитиСаунд" height="44"></a>
<nav aria-label="Разделы"><a href="#services">Услуги</a><a href="#portfolio">Работы</a><a href="#quiz">Подбор</a><a href="#reviews">Отзывы</a><a href="#request">Контакты</a></nav>
<a class="hphone" href="tel:{B.TEL}">{B.PHONE}</a><a class="button primary small" href="#request">Заявка</a></header>

<section class="hero" id="top">{hero_pic}
<video class="hero-video" autoplay muted loop playsinline preload="metadata" poster="{SRC['hero'][0][0]}" aria-hidden="true"><source src="img/{B.HERO}" type="video/mp4"></video>
<div class="hero-in"><h1><span>Звук.</span><span>Свет.</span><span>Сцена.</span><span class="acc">Под ключ.</span></h1>
<p class="lead">Техническое обеспечение концертов, фестивалей, форумов и городских праздников. Нижний Новгород и соседние регионы — с 1991 года.</p>
<div class="actions"><a class="button primary" href="#request">Отправить заявку ↗</a><button class="button ghost" type="button" data-start-quiz>Подобрать комплект</button></div>
<div class="msgrs"><a class="msg msg-max" href="{B.MAX}" target="_blank" rel="noopener">{B.ICO_MAX}MAX</a><a class="msg msg-tg" href="{B.TG}" target="_blank" rel="noopener">{B.ICO_TG}Telegram</a></div></div>
<div class="nums"><div><b>1991</b><span>год основания</span></div><div><b>MLA</b><span>Martin Audio — уникален в России</span></div><div><b>80</b><span>Alphastage-80, гидравлическая сцена</span></div><div><b>своя база</b><span>склад, мастерские, транспорт</span></div></div></section>

<div class="ticker" aria-hidden="true"><div class="ticker-in"><span>{e(ticker)} · </span><span>{e(ticker)} · </span></div></div>

<section id="services"><div class="head-b"><p class="eyebrow">01 — ЧТО ДЕЛАЕМ</p><h2>Не аренда колонок.<br>Техобеспечение целиком.</h2></div>
<div class="bs-grid">{svc_big}</div><ol class="svc-list">{svc_list}</ol></section>

<section id="portfolio" class="bleed"><div class="head-b"><p class="eyebrow">02 — РАБОТЫ</p><h2>Сотни мероприятий. Листайте.</h2></div>
<div class="strip">{pf}</div><p class="strip-note">Фото с наших объектов. Больше — в <a href="https://citysound.ru/portfolio/" target="_blank" rel="noopener">портфолио</a> и <a href="{B.TG}" target="_blank" rel="noopener">Telegram</a>.</p></section>

<section id="quiz"><div class="head-b"><p class="eyebrow">03 — ПОДБОР</p><h2>Пять вопросов — и мы поймём, что вам нужно.</h2></div>
<div class="quiz"><form id="quiz-form" novalidate><div class="quiz-top"><span id="quiz-step"></span><span class="quiz-bar"><i id="quiz-fill"></i></span></div><div id="quiz-body"></div><p class="error" id="quiz-error" role="alert"></p><div class="quiz-nav"><button type="button" class="button ghost" id="quiz-back" hidden>← Назад</button><button type="submit" class="button primary" id="quiz-next">Далее →</button></div></form>
<div id="quiz-result" hidden><p class="eyebrow">ВАШ КОМПЛЕКТ</p><h3 id="qr-title"></h3><ul id="qr-list"></ul><p id="qr-note"></p><div class="actions"><a class="button primary" href="#request" id="qr-go">Получить расчёт по этому ТЗ ↗</a><button type="button" class="text-button" id="qr-again">Пройти заново</button></div></div></div></section>

<section id="method" class="red"><div class="head-b"><p class="eyebrow">04 — КАК РАБОТАЕМ</p><h2>Мы избавляем организаторов от головной боли.</h2></div><div class="mts">{methods}</div></section>

<section id="founder"><div class="fnd">{founder_pic}<div><p class="eyebrow">05 — ОСНОВАТЕЛЬ</p><h2>«Мы отвечаем за то, как прозвучит ваше мероприятие».</h2>{about}<p class="who"><b>Александр Косарев</b><small>генеральный директор ООО «Сити-Саунд» · на демо фото-пример, заменим на настоящее</small></p></div></div></section>

<section id="clients" class="bleed"><div class="head-b"><p class="eyebrow">06 — КЛИЕНТЫ</p><h2>Те, у кого нет права на ошибку.</h2></div><ul class="logos">{logos}</ul></section>

<section id="reviews"><div class="head-b"><p class="eyebrow">07 — БЛАГОДАРНОСТИ</p><h2>Что о нас пишут — в письмах.</h2></div><div class="rvs">{revs}</div></section>

<section id="news"><div class="head-b"><p class="eyebrow">08 — 2026</p><h2>Где мы были в этом году.</h2></div><div class="nws">{news}</div></section>

<section id="request" class="lead-b"><div><p class="eyebrow">09 — ЗАЯВКА</p><h2>Расскажите о мероприятии.</h2><p>Перезвоним, уточним детали и составим ТЗ и предложение с понятным каждым этапом.</p>
<a class="bigphone" href="tel:{B.TEL}">{B.PHONE}</a><p class="contacts"><a href="tel:+78312479060">{B.PHONE2}</a> · <a href="mailto:{B.MAIL}">{B.MAIL}</a></p>
<div class="msgrs"><a class="msg msg-max" href="{B.MAX}" target="_blank" rel="noopener">{B.ICO_MAX}MAX</a><a class="msg msg-tg" href="{B.TG}" target="_blank" rel="noopener">{B.ICO_TG}Telegram</a><a class="msg msg-vk" href="{B.VK}" target="_blank" rel="noopener">ВКонтакте</a></div>
<p class="addr">Нижний Новгород, ул. Снежная, 44 · пн–пт 10:00–18:00 · <a href="{B.MAPS}" target="_blank" rel="noopener">на карте</a></p></div>
<form id="lead-form" action="send.php" method="post" novalidate><input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
<label class="field" for="phone">Телефон<input id="phone" name="Телефон" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" required></label>
<label class="field" for="name">Имя<input id="name" name="Имя" maxlength="80" placeholder="Как к вам обращаться"></label>
<label class="field" for="place">Мероприятие и площадка<input id="place" name="Объект" maxlength="160" placeholder="Корпоратив на 300 человек, Пакгаузы, 12 декабря"></label>
<label class="field" for="summary">Техзадание<textarea id="summary" name="Параметры" rows="4" maxlength="2000" placeholder="Подставится из подбора — или напишите своими словами"></textarea></label>
<button class="button primary" type="submit">Отправить заявку ↗</button><p class="error" id="form-error" role="alert"></p>
<p class="consent">Нажимая кнопку, вы соглашаетесь с политикой обработки персональных данных.</p></form></section>

<footer><div><img src="img/{B.LOGO}" alt="" height="40"><p>ООО «Сити-Саунд» · Нижний Новгород, ул. Снежная, 44 · {B.PHONE} · {B.MAIL}</p></div><p class="foot-note">Демонстрация студии «Форма сайта», вариант 2: тексты, фото и логотип — компании СитиСаунд, ролик смонтирован из фотографий её мероприятий, фото основателя — пример. Кнопка MAX ведёт на max.ru. <a href="https://citysound.ru/" target="_blank" rel="noopener">Действующий сайт ↗</a> · <a href="https://formasaita.ru/demo/citysound/">Вариант 1</a></p></footer>
<div class="mobile-bar"><a href="tel:{B.TEL}">Позвонить</a><a class="mb-max" href="{B.MAX}" target="_blank" rel="noopener">{B.ICO_MAX}MAX</a><a class="mb-tg" href="{B.TG}" target="_blank" rel="noopener">{B.ICO_TG}Telegram</a><a href="#request">Заявка</a></div>
<dialog id="photo-dialog"><button type="button" class="close" data-close aria-label="Закрыть">×</button><img id="photo-large" alt=""></dialog>
<dialog id="result-dialog"><button type="button" class="close" data-close aria-label="Закрыть">×</button><div id="result-body"></div></dialog>
<script src="app.js?v={B.STAMP}" defer></script></body></html>"""
    return head + body


CSS_BOLD = r"""
:root{--bg:#050505;--bg2:#0e0e10;--ink:#fff;--muted:#9a9a9a;--acc:#ff1e2d;--acc-d:#d5111f;--line:#222;--r:4px;--disp:"Unbounded",Inter,Arial,sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth;overflow-x:hidden}body{margin:0;overflow-x:hidden;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit}img{max-width:100%}picture{display:contents}svg{max-width:1.5em;max-height:1.5em}h1,h2,h3{margin:0;font-family:var(--disp);letter-spacing:-.02em;line-height:1.02;text-transform:uppercase}h2{font-size:clamp(30px,4.4vw,60px);font-weight:900}h3{font-size:18px;text-transform:none;font-weight:700}
p{margin:0 0 12px}.eyebrow{font-family:var(--disp);font-size:12px;letter-spacing:.2em;color:var(--acc);font-weight:700;margin:0 0 14px}
.button{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:56px;padding:0 28px;border-radius:var(--r);border:2px solid transparent;font-weight:800;text-decoration:none;cursor:pointer;font-size:15px;text-transform:uppercase;letter-spacing:.04em;font-family:var(--disp)}
.button.primary{background:var(--acc);color:#fff}.button.primary:hover{background:var(--acc-d)}.button.ghost{border-color:#fff;background:transparent;color:#fff}.button.small{min-height:42px;padding:0 18px;font-size:12px}
.text-button{background:none;border:0;color:#fff;text-decoration:underline;text-underline-offset:4px;cursor:pointer;font-size:16px;padding:12px 4px}
.demo{display:flex;justify-content:space-between;gap:10px;padding:7px 24px;background:#000;color:#888;font-size:13px}
.header{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:26px;padding:12px 24px;background:rgba(5,5,5,.9);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.header nav{display:flex;gap:22px;margin-left:auto;font-size:14px;text-transform:uppercase;letter-spacing:.08em}.header nav a{text-decoration:none;color:var(--muted)}.header nav a:hover{color:#fff}
.hphone{font-family:var(--disp);font-weight:700;font-size:16px;text-decoration:none}.brand img{display:block;height:44px;width:auto}
section{padding:96px 24px;max-width:1280px;margin:0 auto}section.bleed{max-width:none;padding-left:0;padding-right:0}section.bleed .head-b,section.bleed .strip-note{max-width:1280px;margin-left:auto;margin-right:auto;padding:0 24px}
.head-b{margin-bottom:40px;max-width:900px}
.hero{position:relative;max-width:none;min-height:100vh;display:flex;flex-direction:column;justify-content:flex-end;padding:120px 24px 0;overflow:hidden;isolation:isolate}
.hero-bg,.hero-video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:-2}.hero-video{z-index:-1}
.hero:before{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,5,5,.2) 0%,rgba(5,5,5,.55) 55%,#050505 100%);z-index:0}
.hero-in{position:relative;z-index:1;max-width:1232px;margin:0 auto;width:100%}
.hero h1{font-size:clamp(56px,11.5vw,168px);font-weight:900;line-height:.9;display:flex;flex-direction:column;margin:0 0 26px}.hero h1 .acc{color:var(--acc)}
.hero .lead{max-width:56ch;font-size:clamp(16px,1.3vw,20px);color:#e6e6e6;margin-bottom:26px}.hero .actions{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:16px}
.msgrs{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 40px}.msg{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 16px;border-radius:var(--r);font-weight:700;font-size:15px;text-decoration:none;color:#fff}.msg svg,.msg .ico{width:20px;height:20px;border-radius:4px}
.msg-max{background:linear-gradient(135deg,#2f7bff,#8a3cff)}.msg-tg{background:#27a7e7}.msg-vk{background:#0077ff}
.nums{position:relative;z-index:1;max-width:1232px;margin:0 auto;width:100%;display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid rgba(255,255,255,.25)}
.nums div{padding:22px 18px 30px;border-right:1px solid rgba(255,255,255,.15)}.nums div:last-child{border-right:0}.nums b{display:block;font-family:var(--disp);font-size:clamp(24px,3.2vw,48px);font-weight:900;line-height:1;text-transform:uppercase}.nums span{font-size:13px;color:#cfcfcf}
.ticker{background:var(--acc);color:#fff;overflow:hidden;white-space:nowrap;font-family:var(--disp);font-weight:700;font-size:15px;letter-spacing:.12em;padding:14px 0;transform:rotate(-1.2deg) scale(1.02);margin:6px 0 20px}
.ticker-in{display:inline-block;animation:tick 70s linear infinite}.ticker-in span{padding-right:20px}@keyframes tick{to{transform:translateX(-50%)}}
.bs-grid{display:grid;grid-template-columns:1fr 1fr;gap:2px;margin-bottom:2px}.bs{position:relative;display:block;text-decoration:none;overflow:hidden;background:#000;aspect-ratio:16/10}
.bs img{width:100%;height:100%;object-fit:cover;display:block;opacity:.75;transition:transform .5s,opacity .3s}.bs:hover img{transform:scale(1.05);opacity:.95}
.bs-n{position:absolute;left:22px;top:18px;font-family:var(--disp);font-size:14px;color:var(--acc);font-weight:900}
.bs-t{position:absolute;left:22px;right:22px;bottom:20px;text-shadow:0 2px 12px rgba(0,0,0,.6)}.bs-t b{display:block;font-family:var(--disp);font-size:clamp(22px,2.6vw,36px);text-transform:uppercase;line-height:1}.bs-t i{display:block;font-style:normal;font-size:12px;letter-spacing:.14em;color:var(--acc);margin:6px 0 8px;text-transform:uppercase}.bs-t small{display:block;color:#eee;font-size:14px;max-width:48ch}
.svc-list{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}.svc-list li a{display:grid;grid-template-columns:60px 1fr 1.6fr;gap:20px;align-items:baseline;padding:22px 0;border-bottom:1px solid var(--line);text-decoration:none}
.svc-list span{font-family:var(--disp);color:var(--acc);font-size:14px}.svc-list b{font-family:var(--disp);font-size:clamp(18px,2vw,26px);text-transform:uppercase}.svc-list small{color:var(--muted);font-size:15px}.svc-list li a:hover b{color:var(--acc)}
.strip{display:flex;gap:14px;overflow-x:auto;padding:0 24px 18px;scroll-snap-type:x mandatory;scrollbar-width:none}.strip::-webkit-scrollbar{display:none}
.strip-item{flex:0 0 min(78vw,420px);margin:0;scroll-snap-align:start}.strip-item button{display:block;width:100%;padding:0;border:0;background:#000;cursor:zoom-in;overflow:hidden}.strip-item img{width:100%;aspect-ratio:3/4;object-fit:cover;display:block;transition:transform .4s}.strip-item button:hover img{transform:scale(1.04)}
.strip-item figcaption{padding:12px 2px 0}.strip-item b{display:block;font-family:var(--disp);font-size:14px;text-transform:uppercase}.strip-item small{color:var(--muted);font-size:13px}.strip-note{color:var(--muted);margin-top:8px}
.quiz{background:#000;border:2px solid var(--acc);padding:28px;max-width:860px}.quiz-top{display:flex;justify-content:space-between;align-items:center;gap:16px;color:var(--muted);font-size:13px;margin-bottom:18px;text-transform:uppercase;letter-spacing:.1em}
.quiz-bar{flex:1;height:3px;background:var(--line);overflow:hidden}.quiz-bar i{display:block;height:100%;background:var(--acc);width:0;transition:width .3s}
.quiz h3{font-family:var(--disp);font-size:22px;margin-bottom:16px;text-transform:uppercase}.quiz-options{display:grid;grid-template-columns:1fr 1fr;gap:8px}.quiz-choice{display:flex;gap:12px;align-items:flex-start;padding:14px 16px;border:1px solid var(--line);cursor:pointer}
.quiz-choice:has(input:checked){border-color:var(--acc);background:rgba(255,30,45,.1)}.quiz-choice input{margin-top:4px;accent-color:var(--acc)}.quiz-choice small{display:block;color:var(--muted);font-size:13px}
.quiz-nav{display:flex;justify-content:space-between;gap:12px;margin-top:20px}#quiz-result h3{font-size:24px;margin-bottom:12px}#qr-list{padding-left:20px;color:#ddd}#qr-note{color:var(--muted)}
section.red{max-width:none;background:var(--acc);color:#fff}section.red>*{max-width:1232px;margin-left:auto;margin-right:auto}section.red .eyebrow{color:#fff}
.mts{display:grid;grid-template-columns:repeat(3,1fr);gap:2px;background:rgba(0,0,0,.25)}.mt{background:var(--acc);padding:24px}.mt span{font-family:var(--disp);font-size:13px;opacity:.8}.mt h3{font-family:var(--disp);text-transform:uppercase;font-size:17px;margin:8px 0 10px}.mt p{margin:0;font-size:15px;color:#ffe9ea}
.fnd{display:grid;grid-template-columns:1fr 1.3fr;gap:48px;align-items:center}.fnd img{width:100%;aspect-ratio:4/5;object-fit:cover;object-position:50% 15%;display:block;clip-path:polygon(0 0,100% 0,100% 92%,0 100%);grid-column:1;grid-row:1}.fnd>div{grid-column:2;grid-row:1}
.fnd h2{font-size:clamp(26px,3vw,40px);margin-bottom:18px}.fnd p{color:#d5d5d5}.fnd .who b{display:block;font-family:var(--disp)}.fnd .who small{color:var(--muted)}
.logos{list-style:none;padding:0 24px;display:grid;grid-template-columns:repeat(8,1fr);gap:2px;max-width:1280px;margin:0 auto}.logos li{background:#fff;padding:10px;display:flex;align-items:center;justify-content:center;filter:grayscale(1);transition:filter .3s}.logos li:hover{filter:none}.logos img{width:100%;aspect-ratio:1;object-fit:contain;display:block}
.rvs{display:grid;grid-template-columns:repeat(2,1fr);gap:2px;align-items:start}.rv{background:var(--bg2);padding:26px;border-left:4px solid var(--acc)}.rv p{font-size:17px;color:#ececec;margin:0 0 16px;line-height:1.45}
.rv footer{display:flex;justify-content:space-between;align-items:center;gap:14px}.rv footer b{display:block;font-family:var(--disp);font-size:12px;text-transform:uppercase;color:var(--acc)}.rv footer small{display:block;color:var(--muted);font-size:13px;margin-top:4px}
.rev-scan{flex:0 0 auto;background:none;border:0;padding:0;cursor:zoom-in}.rev-scan img{width:44px;height:58px;object-fit:cover;object-position:top;background:#fff;display:block}
.nws{display:grid;grid-template-columns:1fr 1fr;gap:2px}.nw{background:var(--bg2)}.nw img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block}.nw div{padding:20px}.nw small{color:var(--acc);font-family:var(--disp);font-size:12px;letter-spacing:.1em}.nw h3{font-family:var(--disp);text-transform:uppercase;margin:8px 0 10px;font-size:17px}.nw p{color:var(--muted);margin:0;font-size:15px}
.lead-b{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:start}.bigphone{display:block;font-family:var(--disp);font-weight:900;font-size:clamp(26px,3.4vw,46px);text-decoration:none;margin:10px 0 6px;line-height:1.05}.lead-b .contacts{color:#ddd;font-size:16px}.lead-b .msgrs{margin:16px 0 20px}.addr{color:var(--muted)}
form{display:grid;gap:12px;background:#000;border:1px solid var(--line);padding:24px}.field{display:grid;gap:6px;font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em}
.field input,.field textarea{font:inherit;font-size:16px;text-transform:none;letter-spacing:0;color:#fff;background:#0e0e10;border:1px solid var(--line);padding:14px;width:100%}.field input:focus,.field textarea:focus{outline:0;border-color:var(--acc)}
.hp{position:absolute;left:-9999px}.error:not(:empty){color:#ff8a94;margin:0}.consent{font-size:13px;color:var(--muted);margin:0}
body>footer{padding:40px 24px 110px;max-width:1280px;margin:0 auto;border-top:1px solid var(--line);display:grid;grid-template-columns:1fr 1fr;gap:24px;color:var(--muted);font-size:14px}body>footer img{display:block;margin-bottom:10px}
.mobile-bar{display:none}dialog{border:0;background:transparent;padding:0;max-width:96vw}dialog::backdrop{background:rgba(0,0,0,.9)}dialog img{max-width:96vw;max-height:88vh;display:block}dialog .close{position:fixed;top:14px;right:16px;width:44px;height:44px;border:0;background:#fff;font-size:26px;cursor:pointer;z-index:2}
#result-body{background:var(--bg2);color:#fff;padding:28px;max-width:520px;border-left:4px solid var(--acc)}
@media (max-width:960px){.bs-grid{grid-template-columns:1fr}.mts{grid-template-columns:1fr 1fr}.rvs{grid-template-columns:1fr}.logos{grid-template-columns:repeat(4,1fr)}.fnd{grid-template-columns:1fr}.fnd img{grid-column:1;grid-row:1}.fnd>div{grid-column:1;grid-row:2}.header nav{display:none}.lead-b{grid-template-columns:1fr}.svc-list li a{grid-template-columns:44px 1fr}.svc-list small{grid-column:2}}
@media (max-width:760px){section{padding:60px 16px}.hero{padding:90px 16px 0}.hero h1{font-size:clamp(46px,15vw,72px)}.nums{grid-template-columns:1fr 1fr}.nums div{border-right:0;border-bottom:1px solid rgba(255,255,255,.15)}.mts,.nws{grid-template-columns:1fr}.quiz{padding:18px}.quiz-options{grid-template-columns:1fr}.fnd img{max-width:340px}
.header{padding:10px 16px;gap:12px}.header .button,.header .hphone{display:none}.demo span:last-child{display:none}body>footer{grid-template-columns:1fr;padding-bottom:110px}.ticker{font-size:13px}
.mobile-bar{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;position:fixed;left:0;right:0;bottom:0;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:rgba(5,5,5,.94);backdrop-filter:blur(10px);border-top:1px solid var(--line);z-index:30}
.mobile-bar a{display:flex;align-items:center;justify-content:center;gap:5px;min-height:48px;font-weight:800;font-size:12.5px;text-decoration:none;background:#1a1a1c;padding:0 4px;text-transform:uppercase;letter-spacing:.02em}.mobile-bar a svg,.mobile-bar a .ico{width:18px;height:18px;flex:0 0 auto;border-radius:4px}.mobile-bar .mb-max{background:linear-gradient(135deg,#2f7bff,#8a3cff)}.mobile-bar .mb-tg{background:#27a7e7}.mobile-bar a:last-child{background:var(--acc)}}
"""
