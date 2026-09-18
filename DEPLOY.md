# Выкладка на REG.RU

**18.09.2026 всё залито на боевой** по SSH (`ssh formasaita` → server280.hosting.reg.ru, u3380158, вход по ключу).
Резервная копия прежних файлов: `~/backups/formasaita-sites-2026-09-18-before-v2.tgz` на сервере.

Повторная выкладка:

    rsync -az --exclude leads.json --exclude store.php --exclude users.php --exclude throttle.php \
          --exclude leads.log.php dist/formasaita/ formasaita:www/formasaita.ru/
    rsync -az --exclude leads.log.php dist/topdrillrus-v2/   formasaita:www/topdrillrus.formasaita.ru/
    rsync -az --exclude leads.log.php dist/skvazhina-ekb-v2/ formasaita:www/skvazhina-ekb.formasaita.ru/

Грабли этого хостинга:
- Apache стоит за nginx: правило «RewriteCond %{HTTPS} !=on» даёт бесконечный 301. Https-редирект — только в панели.
- На пути /admin/ хостинг ставит проверку от ботов: первый ответ — заглушка 124 байта с cookie RCPC и
  переходом на `?attempt=1`. Код 200 на любой адрес под /admin/ без cookie ничего не значит.
  (Из-за этого 18.09 показалось, что leads.json открыт наружу — на деле админки на сервере тогда не было.)
- Закрытые данные всё равно держим в .php с `<?php exit; ?>`: от настроек сервера не зависит.

## Демо для клиентов — `formasaita.ru/demo/<slug>/`

Решение Романа (18.09.2026): поддомены под новые демо не заводим, все демо живут в `~/www/formasaita.ru/demo/<slug>/`.
Раздел закрыт в robots.txt, у каждой страницы noindex, список папок наружу не отдаётся (`demo/index.php` отвечает 404).
На сайте студии ссылок на демо нет — адрес получает только клиент от менеджера.

    rsync -az --exclude leads.log.php dist/<slug>/ formasaita:www/formasaita.ru/demo/<slug>/

Сейчас там: strana-zaborov, zaborpro, arhastroy, russtroy. Два лендинга скважин остались на своих поддоменах.

## 1. Админка — `/www/formasaita.ru/admin/`

Вход `админ` / `admin` → система сразу требует задать свой пароль (от 8 символов). До смены воронка закрыта.
**Папку `data/` при выкладке не затирать** — там живые сделки (`store.php`) и пользователи (`users.php`).

Забыли пароль: удалить `admin/data/users.php` — вернётся стартовая пара с обязательной сменой.
После 5 неверных попыток вход с этого адреса закрыт на 15 минут (`data/throttle.php`).

## 2. Сайт студии — `/www/formasaita.ru/`

Залить `dist/formasaita/`: `index.html`, `send.php`, `policy.html`, `robots.txt`, `img/`.
Заявка с формы сразу становится сделкой в воронке с меткой «с сайта» и пишется в `leads.log.php`.
В `send.php` вписать почту и токен Telegram-бота. В `policy.html` — город, почту, реквизиты (поиск `СОГЛАСОВАТЬ`).

## 3. Лендинги — `/www/<slug>.formasaita.ru/`

Залить **содержимое** `dist/topdrillrus-v2/` и `dist/skvazhina-ekb-v2/` поверх текущих файлов.
Это те же страницы, что лежат на хостинге (снимок — `dist/<slug>-original/`), плюс доработки из `tools/`.
Пересборка: `python3 tools/upgrade.py` (нужны `cwebp` и macOS `sips`).

Пока `"demo": True` в `tools/upgrade.py`: страница закрыта от индексации, заявки уходят в студию
(журнал `leads.log.php` рядом с сайтом; почта и Telegram — в `send.php`). Для боевого запуска поставить
`"demo": False`, вписать `"email"` клиента и пересобрать.
