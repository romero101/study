# Как снять конспект ролика YouTube (проверено 21.09.2026)

Работаем в Chrome пользователя через инструменты `mcp__claude-in-chrome__*` (загрузи их через ToolSearch одним запросом:
`select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__javascript_tool,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__tabs_close_mcp,mcp__claude-in-chrome__browser_batch`).
Сначала `tabs_context_mcp` с createIfEmpty, затем `tabs_create_mcp` — СВОЯ вкладка, чужие не трогать. В конце свою вкладку закрыть.

На каждый ролик:
1. `navigate` на watch-адрес, подождать 3 с.
2. `javascript_tool`:
   `const v=document.querySelector('video');if(v)v.pause();const ex=document.querySelector('#expand');if(ex)ex.click();await new Promise(r=>setTimeout(r,800));const b=document.querySelector('ytd-video-description-transcript-section-renderer button');if(b)b.click();await new Promise(r=>setTimeout(r,4000));({hasBtn:!!b,title:document.title,channel:(document.querySelector('ytd-channel-name a')||{}).textContent,date:(document.querySelector('#info-strings yt-formatted-string, #info span:nth-child(3)')||{}).textContent})`
   Если `hasBtn:false` — у ролика нет расшифровки: запиши это в конспект-заглушку и иди дальше.
3. `computer` screenshot со `scale: 0.1` — без него фоновая вкладка не отрисует панель.
4. `javascript_tool`: панель — `ytd-engagement-panel-section-list-renderer` с `visibility="ENGAGEMENT_PANEL_VISIBILITY_EXPANDED"` и target-id, содержащим `transcript`
   (сейчас это `engagement-panel-searchable-transcript`). Взять innerText, выкинуть строки-таймкоды `/^\d{1,2}:\d{2}(:\d{2})?$/`.
   Если длина 0 — подождать ещё 3 с и повторить шаги 3–4.
5. Результат JS режется примерно на 1000 знаках, поэтому текст кладём в страницу и читаем `get_page_text`:
   `const d=document.createElement('article');d.textContent=window.__t;document.body.replaceChildren(d);d.textContent.length`
   (innerHTML запрещён политикой TrustedHTML — только createElement/textContent). Длинные ролики читать кусками по 40–50 тыс. знаков:
   перед `get_page_text` класть в `d.textContent` срез `window.__t.slice(a,b)`.
Грабли (проверено 21.09.2026):
- описание иногда раскрывается дольше 800 мс, и скрипт возвращает `hasBtn:false`, хотя расшифровка есть — ждать после `#expand` 2 с и искать кнопку повторно, прежде чем писать «расшифровки нет»;
- у части роликов расшифровка открывается в новой панели `PAmodern_transcript_view`, селектор возвращает длину 0 — тогда брать текст обычным `get_page_text` со страницы;
- на длинных роликах панель прогружается дольше: после шага 3 ждать ещё 4–5 с и делать второй снимок экрана;
- автоматическая расшифровка искажает большие числа — сомнительные цифры помечать в таблице, а не угадывать.
6. Дословную расшифровку НЕ сохранять. Сохраняем только конспект.

## Формат конспекта — `docs/seo/konspekty/<id-ролика>.md`

```
---
url: https://www.youtube.com/watch?v=…
title: название ролика
channel: канал / кто говорит
published: дата или год, если видно
for: [темы и ниши, которым пригодится: директ, карты, заборы, ремонт-квартир, …]
---

## О чём ролик
2–3 предложения.

## Тезисы
10–25 пунктов своими словами: что именно советуют делать, в каком порядке, почему. Конкретика, а не «важно настроить рекламу».
Приёмы, последовательности шагов, типичные ошибки, возражения клиентов, примеры формулировок объявлений и офферов.

## Цифры
| Значение | Единица | К чему относится | Когда / где | Со слов кого |
|---|---|---|---|---|
Все числа из ролика: цена клика, цена заявки, бюджет, конверсия, число заявок, сроки, чек, маржа, доли. Если спикеры расходятся — обе цифры.
Если цифр нет — так и написать.

## Что пригодится для статей
3–8 пунктов: какой тезис в какую тему/нишу ложится.

## Оговорки
Кто говорит и в чём его интерес (продаёт услуги, курс, сервис), год, регион, что может быть устаревшим.
```

Цитаты — не длиннее 15 слов и не больше одной на конспект. Никакой отсебятины: только то, что сказано в ролике.
