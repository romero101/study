# -*- coding: utf-8 -*-
"""Версия лендинга одним файлом: картинки встроены как data-URI,
внешних файлов нет вообще. Нужна, чтобы показать демо по ссылке,
пока поддомены на хостинге не подняты."""
import base64, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render, sites
from sites import ALL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "dist", "_share")

def datauri(path):
    with open(path, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()

def main():
    os.makedirs(OUT, exist_ok=True)
    for s in ALL:
        s = dict(s)
        s["endpoint"] = ""            # включает демонстрационный режим форм
        doc = render.build(s)
        imgdir = os.path.join(ROOT, "dist", s["slug"], "img")

        # шапка документа собирается площадкой публикации — оставляем только
        # title, стили и разметку данных
        title = re.search(r"<title>.*?</title>", doc, re.S).group(0)
        style = re.search(r"<style>.*?</style>", doc, re.S).group(0)
        ld = "".join(re.findall(r'<script type="application/ld\+json">.*?</script>', doc, re.S))
        body = re.search(r"<body>(.*?)</body>", doc, re.S).group(1)

        def sub(m):
            f = os.path.join(imgdir, m.group(1))
            return 'src="%s"' % datauri(f) if os.path.exists(f) else m.group(0)
        body = re.sub(r'src="img/([^"]+)"', sub, body)

        out = "%s\n%s\n%s\n%s" % (title, style, ld, body.strip())
        path = os.path.join(OUT, s["slug"] + ".html")
        open(path, "w", encoding="utf-8").write(out)
        print("%-14s %6.0f КБ  %s" % (s["slug"], len(out.encode()) / 1024, path))

if __name__ == "__main__":
    main()
