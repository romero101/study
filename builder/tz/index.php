<?php
/* Согласование ТЗ по личной ссылке /tz/?k=<ключ>. Ключ и имя документа лежат в сделке (tz.key, tz.doc),
   текст ТЗ — в admin/tz/<doc>.php. Ответы пишутся в сделку (tz.answers) и в её историю. */
require __DIR__ . '/../admin/lib.php';
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('Referrer-Policy: no-referrer');
header('Cache-Control: no-store');

$key  = (string)($_POST['k'] ?? $_GET['k'] ?? '');
$data = crm_read();
$idx  = -1;
if (preg_match('/^[a-f0-9]{16,40}$/', $key)) {
    foreach ($data['leads'] as $i => $l) {
        if (!empty($l['tz']['key']) && hash_equals((string)$l['tz']['key'], $key)) { $idx = $i; break; }
    }
}
$T = null;
if ($idx >= 0) {
    $doc = preg_replace('/[^a-z0-9_-]/', '', (string)($data['leads'][$idx]['tz']['doc'] ?? ''));
    $f = __DIR__ . '/../admin/tz/' . $doc . '.php';
    if ($doc !== '' && is_file($f)) $T = require $f;
}
if (!$T) $idx = -1;

$total = 0; if ($T) foreach ($T['sections'] as $s0) $total += count($s0['points']);
$clean = function ($v, $max) { return mb_substr(trim(preg_replace('/\r\n?/', "\n", strip_tags((string)$v))), 0, $max); };
$err = ''; $saved = false; $posted = null;
if ($idx >= 0 && ($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
    $Z = $data['leads'][$idx]['tz'];
    $ans = ['who' => $clean($_POST['who'] ?? '', 200), 'general' => $clean($_POST['general'] ?? '', 4000), 'pts' => [], 'q' => []];
    foreach ($T['sections'] as $s) foreach ($s['points'] as $p) {
        $v = (string)($_POST['v'][$p['id']] ?? '');
        $c = $clean($_POST['c'][$p['id']] ?? '', 2000);
        if (!in_array($v, ['ok', 'change'], true)) $v = $c !== '' ? 'change' : '';
        if ($v !== '' || $c !== '') $ans['pts'][$p['id']] = ['v' => $v, 'c' => $c];
    }
    foreach ($T['questions'] as $q) { $a = $clean($_POST['q'][$q['id']] ?? '', 2000); if ($a !== '') $ans['q'][$q['id']] = $a; }
    $posted = $ans;
    $missChange = [];
    foreach ($ans['pts'] as $id => $a) if ($a['v'] === 'change' && $a['c'] === '') $missChange[] = $id;
    if (!empty($_POST['_gotcha']) || (isset($_POST['_elapsed']) && (int)$_POST['_elapsed'] < 3)) {
        $saved = true;
    } elseif ($ans['who'] === '') {
        $err = 'Укажите, пожалуйста, имя и должность — вверху страницы.';
    } elseif ($missChange) {
        $err = 'В пунктах ' . implode(', ', $missChange) . ' отмечено «Нужно иначе» — напишите, как именно.';
    } elseif (!empty($Z['updated_ts']) && time() - (int)$Z['updated_ts'] < 5) {
        $err = 'Слишком часто. Подождите пару секунд и отправьте ещё раз.';
    } else {
        $first = empty($Z['answers']);
        if (!$first) $Z['history'] = array_slice(array_merge($Z['history'] ?? [], [['at' => $Z['updated_at'] ?? '', 'answers' => $Z['answers']]]), -5);
        $Z['answers'] = $ans;
        if ($first) $Z['sent_at'] = crm_now();
        $Z['updated_at'] = crm_now(); $Z['updated_ts'] = time();
        $data['leads'][$idx]['tz'] = $Z;
        $data['leads'][$idx]['updated'] = crm_now();
        $ok = 0; $ch = 0; foreach ($ans['pts'] as $a) { if ($a['v'] === 'ok') $ok++; if ($a['v'] === 'change') $ch++; }
        $txt = 'ТЗ ' . ($first ? 'согласовано и отправлено' : 'дополнено') . ' (' . $ans['who'] . '): согласен — ' . $ok . ' из ' . $total . ', нужно иначе — ' . $ch .
               ', ответов на вопросы — ' . count($ans['q']) . ' из ' . count($T['questions']) . '.';
        foreach ($T['sections'] as $s) foreach ($s['points'] as $p) {
            $a = $ans['pts'][$p['id']] ?? null;
            if ($a && ($a['v'] === 'change' || $a['c'] !== '')) $txt .= "\n\n" . $p['id'] . ' — ' . ($a['v'] === 'change' ? 'НУЖНО ИНАЧЕ' : 'комментарий') . ': ' . $a['c'] . "\n(пункт: " . mb_substr($p['text'], 0, 140) . '…)';
        }
        $qn = 0;
        foreach ($T['questions'] as $q) { $qn++; if (isset($ans['q'][$q['id']])) $txt .= "\n\nВопрос " . $qn . ': ' . mb_substr($q['text'], 0, 90) . "…\nОтвет: " . $ans['q'][$q['id']]; }
        if ($ans['general'] !== '') $txt .= "\n\nОбщий комментарий: " . $ans['general'];
        $unmarked = $total - count(array_filter($ans['pts'], function ($a) { return $a['v'] !== ''; }));
        if ($unmarked > 0) $txt .= "\n\nБез отметки: " . $unmarked . ' пунктов.';
        $data['leads'][$idx]['comments'][] = ['at' => crm_now(), 'who' => mb_substr($ans['who'], 0, 60), 'kind' => 'brief', 'text' => mb_substr($txt, 0, 12000)];
        if (!crm_write($data)) $err = 'Не удалось сохранить. Попробуйте через минуту — черновик остаётся в этом браузере.';
        else $saved = true;
    }
}
$lead = $idx >= 0 ? $data['leads'][$idx] : null;
if (!$lead) http_response_code(404);
$Z = $lead['tz'] ?? [];
$A = $posted && $err ? $posted : ($Z['answers'] ?? ['who' => '', 'general' => '', 'pts' => [], 'q' => []]);
?><!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title><?= $T ? h($T['title']) . ' — согласование' : 'Техническое задание' ?></title>
<meta name="theme-color" content="#172333">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<style>
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font:400 16.5px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;color:#16202b;background:#eef2f6}
a{color:#2b46d6}
h1,h2{margin:0 0 .35em;line-height:1.2;letter-spacing:-.02em}
h1{font-size:clamp(25px,4.6vw,34px)}
h2{font-size:20px}
p{margin:0 0 10px}
button,input,textarea{font:inherit;color:inherit}
:focus-visible{outline:3px solid #4558ed;outline-offset:2px;border-radius:6px}
.top{background:#172333;color:#fff}
.top .in{max-width:860px;margin:0 auto;padding:12px 16px;display:flex;align-items:center;gap:12px}
.top svg{width:34px;height:34px;flex:0 0 auto}
.top b{font-size:17px;letter-spacing:-.02em}
.top a{margin-left:auto;color:#cdd8e3;text-decoration:none;font-size:15px;white-space:nowrap}
.wrap{max-width:860px;margin:0 auto;padding:22px 16px 120px}
.card{background:#fff;border-radius:16px;padding:22px 20px;box-shadow:0 2px 12px rgba(16,32,48,.06);margin-bottom:16px}
.lead p{color:#41586e}
.meta{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:14.5px;color:#41586e;margin-top:6px}
.who label{display:block;font-weight:700;margin-bottom:6px}
input[type=text],textarea{width:100%;min-height:46px;padding:10px 12px;border:2px solid #d9e2ec;border-radius:10px;background:#fff;font-size:16px}
textarea{min-height:60px;resize:none;overflow:hidden;line-height:1.45}
input:focus,textarea:focus{outline:none;border-color:#4558ed;box-shadow:0 0 0 3px rgba(69,88,237,.15)}
.ok,.err{border-radius:12px;padding:14px 16px;margin-bottom:16px;font-weight:600}
.ok{background:#e9f6ee;border:1px solid #b5dcc3;color:#174d2c}
.err{background:#fff1f0;border:1px solid #f0b3ac;color:#9e2114}
.sec h2{margin-bottom:6px}
.pt{padding:14px 0;border-top:1px solid #eef2f6}
.pt .t{display:flex;gap:10px}
.pt .t i{font-style:normal;font-weight:800;color:#8a96a3;min-width:30px;font-size:14px;padding-top:1px}
.pt .t p{margin:0}
.ch{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 0 40px}
.ch label{position:relative;display:inline-flex;align-items:center;min-height:40px;padding:7px 14px;border:2px solid #d9e2ec;border-radius:99px;cursor:pointer;font-size:14.5px;background:#fff}
.ch input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}
.ch label:has(input[value=ok]:checked){border-color:#2f9e52;background:#e9f6ee;font-weight:700;color:#174d2c}
.ch label:has(input[value=change]:checked){border-color:#c98a12;background:#fff6e0;font-weight:700;color:#6b4c07}
.ch label:has(input:focus-visible){outline:3px solid #4558ed;outline-offset:2px}
.cm{margin:8px 0 0 40px}
.cm[hidden]{display:none}
.q{padding:12px 0;border-top:1px solid #eef2f6}
.q label{display:block;font-weight:700;margin-bottom:6px}
.bar{position:fixed;left:0;right:0;bottom:0;background:#fff;border-top:1px solid #dde6ee;padding:10px 16px calc(10px + env(safe-area-inset-bottom));z-index:5}
.bar .in{max-width:860px;margin:0 auto;display:flex;align-items:center;gap:12px}
.bar .cnt{font-size:14px;color:#41586e;line-height:1.3}
.bar .cnt b{display:block;font-size:15.5px;color:#16202b}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:11px 20px;border-radius:12px;font-weight:700;border:0;cursor:pointer;background:#4558ed;color:#fff;font-size:16px;white-space:nowrap}
.btn:hover{background:#3547d1}
.btn--gh{background:#fff;color:#1c4d85;border:2px solid #d9e2ec}
.btn--gh:hover{background:#f4f8fb}
.bar .btn:first-of-type{margin-left:auto}
.foot{color:#6a7686;font-size:14px}
.none{min-height:70vh;display:grid;place-items:center;padding:20px}
.none div{background:#fff;padding:32px;border-radius:16px;max-width:420px}
@media (max-width:560px){.ch,.cm{margin-left:0}.bar .pr{display:none}}
@media print{body{background:#fff;font-size:12pt}.top,.bar,.who,.ch,.cm textarea:placeholder-shown,.noprint{display:none!important}.card{box-shadow:none;padding:0 0 10px;margin:0}.pt{page-break-inside:avoid}.wrap{padding:0}textarea{border:0;padding:0;min-height:0}}
</style>
</head>
<body>
<div class="top"><div class="in">
  <svg aria-hidden="true" viewBox="0 0 64 64"><rect width="64" height="64" rx="16" fill="#4558ed"/><text x="32" y="46" text-anchor="middle" font-family="system-ui,-apple-system,Roboto,Arial,sans-serif" font-weight="800" font-size="44" fill="#fff">ф</text></svg>
  <b>Форма сайта</b>
  <a href="tel:+79290537603">+7 (929) 053-76-03</a>
</div></div>
<?php if (!$lead): ?>
<div class="none"><div>
  <h1 style="font-size:24px">Ссылка не действует</h1>
  <p>Документ открывается только по личной ссылке из сообщения менеджера. Напишите нам — пришлём новую.</p>
  <p><a href="tel:+79290537603">+7 (929) 053-76-03</a></p>
</div></div>
<?php else: ?>
<main class="wrap">
  <div class="card lead">
    <h1><?= h($T['title']) ?><br><span style="color:#4558ed;font-size:.7em">черновик на согласование</span></h1>
    <p><?= !empty($Z['name']) ? h($Z['name']) . ', ' . mb_strtolower(mb_substr($T['intro'], 0, 1)) . mb_substr($T['intro'], 1) : h($T['intro']) ?></p>
    <div class="meta"><span>Демо-версия: <a href="<?= h($T['demo']) ?>" target="_blank" rel="noopener"><?= h(preg_replace('#^https?://#', '', $T['demo'])) ?></a></span><span>Пунктов: <?= $total ?>, вопросов: <?= count($T['questions']) ?></span><span>Черновик ответов сохраняется в этом браузере</span></div>
  </div>
  <?php if ($saved): ?><div class="ok" role="status">Ответы сохранены <?= h($Z['updated_at'] ?? crm_now()) ?>. Мы уже их видим и пришлём чистовую версию ТЗ. Дополнить можно здесь же по этой ссылке.</div><?php endif; ?>
  <?php if ($err): ?><div class="err" role="alert"><?= h($err) ?></div><?php endif; ?>
  <form method="post" id="f" novalidate>
    <input type="hidden" name="k" value="<?= h($key) ?>">
    <input type="hidden" name="_elapsed" id="el" value="0">
    <div style="position:absolute;left:-9999px" aria-hidden="true"><label>Не заполняйте <input name="_gotcha" tabindex="-1" autocomplete="off"></label></div>
    <div class="card who"><label for="who">Кто согласует — имя и должность</label><input type="text" id="who" name="who" value="<?= h($A['who'] ?? '') ?>" placeholder="Например: Иван Петров, технический директор" autocomplete="name"></div>
    <?php foreach ($T['sections'] as $s): ?>
    <section class="card sec"><h2><?= h($s['title']) ?></h2>
      <?php foreach ($s['points'] as $p): $id = $p['id']; $a = $A['pts'][$id] ?? ['v' => '', 'c' => '']; ?>
      <div class="pt" data-id="<?= h($id) ?>">
        <div class="t"><i><?= h($id) ?></i><p><?= h($p['text']) ?></p></div>
        <div class="ch" role="radiogroup" aria-label="Пункт <?= h($id) ?>">
          <label><input type="radio" name="v[<?= h($id) ?>]" value="ok"<?= $a['v'] === 'ok' ? ' checked' : '' ?>>Согласен</label>
          <label><input type="radio" name="v[<?= h($id) ?>]" value="change"<?= $a['v'] === 'change' ? ' checked' : '' ?>>Нужно иначе</label>
        </div>
        <div class="cm"<?= $a['v'] === 'change' || $a['c'] !== '' ? '' : ' hidden' ?>><textarea name="c[<?= h($id) ?>]" rows="2" aria-label="Как нужно — пункт <?= h($id) ?>" placeholder="Как нужно"><?= h($a['c']) ?></textarea></div>
      </div>
      <?php endforeach; ?>
    </section>
    <?php endforeach; ?>
    <section class="card sec"><h2>Вопросы к вам</h2><p class="foot">Без ответов на них мы не начнём работу. Если ответ пока неизвестен — так и напишите.</p>
      <?php foreach ($T['questions'] as $n => $q): ?>
      <div class="q"><label for="q-<?= h($q['id']) ?>"><?= $n + 1 ?>. <?= h($q['text']) ?></label><textarea id="q-<?= h($q['id']) ?>" name="q[<?= h($q['id']) ?>]" rows="2"><?= h($A['q'][$q['id']] ?? '') ?></textarea></div>
      <?php endforeach; ?>
    </section>
    <section class="card sec"><h2>Общий комментарий</h2><textarea name="general" rows="3" aria-label="Общий комментарий" placeholder="Что ещё важно учесть"><?= h($A['general'] ?? '') ?></textarea></section>
    <p class="foot noprint">Вопросы по документу — <a href="tel:+79290537603">+7 (929) 053-76-03</a>, студия «Форма сайта».</p>
    <div class="bar"><div class="in">
      <div class="cnt">Отмечено<b><span id="cnt">0</span> из <?= $total ?></b></div>
      <button class="btn btn--gh pr" type="button" onclick="print()">Печать</button>
      <button class="btn" type="submit" id="send"><?= empty($Z['answers']) ? 'Отправить' : 'Отправить правки' ?></button>
    </div></div>
  </form>
</main>
<script>
(function () {
  var f = document.getElementById('f'), t0 = Date.now(), store = 'tz:' + <?= json_encode($key) ?>, justSaved = <?= json_encode($saved) ?>;
  function grow(t) { t.style.height = 'auto'; t.style.height = Math.max(60, t.scrollHeight + 4) + 'px'; }
  function count() { document.getElementById('cnt').textContent = f.querySelectorAll('.ch input:checked').length; }
  function sync(pt) { var ch = pt.querySelector('input[value=change]').checked, cm = pt.querySelector('.cm'), ta = cm.querySelector('textarea'); if (ch || ta.value.trim()) { cm.hidden = false; grow(ta); } else cm.hidden = true; }
  function snap() { var o = {}; Array.prototype.forEach.call(f.elements, function (el) { if (!el.name || el.name[0] === '_' || el.name === 'k') return; if (el.type === 'radio') { if (el.checked) o[el.name] = el.value; } else if (el.value.trim()) o[el.name] = el.value; }); return o; }
  try {
    if (justSaved) localStorage.removeItem(store);
    else { var o = JSON.parse(localStorage.getItem(store) || 'null'); if (o) Array.prototype.forEach.call(f.elements, function (el) { var v = o[el.name]; if (v == null) return; if (el.type === 'radio') { if (!f.querySelector('[name="' + el.name + '"]:checked')) el.checked = el.value === v; } else if (!el.value.trim()) el.value = v; }); }
  } catch (e) {}
  f.querySelectorAll('.pt').forEach(sync); f.querySelectorAll('textarea').forEach(function (t) { if (!t.closest('.cm[hidden]')) grow(t); }); count();
  f.addEventListener('change', function (e) { var pt = e.target.closest('.pt'); if (pt) { sync(pt); if (e.target.value === 'change') pt.querySelector('.cm textarea').focus(); } count(); });
  f.addEventListener('input', function (e) { if (e.target.tagName === 'TEXTAREA') grow(e.target); try { localStorage.setItem(store, JSON.stringify(snap())); } catch (err) {} });
  f.addEventListener('change', function () { try { localStorage.setItem(store, JSON.stringify(snap())); } catch (err) {} });
  f.addEventListener('submit', function () { document.getElementById('el').value = Math.round((Date.now() - t0) / 1000); document.getElementById('send').disabled = true; });
  <?php if ($err): ?>document.querySelector('.err').scrollIntoView({ block: 'start' });<?php endif; ?>
})();
</script>
<?php endif; ?>
</body>
</html>
