#!/usr/bin/env python3
"""Скриншоты блоков наших демо для статей — обезличенно: без названий, телефонов и адресов клиентов.

Берёт dist/<demo>/index.html, оставляет на странице один блок, заменяет имена и контакты,
снимает Chrome headless при ширине телефона, кладёт webp в content/stati/img/ (сборка копирует их на сайт).
Запуск: python3 tools/studio/shots.py [имя_снимка …]
"""
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DIST = ROOT / 'dist'
OUT = ROOT / 'content' / 'stati' / 'img'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

# имя: (демо, селектор блока, [действия js до снимка], ширина)
SHOTS = json.loads((Path(__file__).parent / 'shots.json').read_text(encoding='utf-8'))

INJECT = r'''
<script>
window.addEventListener('load', function () {
  setTimeout(function () {
    try { %(actions)s } catch (e) {}
    var t = document.querySelector(%(sel)s);
    if (!t) { document.title = 'H:0'; return; }
    var keep = t, b = document.body;
    b.innerHTML = ''; b.appendChild(keep);
    b.style.cssText = 'margin:0;padding:0;background:#fff;min-height:0;width:%(w)spx;overflow:hidden';
    document.documentElement.style.cssText = 'scroll-behavior:auto';
    var R = %(repl)s;
    var w = document.createTreeWalker(b, NodeFilter.SHOW_TEXT), n;
    while ((n = w.nextNode())) {
      var s = n.nodeValue;
      R.forEach(function (r) { s = s.replace(new RegExp(r[0], 'gi'), r[1]); });
      s = s.replace(/[\w.+-]+@[\w-]+\.[\w.]+/g, 'mail@example.ru');
      s = s.replace(/(\+7|8)[\s(–-]*\d{3}[\s)–-]*\d{3}[\s–-]*\d{2}[\s–-]*\d{2}/g, '+7 (000) 000-00-00');
      n.nodeValue = s;
    }
    b.querySelectorAll('img[alt*="лого" i],.logo img,[class*="logo"] img').forEach(function (i) { i.remove(); });
    document.title = 'H:' + Math.ceil(keep.getBoundingClientRect().height + keep.getBoundingClientRect().top);
  }, 700);
});
</script>
'''


def chrome(*args):
    return subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
                           '--allow-file-access-from-files', '--virtual-time-budget=4000', *args],
                          capture_output=True, text=True, timeout=90)


def shoot(name, spec):
    src = DIST / spec['demo'] / 'index.html'
    html = src.read_text(encoding='utf-8')
    inj = INJECT % {'sel': json.dumps(spec['sel']), 'actions': spec.get('js', ''),
                    'repl': json.dumps(spec.get('replace', []), ensure_ascii=False), 'w': spec.get('w', 390)}
    tmp = src.parent / '_shot.html'
    tmp.write_text(html.replace('</body>', inj + '</body>'), encoding='utf-8')
    try:
        w = spec.get('w', 390)
        dom = chrome(f'--window-size={max(w, 520)},900', '--dump-dom', tmp.as_uri()).stdout
        if '--text' in sys.argv:
            body = re.sub(r'<script.*?</script>|<style.*?</style>', '', dom.split('<body', 1)[-1], flags=re.S)
            print('DUMP', name, '::', re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body))[:1500]); return
        m = re.search(r'<title>H:(\d+)</title>', dom)
        h = int(m.group(1)) if m else 0
        if not h:
            print('!!', name, 'блок не найден'); return
        h = min(h, spec.get('maxh', 2400))
        png = Path(tempfile.gettempdir()) / f'shot-{name}.png'
        chrome(f'--window-size={max(w, 520)},{h}', '--force-device-scale-factor=2', f'--screenshot={png}', tmp.as_uri())
        OUT.mkdir(parents=True, exist_ok=True)
        subprocess.run(['cwebp', '-quiet', '-q', '82', '-crop', '0', '0', str(w * 2), str(h * 2), str(png), '-o', str(OUT / f'{name}.webp')], check=True)
        print('ok', name, f'{w}x{h}', (OUT / f'{name}.webp').stat().st_size // 1024, 'КБ')
    finally:
        tmp.unlink(missing_ok=True)


if __name__ == '__main__':
    want = [a for a in sys.argv[1:] if not a.startswith('--')]
    for name, spec in SHOTS.items():
        if not want or name in want:
            shoot(name, spec)
