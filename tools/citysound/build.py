#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Демо новой главной для citysound.ru: тексты клиента без изменений, свежие фото с их портфолио и Telegram,
ролик на первом экране (монтаж из их концертных фото), квиз под мероприятие, отзывы, заявка.

    python3 tools/citysound/build.py   ->  dist/citysound/
"""
import json, re, shutil, subprocess
from html import escape as e
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RAW = HERE / "raw/img"
OUT = ROOT / "dist/citysound"
IMG = OUT / "img"

PHONE = "+7 (930) 274-88-88"
PHONE2 = "+7 (831) 247-90-60"
TEL = "+79302748888"
MAIL = "zakaz@citysound.ru"
TG = "https://t.me/citysoundteam"
VK = "https://vk.com/citysound_nn"
MAPS = "https://yandex.ru/maps/org/siti_saund/1786738235/"
MAX = "https://max.ru/"  # у компании нет чата MAX — при запуске подставим их ссылку
ICO_TG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21.9 4.6 18.7 19.3c-.2 1-.9 1.3-1.7.8l-4.8-3.5-2.3 2.2c-.3.3-.5.5-1 .5l.3-4.8 8.8-8c.4-.3-.1-.5-.6-.2L8.5 13.1 3.8 11.7c-1-.3-1-1 .2-1.5l18.3-7c.9-.3 1.6.2 1.6 1.4z"/></svg>'
ICO_MAX = '<img class="ico" src="img/max.png" alt="" width="20" height="20">'

# ---------------------------------------------------------------- картинки
def cand(prefix):
    for f in sorted(RAW.iterdir()):
        if f.name.startswith(prefix):
            return f
    raise FileNotFoundError(prefix)

PHOTOS = {
    "svc_sound": "resources_353_sokwu9whxhm", "svc_light": "resources_349_whatsapp-image-2021-12-08-at-15-55.19", "svc_stage": "resources_353_uf4-31mvxe4",
    "svc_led": "resources_360_whatsapp-image-2022-08-22-at-17-35.30", "svc_complex": "resources_360_whatsapp-image-2022-08-22-at-17-35.31",
    "svc_engineer": "resources_353_m9vqnuikqg0", "svc_lightdesign": "resources_359_рисунок6", "svc_rig": "resources_377_ns3", "svc_system": "resources_360_whatsapp-image-2022-08-24",
    "about": "resources_357_whatsapp-image-2022-05-12-at-13-50.17",
    "pf01": "resources_377_ns4", "pf02": "resources_371_r2raiyue8ze", "pf03": "resources_370_f8fba", "pf04": "resources_349_whatsapp-image-2021-12-08-at-15-55-20-2",
    "pf05": "resources_361_whatsapp-image-2022-11-14-at-18-20.33", "pf06": "resources_362_osvblagovsobordiveevo6", "pf07": "resources_363_zhdlborpav",
    "pf08": "resources_360_whatsapp-image-2022-08-22-at-17-35.29", "pf09": "resources_359_рисунок1", "pf10": "resources_357_whatsapp-image-2022-05-12-at-13-51.51",
    "pf11": "resources_358_img-9701-1", "pf12": "resources_352_whatsapp-image-2021-12-09-at-16-24.52",
    "news1": "resources_377_ns3", "news2": "resources_375_photo-2026-02-19-19-12-16",
    "let1": "resources_47_uprav-delami", "let2": "resources_38_filarmoniya", "let3": "resources_37_eparhiya", "let4": "resources_46_sts-nn",
    "let5": "resources_371_благодарность-театр", "let6": "resources_367_благодарность-чувашия", "let7": "resources_43_shantsev", "let8": "resources_355_благодарность-800",
    "let9": "resources_32_miss-nn-2016", "let10": "resources_34_art-shou", "let11": "resources_41_premio", "let12": "resources_344_сл-3-1", "let13": "resources_368_благодарность-сс", "founder": "FOUNDER",
}
CLIENT_LOGOS = ["government-of-the-nizhny-novgorod-region", "gaz-group", "rosatom", "rzd-russian-railways", "lukoil", "gazprom", "tele2", "toyota", "bmw", "mazda", "peugeot", "liebherr", "world-class", "ctc", "agc-glass-unlimited", "the-centre-of-stas-namin"]


def width(p):
    out = subprocess.run(["sips", "-g", "pixelWidth", str(p)], capture_output=True, text=True).stdout
    return int(re.search(r"pixelWidth: (\d+)", out).group(1))


def webp(src, key, sizes=(640, 1280), q=76):
    w = width(src); items = []
    for label in sizes:
        tw = min(label, w); name = f"{key}-{label}.webp"
        subprocess.run(["cwebp", "-quiet", "-q", str(q), "-resize", str(tw), "0", str(src), "-o", str(IMG / name)], check=True)
        items.append((f"img/{name}", tw))
    return items


def pic(key, alt, sizes="(max-width:760px) 92vw, 33vw", cls="", eager=False):
    v = SRC[key]
    srcset = ", ".join(f"{n} {w}w" for n, w in v)
    attrs = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    c = f' class="{cls}"' if cls else ""
    return f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}"><img{c} src="{v[0][0]}" alt="{e(alt)}" {attrs}></picture>'


# ---------------------------------------------------------------- тексты клиента (как на сайте)
ABOUT = [
    "Компания СИТИСАУНД работает на профессиональном рынке технического обеспечения массовых мероприятий с 1991 г.",
    "Наша современная база (склады, офисы, мастерские, зона погрузки, мойка оборудования, зона отдыха) расположена в г. Нижний Новгород с удобным выездом на основные магистрали.",
    "Кроме работы в своём городе мы легко можем обеспечить нашими услугами соседние регионы, имея собственный транспорт и надёжных партнёров по логистике.",
    "Наш персонал — признанные специалисты своего дела экспертного уровня. В свободное от проектов время сотрудники получают уникальные знания на базе компании — обучение, семинары, тренинг, изучение скрытых возможностей аппаратуры.",
    "Мы постоянно инвестируем в новое оборудование, чтобы обеспечить наших заказчиков самыми современными технологиями. Некоторая часть нашего оборудования уникальна в масштабе России (звуковой мультимодульный массив Martin Audio MLA, мобильная гидравлическая сцена Alphastage-80).",
    "Особое внимание мы уделяем безопасности наших проектов. Все конструкции, подвесы, подиумы, сцены собираются только из сертифицированных компонентов с предварительным расчётом нагрузок. Учитывая наш опыт работы вполне понятно стремление делать всё с запасом прочности, мощности, времени.",
    "Имея в собственности большой склад оборудования в собственном здании, мы успешно радуем наших заказчиков комфортной ценой услуг компании.",
]
TURNKEY = ["монтаж сценических конструкций", "оформление светом", "установка акустических систем", "монтаж светодиодных экранов", "установка силовых барьеров", "размещение декора и баннеров клиента на наших конструкциях", "предоставление необходимых музыкальных инструментов"]
METHODS = [
    ("Мы предусмотрительны", "Тщательно готовимся к вашему мероприятию. Сначала выясняем всё: дату, место, предполагаемое число зрителей и формат события, запрашиваем техническую документацию и выясняем ваши пожелания. Затем заполняем подробное ТЗ и составляем предложение по техобеспечению, из которого вам понятен каждый этап: от времени приезда артистов до скорости демонтажа оборудования."),
    ("Мы заботимся об оборудовании", "Оборудование у нас своё собственное, мы бережно за ним ухаживаем, чистим-моем-сушим после каждого выезда, а перед новым — проверяем, поэтому наша аппаратура не «хрипит» и не выключается в самый неподходящий момент."),
    ("Мы обязательные и пунктуальные", "Приезжаем вовремя, монтируем быстро и качественно, соблюдаем договорённости, правила безопасности и тайминг."),
    ("Мы выгодные", "Мы предлагаем не аренду колонок и световых приборов, а комплексную организацию технического обеспечения мероприятия. Лишнего не навязываем, часто ставим дорогое оборудование по цене дешёвого, потому что дешёвого у нас просто нет."),
    ("Мы надёжные", "К нам всегда можно приехать в гости и своими глазами увидеть то, что вам нужно для мероприятия, познакомиться с нашими сотрудниками, обговорить все тонкости с непосредственными исполнителями, получить визуализацию проекта."),
    ("Мы проверенные", "За более чем 20 лет работы с нами делали мероприятия для клиентов, большинство из которых стали постоянными. К нам обращаются организаторы городских фестивалей и кассовых концертов, корпоративных вечеринок и официальных приёмов. В нашем портфолио — сотни мероприятий."),
    ("Мы понятные", "По каждому пункту вашего ТЗ мы даём аргументированный ответ — почему так и почему столько. Мы отвечаем на все ваши вопросы: как сделать свет, чтобы было светло, но непонятно откуда свет, можно ли подвесить экран без ферм и может ли ваш сотрудник разбирать сцену в костюме."),
]
SERVICES = [
    ("svc_sound", "Звук", "Прокат", "Martin Audio MLA и линейные массивы, цифровые консоли Midas и Yamaha, мониторинг, радиосистемы — от двух микрофонов до стадиона."),
    ("svc_light", "Свет", "Прокат", "Головы, заливка, прожекторы, дым и хейзеры, пульты — художник по свету подберёт приборы под площадку и концепт."),
    ("svc_stage", "Сцены, подиумы", "Прокат", "Мобильная гидравлическая сцена Alphastage-80, фермовые сцены, конструктив Layher Metric, подиумы для улицы и помещений."),
    ("svc_led", "Светодиодные экраны", "Прокат", "Экраны для сцены, конференции и уличной трансляции, подвес без ферм там, где это возможно, видеорежиссура."),
    ("svc_complex", "Комплексные решения", "Обслуживание", "Берём на себя большую часть организации: от помощи в составлении ТЗ до согласования с площадкой тайминга монтажа и нагрузок. Персональный руководитель проекта."),
    ("svc_engineer", "Звукорежиссура", "Обслуживание", "Звукорежиссёры с большим опытом: подбор аппаратуры, анализ площадки, расстановка, мощность и сопровождение в течение всего мероприятия."),
    ("svc_lightdesign", "Установка света", "Обслуживание", "Художник по свету определит приборы, крепление и расположение — чтобы мероприятие было зрелищным, а не просто освещённым."),
    ("svc_rig", "Монтаж конструкций", "Обслуживание", "Сцены, порталы, звуковые башни, объёмные стены под экраны и баннеры — только из сертифицированных компонентов с расчётом нагрузок."),
    ("svc_system", "Системные инженеры", "Обслуживание", "Для больших и гулких площадок: расчёт и настройка систем звукоусиления. Наши инженеры отстроили звуковой комплект стадиона на Стрелке."),
]
PORTFOLIO = [
    ("pf01", "NEW STAR CAMP | Роза Хутор", "фестиваль · 2026"), ("pf02", "Ананда-2023", "фестиваль · 2023"), ("pf03", "«Комедiя-ФЕСТ»", "театральный фестиваль · 2023"),
    ("pf04", "Церемония Паралимпийского комитета «Возвращение в жизнь»", "торжественная церемония"), ("pf05", "День работника сельского хозяйства", "торжественная церемония · 2022"),
    ("pf06", "Первосвятительский визит Патриарха Кирилла", "Нижегородская митрополия"), ("pf07", "Финал «Мисс Нижний Новгород-2022»", "конкурс"),
    ("pf08", "Нижний Новгород 801", "городской праздник · 2022"), ("pf09", "Фестиваль песни России 2022", "фестиваль"),
    ("pf10", "77-летие Дня Победы, Дзержинск", "городской праздник · 2022"), ("pf11", "Лыжня России — 2022", "спортивное событие"), ("pf12", "Новогодние мероприятия, Дзержинск", "главная площадь"),
]
NEWS = [
    ("news1", "NEW STAR CAMP | Роза Хутор", "23–29 марта 2026", "Горы, снег, киловатты звука и тонны оборудования! Мы успешно завершили работу по техническому обеспечению одного из самых масштабных и атмосферных фестивалей — New Star Camp на курорте Роза Хутор. Сложная горная логистика, монтаж в условиях снега и ветра, настройка звука и света — мы приняли этот вызов и обеспечили бесперебойную работу всей нашей техники нон-стоп."),
    ("news2", "Лыжня России 2026", "14 февраля 2026", "Нижний Новгород принял участие в главной лыжной гонке страны. Технический фундамент события обеспечили наши специалисты. Мы развернули сценический комплекс и организовали мощную систему звукоусиления, охватившую весь стартовый городок. Несмотря на погодные условия, техническая часть мероприятия прошла без сбоев."),
]
REVIEWS = [
    ("let1", "Управление делами Правительства Нижегородской области", "2010", "Примите слова искренней благодарности за участие в подготовке и проведении рабочего визита председателя Правительства Российской Федерации В. В. Путина в посёлок Верхняя Верея Выксунского района 1 ноября 2010 года.", "В. М. Потапов, управляющий делами Правительства"),
    ("let7", "Губернатор Нижегородской области", "2010", "Благодарю вас за большой вклад в организацию и проведение мероприятий в рамках визита Святейшего Патриарха Московского и всея Руси Кирилла в Нижегородскую область 31 июля — 2 августа 2010 года.", "В. П. Шанцев, губернатор"),
    ("let8", "Глава города Нижнего Новгорода", "2021", "Коллективу ООО «Ситисаунд-НН» — за помощь в организации торжественных праздничных мероприятий, посвящённых 800-летию со дня основания города Нижнего Новгорода.", "Ю. В. Шалабаев, глава города"),
    ("let6", "Министерство культуры Чувашской Республики", "2022", "Благодарность объявляется Косареву Александру Витальевичу, генеральному директору ООО «Сити-Саунд», за организацию и проведение Всероссийского фестиваля-марафона «Песни России» в Чувашской Республике с 9 по 18 июня 2022 года.", "С. А. Каликова, министр"),
    ("let2", "Нижегородская филармония им. Ростроповича", "2008", "Аппаратура соответствовала изысканным требованиям и позволила исполнить программу в точном соответствии с замыслом. Пожалуйста, передайте также наши слова благодарности вашей опытной высокопрофессиональной команде.", "О. Н. Томина, художественный руководитель и директор — о концерте «Кремерата Балтика» Гидона Кремера"),
    ("let9", "Конкурс «Мисс Нижний Новгород»", "2016", "За качественное акустическое сопровождение конкурса, несмотря на сложное сценическое решение. За возможность без перерывов готовиться к конкурсу — за ваш труд и в будни, и в выходные. Вы настоящие профессионалы своего дела.", "Екатерина Чудакова, директор конкурса; Ирина Чернышова, режиссёр"),
    ("let10", "Агентство «АртШоу»", "", "Приятно, что вам можно доверить мероприятие любого уровня сложности, будь то детский праздник или постановочное шоу. Слаженная команда менеджеров, звукорежиссёров, художников по свету, техников и монтажников контролирует все этапы работы.", "Игорь Кирьян, директор; Ирина Чернышова, режиссёр"),
    ("let11", "PREMIO Centre", "", "За стабильно-профессиональное отношение к поставленным задачам, высокое качество оборудования и безупречную квалификацию своих сотрудников.", "Е. П. Шишканов, директор"),
    ("let12", "Нижегородская ярмарка · выставка Silver Land", "2021", "За безупречную работу по техническому обеспечению специализированной выставки индустрии красоты Silver Land, 1–4 апреля 2021 года.", "М. Ю. Соловьёв, генеральный директор АО «Нижегородская ярмарка»"),
    ("let13", "Invest Dubai Expo · Сочи", "2023", "Лучшему партнёру — прокат оборудования СитиСаунд — за активное участие и продуктивное сотрудничество. С уважением и пожеланиями успешного развития.", "команда организаторов Invest Dubai Expo, Grand Karat Sochi, 15–16 апреля 2023"),
]
LETTERS = [("let1", "Управление делами Правительства"), ("let2", "Нижегородская филармония"), ("let3", "Нижегородская епархия"), ("let4", "СТС Нижний Новгород"), ("let5", "Театр «Комедiя», 2023"), ("let6", "Чувашия, 2022")]
QUIZ = [
    ("type", "Что за мероприятие?", [("Концерт или фестиваль", "сцена, линейный массив, свет, экраны"), ("Корпоратив или частное событие", "звук, свет, ведущий, артист по райдеру"), ("Конференция или форум", "речевой звук, экраны, трансляция"), ("Городской праздник или спорт", "уличная сцена, мощное звукоусиление")]),
    ("place", "Где пройдёт?", [("На улице", "погода, генераторы, сцена с крышей"), ("В зале или на площадке", "акустика зала, подвесы"), ("В шатре или на нестандартной площадке", "смотрим документацию площадки"), ("Пока не выбрали", "подскажем, что учесть")]),
    ("size", "Сколько будет зрителей?", [("До 100", ""), ("100–500", ""), ("500–3 000", ""), ("Больше 3 000", "")]),
    ("need", "Что нужно от нас?", [("Только звук", ""), ("Звук и свет", ""), ("Звук, свет, сцена и экраны — под ключ", ""), ("Согласовать райдер артиста и всё остальное", "")]),
    ("when", "Когда?", [("В ближайшие две недели", ""), ("В течение 1–3 месяцев", ""), ("Позже или пока прикидываем", ""), ("Регулярные мероприятия", "")]),
]

SRC = {}


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    IMG.mkdir(parents=True)
    for key, prefix in PHOTOS.items():
        if prefix == "FOUNDER":
            continue
        SRC[key] = webp(cand(prefix), key)
    for name in CLIENT_LOGOS:
        SRC["logo_" + name] = webp(cand("resources_1_") if False else cand_logo(name), "cl-" + name, sizes=(200,), q=80)
    SRC["hero"] = webp(HERE / "assets/hero_poster.jpg", "hero", sizes=(960, 1600), q=72)
    SRC["founder"] = webp(HERE / "gen/founder.jpg", "founder", sizes=(640, 1024), q=80)
    shutil.copy2(HERE / "assets/hero.mp4", IMG / "hero.mp4")
    shutil.copy2(HERE / "assets/logo.png", IMG / "logo.png")
    shutil.copy2(HERE / "assets/max.png", IMG / "max.png")
    shutil.copy2(ROOT / "dist/vodafon/send.php", OUT / "send.php")
    (OUT / "style.css").write_text(CSS, encoding="utf-8")
    (OUT / "app.js").write_text(JS.replace("__QUIZ__", json.dumps(QUIZ, ensure_ascii=False)), encoding="utf-8")
    (OUT / "index.html").write_text(html(), encoding="utf-8")
    (OUT / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    size = sum(p.stat().st_size for p in OUT.rglob("*") if p.is_file()) // 1024
    print(f"{OUT}: {size} КБ, картинок {len(list(IMG.glob('*.webp')))}")


def cand_logo(name):
    p = HERE / "raw/clients" / f"{name}.jpg"
    if not p.exists():
        raise FileNotFoundError(p)
    return p


def html():
    svc = "".join(f'<article class="svc"><a href="#request" data-svc="{e(t)}">{pic(k, t)}<div><span class="tag">{e(g)}</span><h3>{e(t)}</h3><p>{e(d)}</p></div></a></article>' for k, t, g, d in SERVICES)
    about = "".join(f"<p>{e(x)}</p>" for x in ABOUT)
    turnkey = "".join(f"<li>{e(x)}</li>" for x in TURNKEY)
    methods = "".join(f'<div class="method"><h3>{e(t)}</h3><p>{e(x)}</p></div>' for t, x in METHODS)
    pf = "".join(f'<figure class="pf"><button type="button" data-full="{SRC[k][-1][0]}" aria-label="Увеличить: {e(t)}">{pic(k, t, "(max-width:760px) 46vw, 25vw")}</button><figcaption><b>{e(t)}</b><small>{e(s)}</small></figcaption></figure>' for k, t, s in PORTFOLIO)
    news = "".join(f'<article class="news">{pic(k, t, "(max-width:760px) 92vw, 45vw")}<div><small>{e(d)}</small><h3>{e(t)}</h3><p>{e(x)}</p></div></article>' for k, t, d, x in NEWS)
    reviews = "".join(f'<article class="rev"><div class="rev-top"><b>{e(org)}</b>{f"<span>{e(y)}</span>" if y else ""}</div><p>«{e(x)}»</p><footer><small>{e(who)}</small><button type="button" class="rev-scan" data-full="{SRC[k][-1][0]}" aria-label="Открыть письмо: {e(org)}">{pic(k, org, "80px")}<i>письмо</i></button></footer></article>' for k, org, y, x, who in REVIEWS)
    letters = ""
    logos = "".join(f'<li>{pic("logo_" + n, n, "120px")}</li>' for n in CLIENT_LOGOS)
    return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>СитиСаунд — техническое обеспечение мероприятий в Нижнем Новгороде с 1991 года</title>
<meta name="description" content="Концепция новой главной страницы citysound.ru: прокат звука, света, сцен и светодиодных экранов, звукорежиссура и монтаж конструкций. Свои специалисты, собственная база, Martin Audio MLA и Alphastage-80.">
<meta name="robots" content="noindex,nofollow"><link rel="icon" href="img/logo.png"><link rel="stylesheet" href="style.css"></head>
<body>
<div class="demo"><span>Концепция новой главной</span><span>Демонстрация · заявки получает студия «Форма сайта»</span></div>
<header class="header"><a class="brand" href="#top"><img src="img/logo.png" alt="СитиСаунд" height="44"></a>
<nav aria-label="Разделы"><a href="#services">Услуги</a><a href="#portfolio">Портфолио</a><a href="#about">О компании</a><a href="#reviews">Отзывы</a><a href="#founder">Основатель</a><a href="#contacts">Контакты</a></nav>
<div class="hphone"><a href="tel:{TEL}">{PHONE}</a><small>ежедневно · Нижний Новгород</small></div><a class="button primary small" href="#request">Отправить заявку</a></header>

<section class="hero" id="top">{pic("hero", "Сцена на фестивале — работа СитиСаунд", "100vw", "hero-bg", True)}
<video class="hero-video" autoplay muted loop playsinline preload="metadata" poster="{SRC['hero'][0][0]}" aria-hidden="true"><source src="img/hero.mp4" type="video/mp4"></video>
<div class="hero-in"><p class="eyebrow">НИЖНИЙ НОВГОРОД · ТЕХНИЧЕСКОЕ ОБЕСПЕЧЕНИЕ МЕРОПРИЯТИЙ С 1991 ГОДА</p>
<h1>Звук, свет, сцена и экраны<br>для вашего мероприятия — <em>под ключ.</em></h1>
<p class="lead">Чистый и разборчивый звук на всей площадке, грамотно направленный свет с нужными оттенками в нужное время — основа впечатления гостей. Чёткий регламент и отсутствие вдруг возникающих проблем — сохранённые нервы организаторов.</p>
<div class="actions"><a class="button primary" href="#request">Отправить заявку ↗</a><button class="text-button" type="button" data-start-quiz>Подобрать комплект за 5 вопросов</button></div>
<div class="msgrs"><a class="msg msg-max" href="{MAX}" target="_blank" rel="noopener">{ICO_MAX}Написать в MAX</a><a class="msg msg-tg" href="{TG}" target="_blank" rel="noopener">{ICO_TG}Написать в Telegram</a></div>
<ul class="proofs"><li><b>с 1991</b><span>года на рынке технического обеспечения массовых мероприятий</span></li><li><b>Martin Audio MLA</b><span>мультимодульный массив, уникальный в масштабе России</span></li><li><b>Alphastage-80</b><span>мобильная гидравлическая сцена</span></li><li><b>своя база</b><span>склады, мастерские, мойка оборудования, транспорт</span></li></ul></div></section>

<section id="services"><div class="head"><div><p class="eyebrow">ПРОКАТ И ОБСЛУЖИВАНИЕ</p><h2>Что берём на себя.</h2></div><p>Не аренда колонок, а техническое обеспечение мероприятия целиком: от ТЗ и согласования с площадкой до демонтажа.</p></div><div class="svcs">{svc}</div></section>

<section id="about" class="tint"><div class="about"><div class="about-text"><p class="eyebrow">О КОМПАНИИ</p><h2>СитиСаунд с 1991 года.</h2>{about}
<p>Обратившись к нам при организации концертов, фестивалей, корпоративных вечеринок и других событийных проектов, вы обязательно получите в нашем лице необходимую помощь и поддержку. Наши сотрудники возьмут на себя связь с артистами и согласование технического райдера вашего мероприятия. Также мы выполним под ключ:</p><ul class="turnkey">{turnkey}</ul></div>
<div class="about-photo">{pic("about", "Сцена СитиСаунд на городском празднике", "(max-width:760px) 92vw, 40vw")}<figcaption>Городской праздник, Дзержинск, май 2022</figcaption></div></div>
<div class="head"><div><p class="eyebrow">МЕТОДЫ НАШЕЙ РАБОТЫ</p><h2>Мы избавляем организаторов от головной боли, а зрителям дарим приятные впечатления.</h2></div></div><div class="methods">{methods}</div></section>

<section id="portfolio"><div class="head"><div><p class="eyebrow">ПОРТФОЛИО</p><h2>Сотни мероприятий. Вот недавние.</h2></div><p>Фото с наших объектов. Нажмите, чтобы увеличить. Больше — в <a href="https://citysound.ru/portfolio/" target="_blank" rel="noopener">портфолио</a> и в <a href="{TG}" target="_blank" rel="noopener">Telegram-канале</a>.</p></div><div class="pfs">{pf}</div></section>

<section id="quiz" class="tint"><div class="head"><div><p class="eyebrow">ПОДБОР КОМПЛЕКТА</p><h2>Пять вопросов — и мы поймём, что вам нужно.</h2></div><p>Ответы соберутся в техзадание и подставятся в заявку. Телефон спросим только в конце, если захотите расчёт.</p></div>
<div class="quiz"><form id="quiz-form" novalidate><div class="quiz-top"><span id="quiz-step"></span><span class="quiz-bar"><i id="quiz-fill"></i></span></div><div id="quiz-body"></div><p class="error" id="quiz-error" role="alert"></p><div class="quiz-nav"><button type="button" class="button ghost" id="quiz-back" hidden>← Назад</button><button type="submit" class="button primary" id="quiz-next">Далее →</button></div></form>
<div id="quiz-result" hidden><p class="eyebrow">ВАШ КОМПЛЕКТ</p><h3 id="qr-title"></h3><ul id="qr-list"></ul><p id="qr-note"></p><div class="actions"><a class="button primary" href="#request" id="qr-go">Получить расчёт по этому ТЗ ↗</a><button type="button" class="text-button" id="qr-again">Пройти заново</button></div></div></div></section>

<section id="clients"><div class="head"><div><p class="eyebrow">НАШИ КЛИЕНТЫ</p><h2>Работаем с теми, у кого нет права на ошибку.</h2></div></div><ul class="logos">{logos}</ul></section>

<section id="reviews" class="tint"><div class="head"><div><p class="eyebrow">ОТЗЫВЫ</p><h2>Благодарности от заказчиков.</h2></div><p>Выдержки из благодарственных писем — дословно. Нажмите на письмо, чтобы прочитать целиком.</p></div>
<div class="reviews">{reviews}</div></section>

<section id="founder"><div class="founder">{pic("founder", "Александр Косарев, генеральный директор СитиСаунд — фото-пример", "(max-width:760px) 80vw, 30vw")}<div><p class="eyebrow">ОСНОВАТЕЛЬ</p><h2>«Мы не сдаём колонки в аренду. Мы отвечаем за то, как прозвучит ваше мероприятие».</h2>
<p>Александр Косарев руководит СитиСаунд с 1991 года. За это время компания обеспечила визиты Президента и Патриарха, 800-летие Нижнего Новгорода, «Песни России», сотни фестивалей и концертов — и по-прежнему сама выезжает на объекты.</p>
<ul><li>Собственная база, транспорт и склад оборудования в своём здании</li><li>Martin Audio MLA и Alphastage-80 — уникальны в масштабе России</li><li>К нам можно приехать, увидеть оборудование и получить визуализацию проекта</li></ul>
<p class="who"><b>Александр Косарев</b><small>генеральный директор ООО «Сити-Саунд» · на демо фото-пример, заменим на настоящее</small></p></div></div></section>

<section id="news"><div class="head"><div><p class="eyebrow">НОВОСТИ</p><h2>Где мы были в этом году.</h2></div><p><a href="{TG}" target="_blank" rel="noopener">Все новости — в Telegram-канале</a></p></div><div class="newss">{news}</div></section>

<section id="request" class="lead-sec tint"><div><p class="eyebrow">ЗАЯВКА</p><h2>Расскажите о мероприятии — предложим техобеспечение с понятным каждым этапом.</h2>
<p>Перезвоним, уточним детали, запросим документацию площадки и составим подробное ТЗ и предложение.</p>
<p class="contacts"><a href="tel:{TEL}">{PHONE}</a><a href="tel:+78312479060">{PHONE2}</a><a href="mailto:{MAIL}">{MAIL}</a></p>
<div class="msgrs"><a class="msg msg-max" href="{MAX}" target="_blank" rel="noopener">{ICO_MAX}MAX</a><a class="msg msg-tg" href="{TG}" target="_blank" rel="noopener">{ICO_TG}Telegram</a><a class="msg msg-vk" href="{VK}" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M13.2 18.5c-6.6 0-10.4-4.5-10.5-12h3.3c.1 5.5 2.5 7.8 4.5 8.3V6.5h3.1v4.7c1.9-.2 3.9-2.3 4.6-4.7h3.1c-.5 2.9-2.7 5.1-4.2 6 1.5.7 4 2.6 4.9 6h-3.4c-.7-2.3-2.6-4.1-5-4.3v4.3z"/></svg>ВКонтакте</a></div>
<p class="addr">603135, Нижний Новгород, ул. Снежная, 44 · пн–пт 10:00–18:00 · <a href="{MAPS}" target="_blank" rel="noopener">на карте</a></p></div>
<form id="lead-form" action="send.php" method="post" novalidate><input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
<label class="field" for="phone">Телефон<input id="phone" name="Телефон" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" required></label>
<label class="field" for="name">Имя <i>· необязательно</i><input id="name" name="Имя" maxlength="80" placeholder="Как к вам обращаться"></label>
<label class="field" for="place">Мероприятие и площадка <i>· необязательно</i><input id="place" name="Объект" maxlength="160" placeholder="Например, корпоратив на 300 человек, площадка Пакгаузы, 12 декабря"></label>
<label class="field" for="summary">Техзадание <i>· подставится из подбора</i><textarea id="summary" name="Параметры" rows="5" maxlength="2000"></textarea></label>
<button class="button primary" type="submit">Отправить заявку ↗</button><p class="error" id="form-error" role="alert"></p>
<p class="consent">Нажимая кнопку, вы соглашаетесь с политикой обработки персональных данных.</p></form></section>

<footer><div><img src="img/logo.png" alt="" height="40"><p>ООО «Сити-Саунд» · Нижний Новгород, ул. Снежная, 44 · {PHONE} · {MAIL}</p></div><p class="foot-note">Руководство: Александр Косарев (СЕО), Андрей Бирюков (исполнительный директор). Демонстрация студии «Форма сайта»: тексты, фото и логотип — компании СитиСаунд, ролик смонтирован из фотографий её мероприятий. Кнопка MAX ведёт на max.ru — при запуске подставим чат компании. <a href="https://citysound.ru/" target="_blank" rel="noopener">Действующий сайт ↗</a></p></footer>
<div class="mobile-bar"><a href="tel:{TEL}">Позвонить</a><a class="mb-max" href="{MAX}" target="_blank" rel="noopener">{ICO_MAX}MAX</a><a class="mb-tg" href="{TG}" target="_blank" rel="noopener">{ICO_TG}Telegram</a><a href="#request">Заявка</a></div>
<dialog id="photo-dialog"><button type="button" class="close" data-close aria-label="Закрыть">×</button><img id="photo-large" alt=""></dialog>
<dialog id="result-dialog"><button type="button" class="close" data-close aria-label="Закрыть">×</button><div id="result-body"></div></dialog>
<script src="app.js" defer></script></body></html>'''


CSS = r"""
:root{--bg:#0b0c10;--bg2:#12141a;--ink:#f3f3f1;--muted:#a3a7b1;--acc:#ff2d40;--acc-d:#d81f31;--line:#23262e;--r:14px}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Arial,sans-serif;-webkit-font-smoothing:antialiased}
a{color:inherit}img{max-width:100%}picture{display:contents}h1,h2,h3{margin:0;letter-spacing:-.02em;line-height:1.1}h2{font-size:clamp(28px,3.6vw,44px)}h3{font-size:20px}
p{margin:0 0 12px}.eyebrow{font-size:12px;letter-spacing:.14em;color:var(--acc);font-weight:700;margin:0 0 10px}
.button{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:52px;padding:0 26px;border-radius:99px;border:2px solid transparent;font-weight:700;text-decoration:none;cursor:pointer;font-size:16px}
.button.primary{background:var(--acc);color:#fff}.button.primary:hover{background:var(--acc-d)}.button.ghost{border-color:var(--line);background:transparent;color:var(--ink)}.button.small{min-height:42px;padding:0 18px;font-size:14px}
.text-button{background:none;border:0;color:var(--ink);text-decoration:underline;text-underline-offset:4px;cursor:pointer;font-size:16px;padding:12px 4px}
.msgrs{display:flex;flex-wrap:wrap;gap:10px;margin:-18px 0 34px}.msg{display:inline-flex;align-items:center;gap:8px;min-height:44px;padding:0 16px;border-radius:99px;font-weight:700;font-size:15px;text-decoration:none;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.08);backdrop-filter:blur(6px)}.msg svg,.msg .ico{width:20px;height:20px;border-radius:5px}.msg-max{background:linear-gradient(135deg,#2f7bff,#8a3cff);border-color:transparent;color:#fff}.msg-tg{background:#27a7e7;border-color:#27a7e7;color:#fff}.msg-vk{background:#0077ff;border-color:#0077ff;color:#fff}.lead-sec .msgrs{margin:4px 0 22px}
.demo{display:flex;justify-content:space-between;gap:10px;padding:7px 24px;background:#000;color:#bbb;font-size:13px}
.header{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:26px;padding:12px 24px;background:rgba(11,12,16,.85);backdrop-filter:blur(12px);border-bottom:1px solid var(--line)}
.header nav{display:flex;gap:22px;margin-left:auto;font-size:15px}.header nav a{text-decoration:none;color:var(--muted)}.header nav a:hover{color:#fff}
.hphone{text-align:right;line-height:1.15}.hphone a{font-weight:800;font-size:18px;text-decoration:none}.hphone small{display:block;color:var(--muted);font-size:12.5px}
.brand img{display:block;height:44px;width:auto}
section{padding:80px 24px;max-width:1240px;margin:0 auto}section.tint{max-width:none;background:var(--bg2)}section.tint>*{max-width:1192px;margin-left:auto;margin-right:auto}
.head{display:grid;grid-template-columns:1.2fr 1fr;gap:30px;align-items:end;margin-bottom:34px}.head p{color:var(--muted);margin:0}
/* первый экран */
.hero{position:relative;max-width:none;min-height:92vh;display:flex;align-items:center;padding:110px 24px 60px;overflow:hidden;isolation:isolate}
.hero-bg,.hero-video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;z-index:-2}.hero-video{z-index:-1}
.hero:before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(11,12,16,.92) 0%,rgba(11,12,16,.7) 45%,rgba(11,12,16,.25) 100%);z-index:0}
.hero-in{position:relative;z-index:1;max-width:1192px;margin:0 auto;width:100%}
.hero h1{font-size:clamp(38px,6vw,78px);max-width:14ch;margin:0 0 22px}.hero h1 em{font-style:normal;color:var(--acc)}
.hero .lead{max-width:60ch;font-size:clamp(16px,1.4vw,20px);color:#e9e9e6;margin-bottom:26px}.hero .actions{display:flex;flex-wrap:wrap;gap:8px 22px;align-items:center;margin-bottom:38px}
.proofs{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,1fr);gap:12px;max-width:1000px}.proofs li{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);border-radius:var(--r);padding:14px 16px;backdrop-filter:blur(6px)}
.proofs b{display:block;font-size:20px;color:#fff}.proofs span{font-size:13px;color:#d6d6d2}
/* услуги */
.svcs{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.svc a{display:block;text-decoration:none;background:var(--bg2);border:1px solid var(--line);border-radius:var(--r);overflow:hidden;height:100%;transition:transform .2s}.svc a:hover{transform:translateY(-3px)}
.svc img{width:100%;aspect-ratio:16/10;object-fit:cover;display:block}.svc div{padding:16px 18px 20px}.svc .tag{font-size:12.5px;letter-spacing:.12em;color:var(--acc);font-weight:700}.svc h3{margin:6px 0 8px}.svc p{color:var(--muted);font-size:15px;margin:0}
/* о компании */
.about{display:grid;grid-template-columns:1.25fr 1fr;gap:40px;align-items:start;margin-bottom:60px}.about-text p{color:#d9d9d5;font-size:17px}.about-photo{position:sticky;top:90px}.about-photo img{width:100%;aspect-ratio:4/5;object-fit:cover;border-radius:var(--r);display:block}.about-photo figcaption{color:var(--muted);font-size:13px;margin-top:8px}
.turnkey{columns:2;gap:24px;padding-left:20px;color:#d9d9d5}.turnkey li{margin:4px 0}
.methods{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.method{background:var(--bg);border:1px solid var(--line);border-radius:var(--r);padding:20px}.method h3{color:var(--acc);font-size:18px;margin-bottom:8px}.method p{color:#cfd0cc;font-size:15px;margin:0}
/* портфолио */
.pfs{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.pf{margin:0}.pf button{display:block;width:100%;padding:0;border:0;background:#000;border-radius:var(--r);overflow:hidden;cursor:zoom-in}.pf img{width:100%;aspect-ratio:4/3;object-fit:cover;display:block;transition:transform .3s}.pf button:hover img{transform:scale(1.04)}
.pf figcaption{padding:10px 2px 0;line-height:1.3}.pf b{display:block;font-size:15px}.pf small{color:var(--muted);font-size:13.5px}
/* квиз */
.quiz{background:var(--bg);border:1px solid var(--line);border-radius:18px;padding:26px;max-width:820px}.quiz-top{display:flex;justify-content:space-between;align-items:center;gap:16px;color:var(--muted);font-size:14px;margin-bottom:18px}
.quiz-bar{flex:1;height:4px;background:var(--line);border-radius:99px;overflow:hidden}.quiz-bar i{display:block;height:100%;background:var(--acc);width:0;transition:width .3s}
.quiz h3{font-size:24px;margin-bottom:16px}.quiz-options{display:grid;grid-template-columns:1fr 1fr;gap:10px}.quiz-choice{display:flex;gap:12px;align-items:flex-start;padding:14px 16px;border:2px solid var(--line);border-radius:var(--r);cursor:pointer}
.quiz-choice:has(input:checked){border-color:var(--acc);background:rgba(255,45,64,.08)}.quiz-choice input{margin-top:4px;accent-color:var(--acc)}.quiz-choice small{display:block;color:var(--muted);font-size:13px}
.quiz-nav{display:flex;justify-content:space-between;gap:12px;margin-top:20px}#quiz-result h3{font-size:26px;margin-bottom:12px}#qr-list{padding-left:20px;color:#d9d9d5}#qr-note{color:var(--muted)}
/* клиенты */
.logos{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(8,1fr);gap:12px}.logos li{background:#fff;border-radius:12px;padding:10px;display:flex;align-items:center;justify-content:center}.logos img{width:100%;aspect-ratio:1;object-fit:contain;display:block}
/* отзывы */
.reviews{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;align-items:start}.rev{background:var(--bg);border:1px solid var(--line);border-radius:var(--r);padding:22px 22px 18px;display:flex;flex-direction:column;gap:12px}
.rev-top{display:flex;justify-content:space-between;gap:12px;align-items:baseline}.rev-top b{font-size:15px;color:var(--acc)}.rev-top span{color:var(--muted);font-size:14px;white-space:nowrap}.rev p{margin:0;color:#ecece8;font-size:17px;line-height:1.45}
.rev footer{margin-top:4px;display:flex;justify-content:space-between;align-items:center;gap:14px}.rev footer small{color:var(--muted);font-size:13.5px}.rev-scan{flex:0 0 auto;display:flex;align-items:center;gap:8px;background:none;border:0;padding:0;cursor:zoom-in;color:var(--muted);font-size:12.5px}.rev-scan img{width:44px;height:58px;object-fit:cover;object-position:top;border-radius:4px;background:#fff}
.founder{display:grid;grid-template-columns:1fr 1.6fr;gap:40px;align-items:center}.founder img{grid-column:1;grid-row:1}.founder>div{grid-column:2;grid-row:1}.founder img{width:100%;aspect-ratio:4/5;object-fit:cover;object-position:50% 15%;border-radius:var(--r);display:block}.founder h2{font-size:clamp(24px,2.6vw,34px);margin-bottom:16px}.founder p{color:#d9d9d5}.founder ul{color:#d9d9d5;padding-left:20px;margin:0 0 16px}.founder .who b{display:block}.founder .who small{color:var(--muted)}
.letters{display:grid;grid-template-columns:repeat(6,1fr);gap:12px}.letter{margin:0}.letter button{display:block;width:100%;padding:0;border:0;background:#fff;border-radius:10px;overflow:hidden;cursor:zoom-in}.letter img{width:100%;aspect-ratio:3/4;object-fit:cover;object-position:top;display:block}.letter figcaption{font-size:13px;color:var(--muted);margin-top:6px}
/* новости */
.newss{display:grid;grid-template-columns:1fr 1fr;gap:18px}.news{background:var(--bg2);border:1px solid var(--line);border-radius:var(--r);overflow:hidden}.news img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block}.news div{padding:18px 20px 22px}.news small{color:var(--acc);font-weight:700;letter-spacing:.08em;font-size:12.5px}.news h3{margin:6px 0 10px}.news p{color:var(--muted);margin:0;font-size:15px}
/* заявка */
.lead-sec>div:first-child{max-width:none}.lead-sec{display:grid!important;grid-template-columns:1fr 1fr;gap:40px;max-width:1240px!important}.lead-sec .contacts{display:flex;flex-direction:column;gap:4px;font-size:18px;font-weight:600}.lead-sec .addr{color:var(--muted)}
form{display:grid;gap:12px;background:var(--bg);border:1px solid var(--line);border-radius:18px;padding:22px}.field{display:grid;gap:6px;font-size:14px;color:var(--muted)}.field i{font-style:normal;opacity:.7}
.field input,.field textarea{font:inherit;font-size:16px;color:var(--ink);background:#0f1116;border:2px solid var(--line);border-radius:12px;padding:12px 14px;width:100%}.field input:focus,.field textarea:focus{outline:0;border-color:var(--acc)}
.hp{position:absolute;left:-9999px}.error:not(:empty){color:#ff8a94;margin:0}.consent{font-size:13px;color:var(--muted);margin:0}
body>footer{padding:40px 24px 110px;max-width:1240px;margin:0 auto;border-top:1px solid var(--line);display:grid;grid-template-columns:1fr 1fr;gap:24px;color:var(--muted);font-size:14px}body>footer img{display:block;margin-bottom:10px}
.mobile-bar{display:none}dialog{border:0;background:transparent;padding:0;max-width:96vw}dialog::backdrop{background:rgba(0,0,0,.85)}dialog img{max-width:96vw;max-height:88vh;border-radius:12px;display:block}dialog .close{position:fixed;top:14px;right:16px;width:44px;height:44px;border-radius:50%;border:0;background:#fff;font-size:26px;cursor:pointer;z-index:2}
#result-body{background:var(--bg2);color:var(--ink);padding:28px;border-radius:18px;max-width:520px}
@media (max-width:960px){.svcs,.methods{grid-template-columns:1fr 1fr}.pfs{grid-template-columns:repeat(3,1fr)}.logos{grid-template-columns:repeat(4,1fr)}.letters{grid-template-columns:repeat(3,1fr)}.about{grid-template-columns:1fr}.about-photo{position:static}.header nav{display:none}.lead-sec{grid-template-columns:1fr}}
@media (max-width:760px){section{padding:56px 16px}.head{grid-template-columns:1fr;gap:10px;margin-bottom:22px}.hero{min-height:auto;padding:70px 16px 40px}.hero h1{font-size:clamp(34px,10vw,44px)}.proofs{grid-template-columns:1fr 1fr}.svcs,.methods,.newss{grid-template-columns:1fr}.pfs{grid-template-columns:1fr 1fr}.reviews{grid-template-columns:1fr}.founder{grid-template-columns:1fr}.founder img{max-width:320px;grid-column:1;grid-row:1}.founder>div{grid-column:1;grid-row:2}.quiz{padding:18px}.quiz-options{grid-template-columns:1fr}.turnkey{columns:1}
.header{padding:10px 16px;gap:12px}.hphone small{display:none}.hphone a{font-size:15px}.header .button{display:none}.demo span:last-child{display:none}body>footer{grid-template-columns:1fr;padding-bottom:110px}
.mobile-bar{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:6px;position:fixed;left:0;right:0;bottom:0;padding:10px 12px calc(10px + env(safe-area-inset-bottom));background:rgba(11,12,16,.92);backdrop-filter:blur(10px);border-top:1px solid var(--line);z-index:30}
.mobile-bar a{display:flex;align-items:center;justify-content:center;gap:5px;min-height:48px;border-radius:12px;font-weight:700;font-size:13.5px;text-decoration:none;background:#1c1f27;padding:0 4px}.mobile-bar a svg,.mobile-bar a .ico{width:18px;height:18px;flex:0 0 auto;border-radius:4px}.mobile-bar .mb-max{background:linear-gradient(135deg,#2f7bff,#8a3cff)}.mobile-bar .mb-tg{background:#27a7e7}.mobile-bar a:last-child{background:var(--acc)}}
"""

JS = r"""
'use strict';
const QUIZ = __QUIZ__;
const $ = id => document.getElementById(id), opened = Date.now();
function goal(n) { try { if (window.ym && window.YM_ID) ym(window.YM_ID, 'reachGoal', n); } catch {} }
/* лайтбокс */
document.querySelectorAll('[data-full]').forEach(b => b.addEventListener('click', () => { $('photo-large').src = b.dataset.full; $('photo-large').alt = b.getAttribute('aria-label') || ''; $('photo-dialog').showModal(); }));
document.querySelectorAll('dialog').forEach(d => d.addEventListener('click', e => { if (e.target === d || e.target.closest('[data-close]')) d.close(); }));
/* карточка услуги подставляет тему в заявку */
document.querySelectorAll('[data-svc]').forEach(a => a.addEventListener('click', () => { const s = $('summary'); if (!s.value.trim()) s.value = 'Интересует: ' + a.dataset.svc; }));
/* квиз */
const answers = {}; let step = 0;
function render() {
  const q = QUIZ[step], body = $('quiz-body');
  $('quiz-step').textContent = `Вопрос ${step + 1} из ${QUIZ.length}`; $('quiz-fill').style.width = `${(step + 1) / QUIZ.length * 100}%`;
  $('quiz-back').hidden = step === 0; $('quiz-error').textContent = ''; $('quiz-next').textContent = step === QUIZ.length - 1 ? 'Показать комплект →' : 'Далее →';
  const h = document.createElement('h3'); h.textContent = q[1];
  const box = document.createElement('div'); box.className = 'quiz-options';
  q[2].forEach(o => { const l = document.createElement('label'), i = document.createElement('input'), s = document.createElement('span'); l.className = 'quiz-choice'; i.type = 'radio'; i.name = q[0]; i.value = o[0]; i.checked = answers[q[0]] === o[0]; s.textContent = o[0];
    if (o[1]) { const sm = document.createElement('small'); sm.textContent = o[1]; s.append(sm); } l.append(i, s); box.append(l); });
  body.replaceChildren(h, box);
}
function result() {
  const t = answers.type || '', p = answers.place || '', n = answers.need || '', s = answers.size || '';
  const kit = [];
  if (/Концерт/.test(t)) kit.push('Звук: линейный массив Martin Audio под площадку и число зрителей, мониторинг, цифровая консоль, райдерный бэклайн');
  else if (/Конференц/.test(t)) kit.push('Звук: речевые системы с равномерным покрытием, радиомикрофоны, петлички, конференц-система');
  else if (/Городск/.test(t)) kit.push('Звук: уличная система звукоусиления с покрытием всей площади, дежурный звукорежиссёр');
  else kit.push('Звук: компактный комплект под зал, радиомикрофоны, диджейский набор, звукорежиссёр на площадке');
  if (/свет|под ключ|райдер/i.test(n)) kit.push(/Конференц/.test(t) ? 'Свет: заливка сцены и президиума, акценты на спикеров и логотип' : 'Свет: заливка и динамические приборы по программе художника по свету, дым/хейзер');
  if (/сцена|под ключ|райдер/i.test(n) || /Городск|Концерт/.test(t)) kit.push(/улице|шатре/i.test(p) ? 'Сцена: мобильная Alphastage-80 или фермовая сцена с крышей, силовые барьеры, расчёт нагрузок' : 'Сцена и подиумы под площадку, подвесы из сертифицированных компонентов');
  if (/экран|под ключ|райдер/i.test(n) || /Конференц/.test(t)) kit.push('Экраны: светодиодный экран нужного шага пикселя, видеорежиссёр, трансляция при необходимости');
  if (/райдер/i.test(n)) kit.push('Райдер: свяжемся с артистом и согласуем технический райдер сами');
  if (/Больше 3 000|500–3 000/.test(s)) kit.push('Системный инженер: расчёт и настройка звукоусиления на большой площадке, резерв по мощности');
  if (/улице/i.test(p)) kit.push('Уличный формат: защита оборудования от погоды, электропитание, логистика и тайминг монтажа');
  $('qr-title').textContent = `${t}${s ? ', ' + s.toLowerCase() + ' зрителей' : ''}${p ? ', ' + p.toLowerCase() : ''}.`;
  $('qr-list').replaceChildren(...kit.map(x => { const li = document.createElement('li'); li.textContent = x; return li; }));
  $('qr-note').textContent = 'Это ориентир по составу. Точное предложение с понятным каждым этапом составим после ТЗ и документации площадки — цена зависит от площадки, дат и райдеров.';
  $('quiz-form').hidden = true; $('quiz-result').hidden = false;
  $('summary').value = 'Подбор на сайте:\n' + QUIZ.map(q => `${q[1]} ${answers[q[0]] || '—'}`).join('\n') + '\n\nОриентировочный состав:\n- ' + kit.join('\n- ');
  goal('quiz');
}
$('quiz-form').addEventListener('submit', e => { e.preventDefault(); const q = QUIZ[step], c = document.querySelector(`#quiz-body input[name=${q[0]}]:checked`); if (!c) { $('quiz-error').textContent = 'Выберите вариант — или ближайший к вашему.'; return; } answers[q[0]] = c.value; if (step < QUIZ.length - 1) { step++; render(); } else result(); });
$('quiz-back').addEventListener('click', () => { if (step > 0) { step--; render(); } });
$('qr-again').addEventListener('click', () => { step = 0; for (const k in answers) delete answers[k]; $('quiz-result').hidden = true; $('quiz-form').hidden = false; render(); });
document.querySelectorAll('[data-start-quiz]').forEach(b => b.addEventListener('click', () => { $('quiz').scrollIntoView({ behavior: 'smooth' }); }));
render();
/* заявка */
$('lead-form').addEventListener('submit', async e => {
  e.preventDefault(); const form = e.target, err = $('form-error'), button = form.querySelector('[type=submit]');
  if (!/^7\d{10}$/.test($('phone').value.replace(/\D/g, ''))) { err.textContent = 'Введите номер полностью: +7 и 10 цифр.'; $('phone').focus(); return; }
  err.textContent = ''; if (form._gotcha.value) return;
  const data = new FormData(form); data.append('_Страница', location.href); data.append('_elapsed', String(Math.round((Date.now() - opened) / 1000)));
  button.disabled = true; let sent = true;
  try { const r = await fetch('send.php', { method: 'POST', body: data }), j = await r.json().catch(() => ({})); if (!r.ok || !j.ok) throw new Error(); goal('lead'); } catch { sent = false; }
  button.disabled = false;
  $('result-body').innerHTML = sent ? '<h3>Заявка принята</h3><p>Перезвоним в рабочее время, уточним детали и составим ТЗ.</p>' : `<h3>Не отправилось</h3><p>Позвоните нам: <a href="tel:+79302748888">+7 (930) 274-88-88</a> или напишите в <a href="https://t.me/citysoundteam" target="_blank" rel="noopener">Telegram</a>.</p>`;
  if (sent) form.reset(); $('result-dialog').showModal();
});
"""

if __name__ == "__main__":
    build()
