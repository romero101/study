#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Грубый замер «как браузер»: HTML, затем все картинки/css/js со страницы в 6 потоков.
Печатает JSON: время ответа сервера, время HTML, время всей страницы, вес, число файлов.
Работает на python3.6 без сторонних пакетов. Запуск: python3 fetch.py URL [URL...]"""
import json, re, sys, time, ssl, gzip, zlib
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlsplit, quote
from urllib.request import Request, urlopen

UA = ('Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) '
      'Chrome/128.0 Mobile Safari/537.36')
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def iri(u):
    p = urlsplit(u)
    host = p.hostname.encode('idna').decode() if p.hostname else ''
    net = host + (':%d' % p.port if p.port else '')
    return p._replace(netloc=net, path=quote(p.path, safe='/%:@'), query=quote(p.query, safe='=&%:/?+')).geturl()


def get(u, timeout=60):
    t0 = time.time()
    r = urlopen(Request(iri(u), headers={'User-Agent': UA, 'Accept-Encoding': 'gzip, deflate'}), timeout=timeout, context=CTX)
    ttfb = time.time() - t0
    raw = r.read()
    t1 = time.time() - t0
    enc = r.headers.get('Content-Encoding', '')
    body = raw
    try:
        if enc == 'gzip':
            body = gzip.decompress(raw)
        elif enc == 'deflate':
            body = zlib.decompress(raw)
    except Exception:
        pass
    return r.geturl(), ttfb, t1, len(raw), body


def measure(url):
    out = {'url': url}
    try:
        final, ttfb, t_html, size, body = get(url)
    except Exception as e:
        out['error'] = str(e)[:120]
        return out
    html = body.decode('utf-8', 'ignore')
    out.update(ttfb=round(ttfb, 2), html_s=round(t_html, 2), html_kb=round(size / 1024))
    refs = set()
    for m in re.finditer(r'<(?:img|script|source|iframe)[^>]+?(?:src|data-src|data-original)=["\']([^"\']+)', html, re.I):
        refs.add(m.group(1))
    for m in re.finditer(r'<link[^>]+rel=["\'](?:stylesheet|preload)["\'][^>]*href=["\']([^"\']+)', html, re.I):
        refs.add(m.group(1))
    for m in re.finditer(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\'](?:stylesheet|preload)', html, re.I):
        refs.add(m.group(1))
    for m in re.finditer(r'url\(["\']?([^)"\']+\.(?:jpe?g|png|webp|gif|svg|woff2?))', html, re.I):
        refs.add(m.group(1))
    urls = []
    for r in refs:
        if r.startswith('data:') or r.startswith('#') or r.startswith('javascript'):
            continue
        urls.append(urljoin(final, r.strip()))
    urls = sorted(set(urls))

    def one(u):
        try:
            _, _, t, n, _ = get(u, 40)
            return n, t, None
        except Exception as e:
            return 0, 0, str(e)[:60]
    t0 = time.time()
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(one, urls))
    t_res = time.time() - t0
    total = size + sum(r[0] for r in res)
    out.update(files=len(urls) + 1, failed=sum(1 for r in res if r[2]), total_kb=round(total / 1024),
               page_s=round(t_html + t_res, 2))
    return out


if __name__ == '__main__':
    for u in sys.argv[1:]:
        print(json.dumps(measure(u), ensure_ascii=False), flush=True)
