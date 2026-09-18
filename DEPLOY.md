# Что заливать на REG.RU (состояние на 18.09.2026)

Хостинг отдаёт статику через nginx: `.htaccess` для .json/.log **не работает**.
Поэтому всё закрытое хранится в `.php`-файлах с `<?php exit; ?>` в первой строке.

## 1. Срочно: админка — `/www/formasaita.ru/admin/`

Сейчас `https://formasaita.ru/admin/data/leads.json` открывается всем по прямой ссылке.

1. Залить поверх файлы из `dist/formasaita/admin/`: `index.php`, `lib.php`, `api.php`, `app.js`, `data/index.php`.
   **Папку `data/` на сервере не затирать** — там живые правки менеджера.
2. Открыть `https://formasaita.ru/admin/` — при первом запросе `leads.json` переедет в `data/store.php` и удалится.
3. Войти `админ` / `admin` — система сразу потребует задать свой пароль (от 8 символов). До смены воронка закрыта.
4. Проверить: `https://formasaita.ru/admin/data/leads.json` → 404, `.../data/store.php` → пустая страница.

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
