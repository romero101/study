"""Маленький разборщик разметки статей — ровно то, что разрешено в content/stati/_BRIEF.md."""
import html
import re


def meta_and_body(text):
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    if not m:
        raise ValueError('нет frontmatter')
    meta = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            meta[k.strip()] = re.sub(r'\s+#.*$', '', v).strip()
    return meta, text[m.end():]


def inline(s):
    s = html.escape(s, quote=False)
    links = []

    def keep(m):
        href = m.group(2).replace('"', '%22')
        ext = href.startswith('http')
        attr = ' target="_blank" rel="noopener"' if ext else ''
        links.append(f'<a href="{href}"{attr}>{m.group(1)}</a>')
        return f'\x00{len(links) - 1}\x00'

    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', keep, s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?!\w)', r'<i>\1</i>', s)
    s = re.sub(r'\x00(\d+)\x00', lambda m: links[int(m.group(1))], s)
    return s


def slugify(s, used):
    base = re.sub(r'[^\w]+', '-', s.lower()).strip('-')[:48] or 'h'
    t, i = base, 2
    while t in used:
        t, i = f'{base}-{i}', i + 1
    used.add(t)
    return t


def render(body):
    """Возвращает (html, оглавление [(id, текст)], число знаков текста)."""
    out, toc, used = [], [], set()
    lines = body.strip('\n').split('\n')
    i, n = 0, len(lines)
    para = []

    def flush():
        if para:
            out.append('<p>' + inline(' '.join(para)) + '</p>')
            para.clear()

    while i < n:
        ln = lines[i].rstrip()
        if not ln.strip():
            flush(); i += 1; continue
        if ln.startswith('!!!'):
            flush()
            title = ln[3:].strip() or 'Коротко'
            j = i + 1
            box = []
            while j < n and not lines[j].startswith('!!!'):
                box.append(lines[j]); j += 1
            inner = ''.join('<p>' + inline(x.strip()) + '</p>' for x in '\n'.join(box).split('\n\n') if x.strip())
            out.append(f'<aside class="sum"><b class="sum-h">{inline(title)}</b>{inner}</aside>')
            i = j + 1; continue
        m = re.match(r'(#{2,3})\s+(.*)', ln)
        if m:
            flush()
            lvl, txt = len(m.group(1)), m.group(2).strip()
            hid = slugify(txt, used)
            if lvl == 2:
                toc.append((hid, re.sub(r'[*]', '', txt)))
            out.append(f'<h{lvl} id="{hid}">{inline(txt)}</h{lvl}>')
            i += 1; continue
        if ln.startswith('|'):
            flush()
            rows = []
            while i < n and lines[i].startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]); i += 1
            head, rest = rows[0], [r for r in rows[1:] if not all(re.fullmatch(r':?-{2,}:?', c) for c in r)]
            th = ''.join(f'<th>{inline(c)}</th>' for c in head)
            trs = ''.join('<tr>' + ''.join(f'<td data-h="{html.escape(re.sub(r"[*]", "", head[k]) if k < len(head) else "")}">{inline(c)}</td>' for k, c in enumerate(r)) + '</tr>' for r in rest)
            out.append(f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>')
            continue
        if ln.startswith('>'):
            flush()
            q = []
            while i < n and lines[i].startswith('>'):
                q.append(lines[i][1:].strip()); i += 1
            out.append('<blockquote><p>' + '<br>'.join(inline(x) for x in q if x) + '</p></blockquote>')
            continue
        m = re.match(r'(\d+)[.)]\s+(.*)|[-*]\s+(.*)', ln)
        if m:
            flush()
            ordered = m.group(1) is not None
            items = []
            while i < n:
                mm = re.match(r'(\d+)[.)]\s+(.*)', lines[i]) if ordered else re.match(r'[-*]\s+(.*)', lines[i])
                if mm:
                    items.append(mm.group(2) if ordered else mm.group(1)); i += 1
                elif lines[i].startswith('   ') and lines[i].strip() and items:
                    items[-1] += ' ' + lines[i].strip(); i += 1
                else:
                    break
            tag = 'ol' if ordered else 'ul'
            out.append(f'<{tag}>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + f'</{tag}>')
            continue
        para.append(ln.strip()); i += 1
    flush()
    htm = '\n'.join(out)
    chars = len(re.sub(r'<[^>]+>', '', htm))
    return htm, toc, chars
