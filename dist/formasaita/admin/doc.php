<?php
/* Печатная форма документа: /admin/doc.php?id=d1. Только для вошедших. Кнопка «Печать»
   в браузере даёт PDF (Сохранить как PDF). ?plain=1 — без панели, для автоматической печати. */
require __DIR__ . '/lib.php';
require __DIR__ . '/templates.php';
crm_boot();
if (!crm_logged_in() || crm_must_change()) { header('Location: ./'); exit; }
$D = crm_docs();
$i = crm_doc_find($D, (string)($_GET['id'] ?? ''));
if ($i < 0) { http_response_code(404); exit('Документ не найден'); }
$doc = $D['docs'][$i];
$title = doc_title($doc);
$lead = ''; foreach (crm_read()['leads'] as $l) if ($l['id'] === ($doc['lead_id'] ?? '')) $lead = $l['company'];
?><!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title><?= h($title) ?><?= $lead ? ' — ' . h($lead) : '' ?></title>
<style>
*{box-sizing:border-box}
html{background:#e9edf2}
body{margin:0;font:12pt/1.45 "Times New Roman",Times,serif;color:#000}
.bar{position:sticky;top:0;background:#16202b;color:#fff;padding:10px 16px;display:flex;gap:14px;align-items:center;font:14px -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;z-index:2}
.bar a,.bar button{color:#fff;text-decoration:none;font:inherit}
.bar button{background:#4558ed;border:0;border-radius:8px;padding:8px 14px;font-weight:700;cursor:pointer}
.bar .t{margin-left:auto;color:#9aa8b6}
.page{background:#fff;width:210mm;min-height:297mm;margin:16px auto;padding:20mm 18mm 18mm;box-shadow:0 8px 30px rgba(0,0,0,.12)}
h1{font-size:16pt;text-align:center;margin:0 0 6pt;letter-spacing:.01em}
h2{font-size:12pt;margin:12pt 0 4pt;text-align:center;page-break-after:avoid}
p{margin:0 0 6pt;text-align:justify}
p.sub{text-align:center;margin-bottom:10pt}
p.pt{text-indent:0}
p.tot{text-align:right;margin-top:6pt}
table{border-collapse:collapse;width:100%}
table.hdr{margin:8pt 0 10pt}
table.hdr td{padding:2pt 0;vertical-align:top}
table.hdr td.k{width:22%;color:#333}
table.hdr td.r,td.r{text-align:right}
table.grid{margin:6pt 0}
table.grid th,table.grid td{border:1px solid #000;padding:4pt 6pt;vertical-align:top;font-size:11pt}
table.grid th{font-weight:700;text-align:center;background:#f2f2f2}
table.grid td.c{text-align:center;white-space:nowrap}
table.grid td.r{white-space:nowrap}
table.bank td{border:1px solid #000;padding:4pt 6pt;font-size:10.5pt;vertical-align:top}
table.bank td.l{width:55%}
table.sign{margin-top:16pt;page-break-inside:avoid}
table.sign td{width:50%;vertical-align:top;padding:0 10pt 0 0;font-size:10.5pt}
table.sign td+td{padding:0 0 0 10pt}
.sign .who{font-weight:700;font-size:12pt;margin-bottom:4pt}
.sign .req{line-height:1.4;margin-bottom:14pt}
.sign .sig{margin-top:22pt;white-space:nowrap}
.sign .mp{color:#555;font-size:10pt}
.sig1{margin-top:26pt}
table.qr{margin-top:14pt;page-break-inside:avoid}
table.qr td{vertical-align:middle;padding:0}
table.qr td.code{width:40mm}
table.qr td.code svg{width:36mm;height:36mm;display:block}
table.qr td.txt{padding-left:6mm;font-size:10.5pt;line-height:1.4}
@page{size:A4;margin:16mm 14mm}
@media print{html{background:#fff}.bar{display:none}.page{width:auto;min-height:0;margin:0;padding:0;box-shadow:none}}
</style>
</head>
<body>
<?php if (empty($_GET['plain'])): ?>
<div class="bar"><a href="./#acc">← Бухгалтерия</a><button type="button" onclick="print()">Печать / сохранить PDF</button><span class="t"><?= h($title) ?><?= $lead ? ' · ' . h($lead) : '' ?> · <?= h($doc['status']) ?></span></div>
<?php endif; ?>
<div class="page"><?= doc_render($doc, $D) ?></div>
<?php if ($doc['type'] === 'invoice'): ?>
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js"></script>
<script>
document.querySelectorAll('[data-qr]').forEach(function (el) {
  try { qrcode.stringToBytes = qrcode.stringToBytesFuncs['UTF-8']; var q = qrcode(0, 'M'); q.addData(el.dataset.qr, 'Byte'); q.make(); el.innerHTML = q.createSvgTag({ cellSize: 3, margin: 2, scalable: true }); }
  catch (e) { el.textContent = 'QR не построился: ' + e.message; }
});
</script>
<?php endif; ?>
</body>
</html>
