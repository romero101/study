#!/usr/bin/env python3
"""Указатель конспектов роликов: docs/seo/konspekty/_INDEX.md. Запуск: python3 tools/studio/konspekty_index.py"""
import csv, glob, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
K = ROOT / 'docs' / 'seo' / 'konspekty'
vids = {r['url'].split('v=')[-1]: r for r in csv.DictReader(open(ROOT / 'docs' / 'seo' / 'videos.csv', encoding='utf-8'))
        if r['platform'] == 'youtube'}
rows = []
for f in sorted(x for x in K.glob('*.md') if x.name not in ('_HOWTO.md', '_INDEX.md')):
    s = f.read_text(encoding='utf-8')
    fm = s.split('---')[1] if s.startswith('---') else ''

    def g(k):
        m = re.search(r'^%s:\s*(.*)$' % k, fm, re.M)
        return m.group(1).strip() if m else ''

    nums = 0
    if '## Цифры' in s:
        block = s.split('## Цифры')[-1].split('\n## ')[0]
        nums = len([l for l in block.splitlines() if l.startswith('|') and not re.match(r'\|\s*(:?-|Значение)', l)])
    empty = 'расшифровки нет' in s.lower() and len(s) < 1200
    rows.append((f.stem, g('title') or vids.get(f.stem, {}).get('title', ''), g('channel'), g('published'), g('for'), nums, empty))

out = ['# Указатель конспектов роликов', '',
       'Конспекты лежат в `docs/seo/konspekty/<ID>.md`. Дословных расшифровок нет и не будет.', '',
       '| ID | Ролик | Кто говорит | Когда | Для каких тем | Цифр | Статус |', '|---|---|---|---|---|---|---|']
for v, t, c, p, fo, n, e in rows:
    out.append(f'| {v} | {t[:80]} | {c[:30]} | {p[:12]} | {fo[:90]} | {n} | {"нет расшифровки" if e else "снят"} |')
(K / '_INDEX.md').write_text('\n'.join(out) + '\n', encoding='utf-8')
print(len(rows), 'файлов; без расшифровки:', sum(1 for r in rows if r[6]), '; цифр всего:', sum(r[5] for r in rows))
