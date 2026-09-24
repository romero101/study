<?php
/* Анкета клиента на запуск сайта и рекламы. Открывается по личной ссылке /anketa/?k=<ключ>,
   ключ лежит в сделке (brief.key) и создаётся из карточки в админке. Ответы пишутся прямо
   в сделку (brief.answers) и появляются в её истории. Логина у клиента нет и не нужно. */
require __DIR__ . '/../admin/lib.php';
$Q = require __DIR__ . '/../admin/questions.php';
header('X-Content-Type-Options: nosniff');
header('X-Frame-Options: DENY');
header('Referrer-Policy: no-referrer');
header('Cache-Control: no-store');

$key  = (string)($_POST['k'] ?? $_GET['k'] ?? '');
$data = crm_read();
$idx  = -1;
if (preg_match('/^[a-f0-9]{16,40}$/', $key)) {
    foreach ($data['leads'] as $i => $l) {
        if (!empty($l['brief']['key']) && hash_equals((string)$l['brief']['key'], $key)) { $idx = $i; break; }
    }
}
$total = 0; $keys = [];
foreach ($Q as $s) foreach ($s['q'] as $q) { $total++; $keys[$q['k']] = $q; }

$err = ''; $saved = false; $posted = [];
if ($idx >= 0 && ($_SERVER['REQUEST_METHOD'] ?? '') === 'POST') {
    $B = $data['leads'][$idx]['brief'];
    $a = is_array($_POST['a'] ?? null) ? $_POST['a'] : [];
    foreach ($keys as $k => $q) {
        $v = $a[$k] ?? '';
        if (is_array($v)) $v = implode('; ', array_map('strval', $v));
        $v = trim(preg_replace('/\r\n?/', "\n", strip_tags((string)$v)));
        if (in_array($q['type'], ['radio', 'check'], true) && $v !== '') {
            $ok = true;
            foreach (explode('; ', $v) as $part) if (!in_array($part, $q['options'], true)) $ok = false;
            if (!$ok) $v = '';
        }
        $posted[$k] = mb_substr($v, 0, 4000);
    }
    $missing = [];
    foreach ($keys as $k => $q) if (!empty($q['req']) && $posted[$k] === '') $missing[] = $q['label'];
    if (!empty($_POST['_gotcha']) || (isset($_POST['_elapsed']) && (int)$_POST['_elapsed'] < 3)) {
        $saved = true;                                   // боту отвечаем «сохранено», ничего не пишем
    } elseif ($missing) {
        $err = 'Осталось заполнить: ' . implode(', ', array_map(function ($m) { return '«' . $m . '»'; }, $missing)) . '.';
    } elseif (!empty($B['updated_ts']) && time() - (int)$B['updated_ts'] < 5) {
        $err = 'Слишком часто. Подождите пару секунд и нажмите «Отправить» ещё раз.';
    } else {
        $answers = array_filter($posted, function ($v) { return $v !== ''; });
        $n = count($answers);
        $first = empty($B['answers']);
        if (!$first) {
            $B['history'] = array_slice(array_merge($B['history'] ?? [], [['at' => $B['updated_at'] ?? '', 'answers' => $B['answers']]]), -5);
        }
        $B['answers'] = $answers;
        $B['count'] = $n; $B['total'] = $total;
        if ($first) $B['sent_at'] = crm_now();
        $B['updated_at'] = crm_now(); $B['updated_ts'] = time();
        $B['ip'] = $_SERVER['REMOTE_ADDR'] ?? '';
        $data['leads'][$idx]['brief'] = $B;
        $data['leads'][$idx]['updated'] = crm_now();
        $who = mb_substr($answers['filled_by'] ?? 'клиент', 0, 60);
        $data['leads'][$idx]['comments'][] = ['at' => crm_now(), 'who' => $who, 'kind' => 'brief',
            'text' => 'Анкета на запуск ' . ($first ? 'заполнена' : 'обновлена') . ': ' . $n . ' из ' . $total .
                      ' ответов. Ответы — в блоке «Анкета» этой карточки.'];
        if (!crm_write($data)) $err = 'Не удалось сохранить ответы. Попробуйте ещё раз через минуту; черновик остаётся в этом браузере.';
        else $saved = true;
    }
}
$lead  = $idx >= 0 ? $data['leads'][$idx] : null;
if (!$lead) http_response_code(404);
$B     = $lead['brief'] ?? [];
$vals  = $err ? $posted : ($B['answers'] ?? []);
$hints = $B['hints'] ?? [];
$name  = trim((string)($B['name'] ?? ''));
?><!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title><?= $lead ? 'Анкета на запуск — ' . h($lead['company']) : 'Анкета' ?></title>
<meta name="theme-color" content="#172333">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<style>
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;font:400 17px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;color:#16202b;background:#eef2f6}
a{color:#2b46d6}
h1,h2{margin:0 0 .35em;line-height:1.2;letter-spacing:-.02em}
h1{font-size:clamp(26px,5.5vw,36px)}
h2{font-size:21px}
p{margin:0 0 12px}
button,input,select,textarea{font:inherit;color:inherit}
:focus-visible{outline:3px solid #4558ed;outline-offset:2px;border-radius:6px}
.top{background:#172333;color:#fff}
.top .in{max-width:760px;margin:0 auto;padding:12px 16px;display:flex;align-items:center;gap:12px}
.top svg{width:34px;height:34px;flex:0 0 auto}
.top b{font-size:17px;letter-spacing:-.02em}
.top a{margin-left:auto;color:#cdd8e3;text-decoration:none;font-size:15px;white-space:nowrap}
.wrap{max-width:760px;margin:0 auto;padding:22px 16px 120px}
.lead{background:#fff;border-radius:16px;padding:22px 20px;box-shadow:0 2px 12px rgba(16,32,48,.06);margin-bottom:16px}
.lead p{color:#41586e;font-size:16px}
.lead p:last-child{margin:0}
.ok,.err{border-radius:12px;padding:14px 16px;margin-bottom:16px;font-weight:600;font-size:16px}
.ok{background:#e9f6ee;border:1px solid #b5dcc3;color:#174d2c}
.err{background:#fff1f0;border:1px solid #f0b3ac;color:#9e2114}
.sec{background:#fff;border-radius:16px;padding:20px 20px 8px;box-shadow:0 2px 12px rgba(16,32,48,.06);margin-bottom:16px}
.sec>header{margin-bottom:14px}
.sec>header small{display:block;color:#6a7686;font-size:14px;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px}
.sec>header p{color:#41586e;font-size:15px;margin:6px 0 0}
.q{padding:14px 0 16px;border-top:1px solid #eef2f6}
.q label.l,.q .l{display:block;font-weight:700;font-size:16.5px;line-height:1.35;margin-bottom:6px}
.q .l i{font-style:normal;color:#8a96a3;font-weight:600;margin-right:6px}
.q .l em{font-style:normal;color:#c02b1d}
.q .hint{color:#6a7686;font-size:14.5px;line-height:1.45;margin:0 0 10px}
.q .hint.own{color:#5a4300;background:#fff6e0;border-left:3px solid #e6b422;padding:8px 10px;border-radius:0 8px 8px 0}
.q input[type=text],.q input[type=email],.q input[type=tel],.q textarea{width:100%;min-height:48px;padding:11px 13px;border:2px solid #d9e2ec;border-radius:10px;background:#fff;font-size:17px}
.q textarea{min-height:64px;resize:none;overflow:hidden;line-height:1.45}
.q input:focus,.q textarea:focus{outline:none;border-color:#4558ed;box-shadow:0 0 0 3px rgba(69,88,237,.15)}
.opts{display:flex;flex-wrap:wrap;gap:8px}
.opts label{position:relative;display:inline-flex;align-items:center;min-height:44px;padding:9px 14px;border:2px solid #d9e2ec;border-radius:99px;cursor:pointer;font-size:15.5px;background:#fff}
.opts input{position:absolute;opacity:0;inset:0;width:100%;height:100%;margin:0;cursor:pointer}
.opts label:has(input:checked){border-color:#4558ed;background:#eef1ff;font-weight:700}
.opts label:has(input:focus-visible){outline:3px solid #4558ed;outline-offset:2px}
.bar{position:fixed;left:0;right:0;bottom:0;background:#fff;border-top:1px solid #dde6ee;padding:10px 16px calc(10px + env(safe-area-inset-bottom));z-index:5}
.bar .in{max-width:760px;margin:0 auto;display:flex;align-items:center;gap:14px}
.bar .cnt{font-size:14.5px;color:#41586e;line-height:1.3}
.bar .cnt b{display:block;font-size:16px;color:#16202b}
.btn{margin-left:auto;display:inline-flex;align-items:center;justify-content:center;min-height:50px;padding:12px 22px;border-radius:12px;font-weight:700;border:0;cursor:pointer;background:#4558ed;color:#fff;font-size:17px;white-space:nowrap}
.btn:hover{background:#3547d1}
.btn[disabled]{opacity:.6;cursor:progress}
.foot{color:#6a7686;font-size:14px;margin-top:18px}
.foot a{color:#41586e}
.none{min-height:70vh;display:grid;place-items:center;padding:20px}
.none div{background:#fff;padding:32px;border-radius:16px;max-width:420px;box-shadow:0 12px 40px rgba(16,32,48,.12)}
@media (min-width:640px){.sec{padding:24px 26px 10px}.lead{padding:26px}}
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
  <p>Анкета открывается только по личной ссылке из письма или сообщения менеджера. Если ссылка не открывается — напишите нам, пришлём новую.</p>
  <p><a href="tel:+79290537603">+7 (929) 053-76-03</a></p>
</div></div>
<?php else:
$done = 0; foreach ($keys as $k => $q) if (($vals[$k] ?? '') !== '') $done++;
?>
<main class="wrap">
  <div class="lead">
    <h1>Анкета на запуск<br><span style="color:#4558ed"><?= h($lead['company']) ?></span></h1>
    <p><?= $name ? h($name) . ', з' : 'З' ?>десь всё, что нужно нам от вас, чтобы собрать сайт и запустить рекламу без задержек. Это минут пятнадцать. Можно заполнять частями: черновик сохраняется в этом браузере, а после отправки ответы можно дополнить по той же ссылке.</p>
    <p>Файлы сюда прикладывать не нужно — фото и логотип пришлите ссылкой на папку или менеджеру в Telegram. Пароли не пишите нигде: доступы выдаются из ваших кабинетов.</p>
  </div>
  <?php if ($saved): ?><div class="ok" role="status">Ответы сохранены <?= h($B['updated_at'] ?? crm_now()) ?>. Менеджер их уже видит. Если что-то вспомните — дополните здесь же и отправьте снова.</div><?php endif; ?>
  <?php if ($err): ?><div class="err" role="alert"><?= h($err) ?></div><?php endif; ?>
  <form method="post" id="f" novalidate>
    <input type="hidden" name="k" value="<?= h($key) ?>">
    <input type="hidden" name="_elapsed" id="el" value="0">
    <div style="position:absolute;left:-9999px" aria-hidden="true"><label>Не заполняйте <input name="_gotcha" tabindex="-1" autocomplete="off"></label></div>
    <?php $n = 0; foreach ($Q as $si => $s): ?>
    <section class="sec" id="s-<?= h($s['id']) ?>">
      <header><small>Раздел <?= $si + 1 ?> из <?= count($Q) ?></small><h2><?= h($s['title']) ?></h2>
        <?php if (!empty($s['intro'])): ?><p><?= h($s['intro']) ?></p><?php endif; ?></header>
      <?php foreach ($s['q'] as $q): $n++; $k = $q['k']; $v = $vals[$k] ?? ''; $id = 'q-' . $k;
            $hint = $hints[$k] ?? ($q['hint'] ?? ''); $own = isset($hints[$k]); ?>
      <div class="q" data-k="<?= h($k) ?>">
        <?php if (in_array($q['type'], ['radio', 'check'], true)): ?>
          <div class="l" id="<?= $id ?>-l"><i><?= $n ?>.</i><?= h($q['label']) ?><?= !empty($q['req']) ? ' <em>*</em>' : '' ?></div>
          <?php if ($hint): ?><p class="hint<?= $own ? ' own' : '' ?>"><?= h($hint) ?></p><?php endif; ?>
          <div class="opts" role="group" aria-labelledby="<?= $id ?>-l">
            <?php $chosen = $q['type'] === 'check' ? explode('; ', $v) : [$v];
                  foreach ($q['options'] as $o): ?>
            <label><input type="<?= $q['type'] === 'check' ? 'checkbox' : 'radio' ?>" name="a[<?= h($k) ?>]<?= $q['type'] === 'check' ? '[]' : '' ?>" value="<?= h($o) ?>"<?= in_array($o, $chosen, true) ? ' checked' : '' ?>><?= h($o) ?></label>
            <?php endforeach; ?>
          </div>
        <?php else: ?>
          <label class="l" for="<?= $id ?>"><i><?= $n ?>.</i><?= h($q['label']) ?><?= !empty($q['req']) ? ' <em>*</em>' : '' ?></label>
          <?php if ($hint): ?><p class="hint<?= $own ? ' own' : '' ?>"><?= h($hint) ?></p><?php endif; ?>
          <?php if ($q['type'] === 'textarea'): ?>
            <textarea id="<?= $id ?>" name="a[<?= h($k) ?>]" rows="2"><?= h($v) ?></textarea>
          <?php else: ?>
            <input id="<?= $id ?>" type="<?= $q['type'] === 'email' ? 'email' : 'text' ?>" name="a[<?= h($k) ?>]" value="<?= h($v) ?>"<?= $q['type'] === 'email' ? ' autocomplete="email" inputmode="email"' : '' ?>>
          <?php endif; ?>
        <?php endif; ?>
      </div>
      <?php endforeach; ?>
    </section>
    <?php endforeach; ?>
    <p class="foot">Звёздочкой отмечены три ответа, без которых мы не начнём. Остальное можно дослать позже. Вопросы по анкете — <a href="tel:+79290537603">+7 (929) 053-76-03</a>, студия «Форма сайта».</p>
    <div class="bar"><div class="in">
      <div class="cnt">Отвечено<b><span id="cnt"><?= $done ?></span> из <?= $total ?></b></div>
      <button class="btn" type="submit" id="send"><?= empty($B['answers']) ? 'Отправить ответы' : 'Отправить дополнения' ?></button>
    </div></div>
  </form>
</main>
<script>
(function () {
  var f = document.getElementById('f'), cnt = document.getElementById('cnt'), t0 = Date.now();
  var store = 'anketa:' + <?= json_encode($key) ?>, saved = <?= json_encode(!empty($B['answers'])) ?>, justSaved = <?= json_encode($saved) ?>;
  function fields() { return Array.prototype.slice.call(f.querySelectorAll('[name^="a["]')); }
  function grow(t) { t.style.height = 'auto'; t.style.height = Math.max(64, t.scrollHeight + 4) + 'px'; }
  function answered() {
    var seen = {}, n = 0;
    fields().forEach(function (el) {
      var k = el.closest('.q').dataset.k; if (seen[k]) return;
      var v = (el.type === 'radio' || el.type === 'checkbox') ? !!f.querySelector('[name="' + el.name + '"]:checked') : el.value.trim() !== '';
      if (v) { seen[k] = 1; n++; }
    });
    cnt.textContent = n;
  }
  function snapshot() {
    var o = {};
    fields().forEach(function (el) {
      if (el.type === 'radio') { if (el.checked) o[el.name] = el.value; }
      else if (el.type === 'checkbox') { if (el.checked) (o[el.name] = o[el.name] || []).push(el.value); }
      else if (el.value.trim() !== '') o[el.name] = el.value;
    });
    return o;
  }
  function restore() {
    try {
      if (justSaved) { localStorage.removeItem(store); return; }
      var o = JSON.parse(localStorage.getItem(store) || 'null'); if (!o) return;
      fields().forEach(function (el) {
        var v = o[el.name]; if (v == null) return;
        if (el.type === 'radio') el.checked = el.value === v;
        else if (el.type === 'checkbox') el.checked = v.indexOf(el.value) > -1;
        else if (el.value.trim() === '') el.value = v;   // ответы с сервера главнее черновика
      });
    } catch (e) {}
  }
  restore();
  f.querySelectorAll('textarea').forEach(grow);
  answered();
  f.addEventListener('input', function (e) {
    if (e.target.tagName === 'TEXTAREA') grow(e.target);
    answered();
    try { localStorage.setItem(store, JSON.stringify(snapshot())); } catch (err) {}
  });
  f.addEventListener('change', answered);
  f.addEventListener('submit', function () {
    document.getElementById('el').value = Math.round((Date.now() - t0) / 1000);
    document.getElementById('send').disabled = true;
  });
  <?php if ($err): ?>var bad = document.querySelector('.err'); if (bad) bad.scrollIntoView({ block: 'start' });<?php endif; ?>
})();
</script>
<?php endif; ?>
</body>
</html>
