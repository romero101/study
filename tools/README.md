# Инструменты студии

| Что | Где | Как запускать |
|---|---|---|
| Движок лендингов **заборов** | `tools/fence/app.js` + `config.js` рядом со страницей | новая площадка: скопировать `dist/strana-zaborov/`, заменить `config.js`, тексты и фото; пример генератора — `tools/fence/build_zaborpro.py` |
| Движок лендингов **скважин** | `tools/well/` | `python3 tools/well/build.py <slug>` → `dist/well-<slug>/`; клиент = `clients/<slug>.json` + папка jpg |
| Точечная доработка уже выложенных лендингов скважин | `tools/upgrade.py` | `python3 tools/upgrade.py` → `dist/topdrillrus-v2/`, `dist/skvazhina-ekb-v2/` (это то, что на боевом) |
| Общий приём заявок | `tools/shared/send.php` | кладётся в каждую площадку сборкой |

Новый клиент по скважинам: скопировать `tools/well/clients/topdrillrus.json`, заменить бренд, телефон, тарифы (`rates`: min/max за метр и предел глубины),
факты (`trust`), карточки услуг, альбомы, отзывы (дословно, с источником) и вопросы. Фото — jpg в `tools/well/clients/<slug>/`:
`hero-result.jpg` (результат, а не стройплощадка), `scheme.jpg`, `alb-*.jpg`. Нужны `cwebp` и macOS `sips`.

Правила, общие для всех демо, — в памяти проекта (`formasaita-landing-rules`): результат на первом экране, без повторов блоков,
отзывы дословно, расчёт в мессенджер — только MAX, демо клиентов не показывать на сайте студии.
