#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает dist/zaborpro/index.html (Заборы, Новосибирск) из шаблона dist/strana-zaborov/index.html.
Общие части — шапка <head>, калькулятор, диалоги — берутся из шаблона; контент клиента — отсюда.
Тексты, цены, отзывы и фото — с zaborpronsk.ru (снимок в dist/zaborpro-source). Запуск: python3 tools/fence/build_zaborpro.py"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "dist/zaborpro"
h = (ROOT / "dist/strana-zaborov/index.html").read_text(encoding="utf-8")


def pic(name, alt, w, hh, sizes, cls=""):
    c = f' class="{cls}"' if cls else ""
    return (f'<picture><source type="image/webp" srcset="img/{name}-640.webp 640w, img/{name}-1280.webp 1280w" sizes="{sizes}">'
            f'<img{c} src="img/{name}-640.webp" alt="{alt}" loading="lazy" decoding="async" width="{w}" height="{hh}"></picture>')


def card(img, alt, title, price, items, key, render=False):
    lis = "".join(f"<li>{i}</li>" for i in items)
    return (f'<article class="type">{pic(img, alt, 640, 480, "(max-width:760px) 84vw, 33vw", "render" if render else "")}'
            f'<div><h3>{title}</h3><p class="price">от {price} ₽<small>/ п.м.</small></p><ul>{lis}</ul>'
            f'<button class="button ghost" type="button" data-pick="{key}">Рассчитать ↗</button></div></article>')


def quote(text, name, date, what):
    return (f'<blockquote><p>{text}</p><footer><span class="ava">{name[0].upper()}</span>'
            f'<span>{name}<small>{date} · {what} · Авито</small></span></footer></blockquote>')


types = "".join([
    card("g1-03", "Тёмный забор из профлиста у частного дома", "Профлист", "2 600",
         ["Глухой: с улицы участок не видно", "Самый быстрый монтаж", "Любой цвет по каталогу RAL"], "prof"),
    card("g2-05", "Забор из коричневого евроштакетника на ленточном основании", "Евроштакетник", "3 200",
         ["Выглядит как дерево, не гниёт", "Продувается — не парусит", "Штакетник продаём и отдельно"], "evro"),
    card("type-02", "Забор из 3D-сетки", "3D-сетка", "3 200",
         ["Сварные панели с рёбрами жёсткости", "Участок просматривается", "Для дома, парковки, территории"], "d3", True),
    card("type-04", "Деревянный забор", "Дерево", "3 400",
         ["Натуральный материал", "Под стиль дома и бани", "Обработка от влаги"], "wood", True),
    card("type-05", "Сварной кованый забор", "Сварной / кованый", "3 200",
         ["Металл, сварка, ковка", "Индивидуальный рисунок", "Ворота в том же стиле"], "weld", True),
    card("g1-08", "Забор из профлиста на кирпичном основании", "С кирпичными столбами", "3 400",
         ["Столбы и цоколь из кирпича", "Заполнение — профлист или штакетник", "Фундамент делаем сами"], "brick"),
])

# Отзывы — дословно со скриншотов Авито на сайте компании, орфография авторов сохранена.
reviews = "".join([
    quote("Отличные ребята! Вежливые, аккуратные. Все нюансы обговорили за 10 минут по телефону, тут же сделали заказ. "
          "Работа выполнена максимально качественно и быстро. 43 метра каркаса за 6 часов, весь материал + работа. "
          "Цена значительно ниже рыночной. P. S контакт записан, однозначно буду вас рекомендовать.",
          "Ирина", "5 октября 2024", "Каркас забора"),
    quote("Делали монтаж забора 82 метра.Что мне понравилось в первую очередь, пунктуальность!) Первая встреча прошла ровно "
          "во столько, во сколько договорились..) Быстренько сделали замеры, на следующий день до обеда завезли материалы, "
          "И тут же приступили к работе.. Ребята очень коммуникабельные, вежливые, отзывчивые!!! Спилили лишние ветки клена, "
          "что мешали работе, быстро, качественно выполнили работу за два дня!!!) Рекомендую..))) Цена тоже устроила меня) "
          "Очень приятно было с ними сотрудничать, мастер Андрей отлично всё организовал!)",
          "ольга", "26 мая 2024", "Забор из профлиста под ключ"),
    quote("Договорился с Андреем,приехал на замер,на следующей день приступил к работе,за два дня 60 метров под ключ "
          "сделал работу ,просто на ура, всем советую люди работают просто на совесть и на качество \U0001F44D",
          "Влад Шекуто", "7 июня 2024", "Забор из профлиста под ключ"),
    quote("Спасибо мастеру Андрею за прекрасный забор !!! Заказала забор 30 метров с воротами !Сделали за два дня !"
          "Мастера своего дела !Цена очень порадовала !!Рекомендую !!!",
          "Анна Невзорова", "26 мая 2024", "Забор из профлиста под ключ"),
    quote("Андрей спасибо за отличную работу, быстро качественно 80 метров за один день!!!будем обращаться обязательно",
          "евгений", "13 августа 2024", "Каркас забора"),
])

head = h[:h.index("<body>")]
head = head.replace("Страна Заборов — заборы под ключ в Дзержинске и Нижнем Новгороде", "Заборы под ключ в Новосибирске — расчёт цены за минуту")
head = re.sub(r'<meta name="description" content="[^"]*">',
              '<meta name="description" content="Концепция сайта: заборы из профлиста, евроштакетника, 3D-сетки под ключ в Новосибирске и области. '
              'Калькулятор стоимости, винтовые сваи, рассрочка 0%.">', head)
head = head.replace("#16261d", "#132010").replace("img/evro-15-640.webp 640w, img/evro-15-1280.webp 1280w", "img/hero-01-640.webp 640w, img/hero-01-1280.webp 1280w")
head = re.sub(r'<script type="application/ld\+json">.*?</script>',
              '<script type="application/ld+json">{"@context":"https://schema.org","@type":"HomeAndConstructionBusiness","name":"Заборы — установка заборов",'
              '"telephone":"+79134506655","email":"zabor3003@yandex.com","address":{"@type":"PostalAddress","addressLocality":"Новосибирск"},'
              '"areaServed":"Новосибирск и область","priceRange":"от 2600 ₽ за п.м."}</script>', head, flags=re.S)

top = f'''<body>
<div class="demo">Концепция нового сайта <span>Демонстрация · заявки получает студия «Форма сайта»</span></div>

<header class="header">
  <a class="brand" href="#top"><img src="img/logo.png" alt="" width="46" height="46"><span>ЗАБОРЫ<small>Производство и монтаж · Новосибирск</small></span></a>
  <nav aria-label="Разделы"><a href="#types">Заборы и цены</a><a href="#calc">Калькулятор</a><a href="#piles">Винтовые сваи</a><a href="#works">Работы</a><a href="#reviews">Отзывы</a></nav>
  <a class="header-phone" href="tel:+79134506655" data-goal="call">+7 (913) 450-66-55<small>Новосибирск и область</small></a>
</header>

<main id="top">
<section class="hero">
  <picture><source type="image/webp" srcset="img/hero-01-640.webp 640w, img/hero-01-1280.webp 1280w" sizes="100vw">
  <img class="hero-bg" src="img/hero-01-1280.webp" alt="Готовый забор у частного дома: брусчатка, газон, туи" width="1280" height="493" fetchpriority="high"></picture>
  <div class="hero-copy">
    <p class="eyebrow">НОВОСИБИРСК И ОБЛАСТЬ · СВОЁ ПРОИЗВОДСТВО</p>
    <h1>Забор под ключ<br><em>за 1–3 дня.</em><br>Платите потом.</h1>
    <p class="intro">Рассрочка 0% без банка, цена закреплена в договоре. Посчитайте свой забор за минуту — телефон для этого не нужен.</p>
    <div class="actions">
      <a class="button primary" href="#calc">Рассчитать мой забор ↗</a>
      <button class="text-button" type="button" data-start-quiz>Не знаю, какой выбрать — помогите</button>
    </div>
  </div>
</section>

<ul class="trust">
  <li><b>540+</b><span>заборов построено <br>в городе и области</span></li>
  <li><b>1–3 дня</b><span>монтаж <br>стандартного забора</span></li>
  <li><b>0%</b><span>рассрочка <br>без банка</span></li>
  <li><b>3D-модель</b><span>забора — до <br>начала работ</span></li>
</ul>

<section id="types">
  <div class="head"><div><p class="eyebrow">ЗАБОРЫ И ЦЕНЫ</p><h2>Шесть типов заборов. Цена — сразу.</h2></div>
    <p>Цены «от» — с сайта компании, за погонный метр. Итог фиксируется в договоре и после замера не меняется.</p></div>
  <div class="types">{types}</div>
  <p class="also">Ещё делаем: ворота любой сложности, фундаменты, демонтаж старого забора с вывозом. Евроштакетник продаём отдельно. <a href="#request">Спросить цену →</a></p>
</section>

'''

calc = h[h.index('<section id="calc"'):h.index('<section id="works">')]
chips = "".join(f'<label><input type="radio" name="type" value="{k}"{" checked" if k == "prof" else ""}><span>{n}</span></label>'
                for k, n in [("prof", "Профлист"), ("evro", "Евроштакетник"), ("d3", "3D-сетка"), ("wood", "Дерево"), ("weld", "Сварной"), ("brick", "Кирпичные столбы")])
calc = re.sub(r'(<fieldset class="chips" id="type-chips"><legend>Тип забора</legend>).*?(</fieldset>)', lambda m: m.group(1) + chips + m.group(2), calc, flags=re.S)
calc = calc.replace("от 114 000 ₽", "от 156 000 ₽").replace("60 м × от 1 900 ₽", "60 м × от 2 600 ₽")
calc = calc.replace("Цена «от» по прайсу с сайта компании. Высота, ворота и калитка входят в смету после бесплатного замера.",
                    "Цена «от» по сайту компании. Высота, ворота, калитка и сваи входят в смету после бесплатного замера — и дальше цена не меняется.")
calc = calc.replace("<span>Демонтаж старого забора</span>", "<span>Демонтаж старого забора с вывозом</span>")
calc = calc.replace('<label class="check"><input type="checkbox" id="x-doors">', '<label class="check"><input type="checkbox" id="x-piles"><span>Винтовые сваи вместо столбов в грунт</span></label>\n          <label class="check"><input type="checkbox" id="x-doors">')

rest = f'''<section id="piles" class="tint">
  <div class="piles">
    <div class="piles-photos">{pic("svai-01", "Столб забора на винтовой свае", 640, 1100, "(max-width:760px) 45vw, 25vw")}{pic("svai-02", "Забор из профлиста на винтовых сваях", 640, 1100, "(max-width:760px) 45vw, 25vw")}</div>
    <div><p class="eyebrow">ДЛЯ СИБИРСКОГО ГРУНТА</p><h2>Забор на винтовых сваях не «уйдёт» весной.</h2>
      <ul><li>Пучинистый грунт выталкивает обычные столбы — забор ведёт уже через пару зим</li><li>Сваи закручиваем ниже глубины промерзания</li><li>Подходит под любой тип забора</li></ul>
      <div class="depth"><div><b>2 м</b>глубина закручивания свай</div><div><b>1,5–1,7 м</b>глубина промерзания в регионе</div></div>
      <a class="button primary" href="#calc">Рассчитать забор на сваях ↗</a></div>
  </div>
</section>

<section id="works">
  <div class="head"><div><p class="eyebrow">НАШИ РАБОТЫ</p><h2>Заборы, которые уже стоят.</h2></div>
    <p>Фотографии с объектов компании в Новосибирске и области. Нажмите, чтобы увеличить.</p></div>
  <div class="filters" role="tablist" aria-label="Тип забора">
    <button role="tab" aria-selected="true" data-filter="all">Все</button><button role="tab" aria-selected="false" data-filter="prof">Профлист</button><button role="tab" aria-selected="false" data-filter="evro">Евроштакетник</button>
  </div>
  <div class="gallery" id="gallery"></div>
</section>

<section id="process" class="tint">
  <div class="head"><div><p class="eyebrow">КАК МЫ РАБОТАЕМ</p><h2>От звонка до готового забора.</h2></div></div>
  <ol class="steps">
    <li><h3>Бесплатный замер</h3><p>Мастер приезжает на участок, оценивает грунт и считает стоимость работ.</p></li>
    <li><h3>3D-модель и договор</h3><p>Показываем, как будет выглядеть забор, до начала работ. Цена и сроки закреплены в официальном договоре.</p></li>
    <li><h3>Монтаж за 1–3 дня</h3><p>Привозим материалы со своего производства и ставим забор. Старый демонтируем и вывозим.</p></li>
    <li><h3>Оплата и гарантия</h3><p>Можно в рассрочку 0% без банка. Если что-то обнаружится — приедем и бесплатно исправим.</p></li>
  </ol>
</section>

<section id="guarantee">
  <div class="head"><div><p class="eyebrow">ГАРАНТИИ</p><h2>Три гарантии в договоре.</h2></div></div>
  <div class="guar">
    <div><b>01 / ЦЕНА</b><h3>Точная стоимость</h3><p>Сразу называем конечную цену — дополнительных расходов не будет.</p></div>
    <div><b>02 / КАЧЕСТВО</b><h3>Исправим бесплатно</h3><p>Гарантия на выполненные работы. В случае проблемы приедем и бесплатно исправим.</p></div>
    <div><b>03 / МАТЕРИАЛЫ</b><h3>Проверенные бренды</h3><p>Используем проверенные европейские и отечественные материалы, своё производство — без накруток.</p></div>
  </div>
</section>

<section id="reviews" class="tint">
  <div class="head"><div><p class="eyebrow">ОТЗЫВЫ</p><h2>Что пишут заказчики на Авито.</h2></div>
    <p>Приведены дословно, орфография авторов сохранена. Скриншоты отзывов опубликованы на <a href="https://zaborpronsk.ru/" target="_blank" rel="noopener">сайте компании</a>.</p></div>
  <div class="reviews">{reviews}</div>
</section>

<section id="faq">
  <div class="faq"><div><p class="eyebrow">ВОПРОСЫ</p><h2>Спрашивают до заказа.</h2></div>
  <div>
    <details><summary>Сколько времени занимает монтаж?</summary><p>В большинстве случаев стандартный забор устанавливается за 1–3 дня. Точные сроки назовёт специалист при выезде на участок.</p></details>
    <details><summary>Можно посмотреть, как будет выглядеть забор, до начала работ?</summary><p>Да. Перед началом работ готовим 3D-модель будущего забора и показываем её вам.</p></details>
    <details><summary>Уберёте старый забор?</summary><p>Да, демонтируем старые заборы с вывозом. Стоимость демонтажа рассчитывается индивидуально.</p></details>
    <details><summary>Как работает рассрочка?</summary><p>Рассрочка 0% без банка — условия и срок фиксируются в договоре. Уточните их у специалиста на замере.</p></details>
    <details><summary>Нужно ли готовить участок?</summary><p>Нужно очистить территорию вдоль будущего забора от мусора. Этим может заняться наша команда.</p></details>
    <details><summary>В какое время года лучше ставить забор?</summary><p>Забор можно ставить в любое время года. Идеально — весна, когда днём и ночью плюсовая температура.</p></details>
  </div></div>
</section>

<section id="request" class="lead">
  <div>
    <p class="eyebrow">ЗАЯВКА</p><h2>Бесплатный замер и точная цена.</h2>
    <p>Оставьте телефон — перезвоним и договоримся о замере. Расчёт из калькулятора подставится сам.</p>
    <a class="big-phone" href="tel:+79134506655" data-goal="call">+7 (913) 450-66-55</a>
    <a class="mail" href="https://max.ru/u/f9LHodD0cOIzW_KwD6V95P4HzU-wEbE4bVD-aPUi25zRvevfIaOiN3lOX0Q" target="_blank" rel="noopener" data-goal="max">Написать в MAX</a><br>
    <a class="mail" href="mailto:zabor3003@yandex.com">zabor3003@yandex.com</a>
    <p class="addr">Новосибирск и область</p>
  </div>
  <form id="lead-form" action="send.php" method="post" novalidate>
    <input class="hp" type="text" name="_gotcha" tabindex="-1" autocomplete="off" aria-hidden="true">
    <label class="field" for="phone">Телефон<input id="phone" name="Телефон" type="tel" inputmode="tel" autocomplete="tel" placeholder="+7 (___) ___-__-__" required></label>
    <label class="field" for="name">Имя <i>· необязательно</i><input id="name" name="Имя" maxlength="80" autocomplete="given-name" placeholder="Как к вам обращаться"></label>
    <label class="field" for="place">Где участок <i>· необязательно</i><input id="place" name="Участок" maxlength="120" placeholder="Например, Бердск, СНТ «Ветеран»"></label>
    <label class="field" for="summary">Расчёт<textarea id="summary" name="Параметры" rows="4" maxlength="2000"></textarea></label>
    <button class="button primary" type="submit">Заказать замер ↗</button>
    <p class="hint">Демо-версия: заявка придёт в студию «Форма сайта», а не в компанию.</p>
    <p class="error" id="form-error" role="alert"></p>
    <p class="consent">Нажимая кнопку, вы соглашаетесь с <a href="policy.html" target="_blank" rel="noopener">политикой обработки персональных данных</a>.</p>
  </form>
</section>
</main>

<footer>
  <a class="brand" href="#top"><img src="img/logo.png" alt="" width="40" height="40" loading="lazy"><span>ЗАБОРЫ<small>Новосибирск и область</small></span></a>
  <p>Концепция для обсуждения с компанией.<br>Не официальный сайт и не публичная оферта.</p>
  <a href="https://zaborpronsk.ru/" target="_blank" rel="noopener">Действующий сайт ↗</a>
</footer>

<div class="mobile-bar"><a href="tel:+79134506655" data-goal="call">Позвонить</a><a href="#request" id="bar-chat">Заявка</a><a href="#calc">Цена ↗</a></div>

'''

tail = h[h.index('<dialog id="lead-dialog">'):]
tail = re.sub(r'config\.js\?v=\d+', "config.js?v=2", tail)
tail = re.sub(r'app\.js\?v=\d+', "app.js?v=2", tail)
(OUT / "index.html").write_text(head + top + calc + rest + tail, encoding="utf-8")


def fill(t):
    return t.replace("__BRAND__", "Заборы, Новосибирск").replace("__DISALLOW__", "Disallow: /").replace("__CANONICAL__", "https://zaborpro.formasaita.ru/")


(OUT / "send.php").write_text(fill((ROOT / "tools/shared/send.php").read_text(encoding="utf-8")).replace("__EMAIL__", ""), encoding="utf-8")
for n in ("robots.txt", ".htaccess"):
    (OUT / n).write_text(fill((ROOT / "builder/shared" / n).read_text(encoding="utf-8")), encoding="utf-8")
(OUT / "policy.html").write_text(fill((ROOT / "builder/shared/policy.html").read_text(encoding="utf-8"))
                                 .replace("__EMAIL__", "zabor3003@yandex.com").replace("__CITY__", "Новосибирск"), encoding="utf-8")
(OUT / "app.js").write_text((ROOT / "tools/fence/app.js").read_text(encoding="utf-8"), encoding="utf-8")
print("dist/zaborpro собран:", (OUT / "index.html").stat().st_size // 1024, "КБ html")
