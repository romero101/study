#!/usr/bin/env python3
"""Проверка статей без сборки (ничего не пишет): python3 tools/studio/check.py [slug …]"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import build

arts, problems = build.load_articles()
want = sys.argv[1:]
bad = [p for p in problems if not want or any(p.startswith(w) for w in want)]
for a in arts:
    if want and a['slug'] not in want:
        continue
    n = a['html'].count('<figure class="fig"') + a['html'].count('class="widget"') + a['html'].count('class="qz"')
    print(f"{a['slug']}: иллюстраций {n}")
print('\n'.join('!! ' + p for p in bad) or 'ошибок нет')
sys.exit(1 if bad else 0)
