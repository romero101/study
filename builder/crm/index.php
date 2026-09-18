<?php
require __DIR__ . '/lib.php';
crm_boot();

$err = ''; $ok = '';
$post = ($_SERVER['REQUEST_METHOD'] ?? '') === 'POST';
if ($post && isset($_POST['login'])) {
    $err = crm_login($_POST['u'] ?? '', $_POST['p'] ?? '');
    if ($err === '') { header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?')); exit; }
}
if ($post && isset($_POST['logout']) && crm_csrf_ok($_POST['csrf'] ?? '')) {
    $_SESSION = []; session_destroy(); header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?')); exit;
}
if ($post && isset($_POST['newpass']) && crm_logged_in()) {
    $err = crm_csrf_ok($_POST['csrf'] ?? '')
        ? crm_change_password($_POST['cur'] ?? '', $_POST['p1'] ?? '', $_POST['p2'] ?? '')
        : 'Сессия устарела, обновите страницу';
    if ($err === '') { header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?') . '?changed=1'); exit; }
}
$passScreen = crm_logged_in() && (crm_must_change() || isset($_GET['password']) || ($post && isset($_POST['newpass'])));
if (isset($_GET['changed'])) $ok = 'Пароль изменён';
$locked = crm_logged_in() ? 0 : crm_locked_for();

$data = crm_read();
?><!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title><?= h(CRM_TITLE) ?></title>
<style>
*,*::before,*::after{box-sizing:border-box}
body{margin:0;font:400 15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;
color:#16202b;background:#eef2f6}
h1,h2,h3{margin:0 0 .4em;line-height:1.2;letter-spacing:-.02em}
a{color:#1c4d85}
button,input,select,textarea{font:inherit;color:inherit}
:focus-visible{outline:3px solid #2f6fb5;outline-offset:2px;border-radius:4px}

/* ---------- вход ---------- */
.login{min-height:100vh;display:grid;place-items:center;padding:20px}
.login form{background:#fff;padding:32px;border-radius:16px;box-shadow:0 12px 40px rgba(16,32,48,.12);
width:100%;max-width:380px}
.login h1{font-size:23px}
.login p{color:#6a7686;font-size:14px;margin:0 0 22px}
.f{margin-bottom:14px}
.f label{display:block;font-weight:700;font-size:14px;margin-bottom:6px}
.f input,.f select,.f textarea{width:100%;min-height:46px;padding:11px 13px;border:2px solid #d9e2ec;
border-radius:10px;background:#fff}
.f textarea{min-height:90px;resize:vertical}
.f input:focus,.f select:focus,.f textarea:focus{outline:none;border-color:#2f6fb5}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:46px;padding:11px 20px;
border-radius:10px;font-weight:700;border:2px solid transparent;cursor:pointer;background:#2f6fb5;color:#fff;
text-decoration:none}
.btn:hover{background:#245a96}
.btn--w{width:100%}
.btn--gh{background:#fff;color:#1c4d85;border-color:#d9e2ec}
.btn--gh:hover{background:#f4f8fb}
.btn--sm{min-height:38px;padding:8px 14px;font-size:14px}
.err{background:#fff1f0;border:1px solid #f0b3ac;color:#9e2114;padding:11px 14px;border-radius:10px;
margin-bottom:16px;font-weight:600;font-size:14px}

.login h1+p{line-height:1.45}
.f label small{font-weight:400;color:#6a7686}
.pw{position:relative}.pw input{padding-right:92px}
.eye{position:absolute;right:6px;top:6px;bottom:6px;border:0;background:#eef3f8;border-radius:7px;padding:0 10px;
font-size:13px;cursor:pointer;color:#41586e}
.back{text-align:center;margin:18px 0 0!important;font-size:14px}
.out{display:inline}.out button{background:none;border:0;color:#cdd8e3;cursor:pointer;text-decoration:underline;padding:0;min-height:32px}
.warn--ok{background:#e9f6ee;border-color:#b5dcc3;color:#174d2c}
.src{display:inline-block;margin-left:6px;background:#fff0d6;color:#8a5a00;border-radius:99px;padding:1px 8px;font-size:11.5px;font-weight:700}

/* ---------- скрипт звонка ---------- */
.script{margin:18px 0;border:2px solid #d6e3f3;border-radius:14px;background:#f6faff}
.script>summary{cursor:pointer;padding:14px 18px;list-style:none;display:flex;gap:12px;align-items:baseline;flex-wrap:wrap;min-height:48px}
.script>summary::-webkit-details-marker{display:none}
.script>summary:before{content:"▸";color:#2f6fb5}
.script[open]>summary:before{content:"▾"}
.script>summary span{font-size:13.5px;color:#41586e;flex:1;min-width:220px}
#d-script{padding:0 18px 18px}
.sc h4{margin:20px 0 8px;font-size:12.5px;text-transform:uppercase;letter-spacing:.06em;color:#2f6fb5}
.sc p,.sc li{font-size:14.5px;line-height:1.55;margin:0 0 6px}
.sc ul{margin:0;padding-left:20px}
.sc .say{white-space:pre-wrap;background:#fff;border:1px solid #dde6ee;border-left:4px solid #2f6fb5;border-radius:8px;padding:12px 14px;font-size:14.5px;line-height:1.6}
.sc .warn2{background:#fff6e0;border:1px solid #f0d79b;color:#6b4c07;border-radius:8px;padding:10px 13px;font-size:14px}
.sc details{background:#fff;border:1px solid #dde6ee;border-radius:8px;margin-bottom:6px}
.sc details summary{cursor:pointer;padding:11px 14px;font-weight:700;font-size:14.5px;min-height:44px}
.sc details .say{border:0;border-top:1px solid #eef2f6;border-radius:0 0 8px 8px;border-left:0}
.sc details.own summary{color:#7a4a00}

/* ---------- каркас ---------- */
.top{background:#16202b;color:#fff;padding:12px 0}
.top .in{max-width:1500px;margin:0 auto;padding:0 18px;display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.top b{font-size:17px;letter-spacing:-.02em}
.top .sp{margin-left:auto;display:flex;align-items:center;gap:14px;font-size:14px;color:#9aa8b6}
.top a{color:#cdd8e3}
.warn{background:#fff6e0;border-bottom:1px solid #f0d79b;color:#6b4c07;font-size:13.5px;padding:9px 18px;text-align:center}
.wrap{max-width:1500px;margin:0 auto;padding:18px}

/* ---------- воронка ---------- */
.funnel{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:18px}
.fst{background:#fff;border:2px solid #e4ebf1;border-radius:12px;padding:12px 14px;cursor:pointer;text-align:left}
.fst:hover{border-color:#c3d3e0}
.fst[aria-pressed=true]{border-color:#2f6fb5;background:#eaf2fb}
.fst i{display:block;font-style:normal;font-size:12.5px;color:#6a7686;margin-bottom:5px;line-height:1.3}
.fst b{font-size:22px;letter-spacing:-.02em}
.fst s{display:block;text-decoration:none;font-size:12.5px;color:#6a7686;margin-top:2px}

/* ---------- таблица ---------- */
.tools{display:flex;gap:10px;margin-bottom:12px;flex-wrap:wrap;align-items:center}
.tools input[type=search]{min-height:44px;padding:10px 14px;border:2px solid #d9e2ec;border-radius:10px;
min-width:260px;flex:1;background:#fff}
.tbl{background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 2px 12px rgba(16,32,48,.06)}
.tbl-scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:900px}
th,td{text-align:left;padding:11px 14px;border-bottom:1px solid #eef2f6;vertical-align:top;font-size:14.5px}
th{background:#f7fafc;font-size:12.5px;text-transform:uppercase;letter-spacing:.05em;color:#6a7686;
position:sticky;top:0;z-index:1}
tbody tr{cursor:pointer}
tbody tr:hover{background:#f7fafc}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.co{font-weight:700}
.co s{display:block;text-decoration:none;font-weight:400;color:#6a7686;font-size:13px}
.pill{display:inline-block;padding:4px 10px;border-radius:99px;font-size:12.5px;font-weight:700;white-space:nowrap}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:1px}
.mini{color:#6a7686;font-size:13px}
.ps{font-weight:700}
.ps--bad{color:#c02b1d}.ps--mid{color:#b06a08}.ps--ok{color:#166534}
.empty{padding:40px 18px;text-align:center;color:#6a7686}

/* ---------- карточка сделки ---------- */
dialog{border:0;border-radius:16px;padding:0;width:min(980px,96vw);max-height:92vh;
box-shadow:0 24px 70px rgba(8,16,24,.36)}
dialog::backdrop{background:rgba(12,20,30,.55)}
.dlg{display:flex;flex-direction:column;max-height:92vh}
.dlg__h{padding:18px 22px;border-bottom:1px solid #eef2f6;display:flex;align-items:flex-start;gap:14px}
.dlg__h h2{font-size:20px;margin:0}
.dlg__h .mini{margin-top:3px}
.x{margin-left:auto;background:none;border:0;font-size:26px;line-height:1;cursor:pointer;color:#6a7686;
min-width:44px;min-height:44px}
.dlg__b{padding:20px 22px;overflow:auto}
.ba{display:grid;gap:16px}
@media (min-width:820px){.ba{grid-template-columns:1fr 1fr}}
.col{background:#f7fafc;border:1px solid #e4ebf1;border-radius:12px;padding:16px}
.col--now{background:#f1f8f3;border-color:#c8e6d2}
.col h3{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:#6a7686;margin-bottom:12px}
.row{margin-bottom:13px}
.row:last-child{margin-bottom:0}
.row em{display:block;font-style:normal;font-size:12.5px;color:#6a7686;margin-bottom:4px}
.ed{width:100%;border:1px solid transparent;border-radius:8px;padding:7px 9px;background:transparent;
resize:vertical;min-height:38px;font-size:14.5px;line-height:1.45}
.ed:hover{border-color:#d9e2ec;background:#fff}
.ed:focus{outline:none;border-color:#2f6fb5;background:#fff}
.saved{color:#166534;font-size:12.5px;font-weight:700;opacity:0;transition:opacity .2s}
.saved.on{opacity:1}
.stagebar{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:18px 0}
.stagebar select{min-height:46px;padding:10px 12px;border:2px solid #d9e2ec;border-radius:10px;background:#fff;
font-weight:700;min-width:220px}
.log{margin-top:8px;border-top:1px solid #eef2f6;padding-top:16px}
.log h3{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:#6a7686}
.note{display:flex;gap:11px;padding:11px 0;border-bottom:1px solid #f2f6f9}
.note:last-child{border:0}
.note .av{flex:0 0 auto;width:30px;height:30px;border-radius:50%;background:#dfe8f0;display:grid;place-items:center;
font-size:12px;font-weight:800;color:#41586e}
.note--stage .av{background:#e4eefb;color:#1c4d85}
.note .tx{flex:1;min-width:0}
.note .tx b{font-size:13.5px}
.note .tx s{text-decoration:none;color:#8a96a3;font-size:12.5px;margin-left:7px}
.note .tx p{margin:2px 0 0;white-space:pre-wrap;word-break:break-word}
.dlg__f{padding:16px 22px;border-top:1px solid #eef2f6;background:#fafcfd}
.dlg__f textarea{width:100%;min-height:74px;padding:11px 13px;border:2px solid #d9e2ec;border-radius:10px;
resize:vertical;background:#fff}
.quick{display:flex;gap:7px;flex-wrap:wrap;margin:9px 0}
.quick button{background:#eef3f8;border:1px solid #dde6ee;border-radius:99px;padding:6px 12px;font-size:13px;
cursor:pointer;min-height:34px}
.quick button:hover{background:#e2ebf4}
@media (max-width:640px){
  table{min-width:700px}
  .dlg__h,.dlg__b,.dlg__f{padding-inline:15px}
  /* на телефоне карточка листается целиком: закреплённый низ с комментарием съедал весь экран */
  dialog{width:100vw;max-width:100vw;max-height:100dvh;height:100dvh;border-radius:0;margin:0}
  .dlg{max-height:none;height:100dvh;overflow:auto;display:block}
  .dlg__h{position:sticky;top:0;background:#fff;z-index:2}
  .dlg__b{overflow:visible}
  .quick{flex-wrap:nowrap;overflow-x:auto;padding-bottom:6px;-webkit-overflow-scrolling:touch}
  .quick button{white-space:nowrap;flex:0 0 auto;min-height:40px}
  .script>summary span{min-width:0;flex-basis:100%}
}
</style>
</head>
<body>
<?php if (!crm_logged_in()): ?>
<div class="login">
  <form method="post" autocomplete="on">
    <h1>Форма сайта</h1>
    <p>Воронка продаж. Вход для сотрудников студии.</p>
    <?php if ($err): ?><div class="err" role="alert"><?= h($err) ?></div><?php endif; ?>
    <?php if ($locked && !$err): ?><div class="err" role="alert">Слишком много попыток. Вход закрыт ещё на <?= $locked ?> мин.</div><?php endif; ?>
    <div class="f"><label for="u">Логин</label>
      <input id="u" name="u" autocomplete="username" autocapitalize="none" autofocus required></div>
    <div class="f"><label for="p">Пароль</label>
      <div class="pw"><input id="p" name="p" type="password" autocomplete="current-password" required>
      <button type="button" class="eye" data-eye="p" aria-label="Показать пароль">показать</button></div></div>
    <button class="btn btn--w" type="submit" name="login" value="1">Войти</button>
    <p class="back"><a href="../">← На сайт студии</a></p>
  </form>
</div>
<?php elseif ($passScreen): ?>
<div class="login">
  <form method="post">
    <h1><?= crm_must_change() ? 'Задайте свой пароль' : 'Смена пароля' ?></h1>
    <p><?= crm_must_change() ? 'Вы вошли со стартовым паролем. Пока он не сменён, воронка закрыта: в ней контакты клиентов.' : 'После смены вход на других устройствах останется активным до выхода.' ?></p>
    <?php if ($err): ?><div class="err" role="alert"><?= h($err) ?></div><?php endif; ?>
    <input type="hidden" name="csrf" value="<?= h(crm_csrf()) ?>">
    <div class="f"><label for="cur">Текущий пароль</label>
      <input id="cur" name="cur" type="password" autocomplete="current-password" required autofocus></div>
    <div class="f"><label for="p1">Новый пароль <small>не короче <?= CRM_MIN_PASS ?> символов</small></label>
      <div class="pw"><input id="p1" name="p1" type="password" autocomplete="new-password" minlength="<?= CRM_MIN_PASS ?>" required>
      <button type="button" class="eye" data-eye="p1" aria-label="Показать пароль">показать</button></div></div>
    <div class="f"><label for="p2">Новый пароль ещё раз</label>
      <input id="p2" name="p2" type="password" autocomplete="new-password" minlength="<?= CRM_MIN_PASS ?>" required></div>
    <button class="btn btn--w" type="submit" name="newpass" value="1">Сохранить пароль</button>
    <?php if (!crm_must_change()): ?><p class="back"><a href="./">← Назад в воронку</a></p><?php endif; ?>
  </form>
</div>
<?php else: ?>

<div class="top"><div class="in">
  <b><?= h(CRM_TITLE) ?></b>
  <span class="sp">
    <span><?= h($_SESSION['crm_name'] ?? '') ?></span>
    <a href="?password=1">Сменить пароль</a>
    <form method="post" class="out"><input type="hidden" name="csrf" value="<?= h(crm_csrf()) ?>">
      <button type="submit" name="logout" value="1">Выйти</button></form>
  </span>
</div></div>
<?php if ($ok): ?><div class="warn warn--ok"><?= h($ok) ?></div><?php endif; ?>

<div class="wrap">
  <div class="funnel" id="funnel"></div>
  <div class="tools">
    <input type="search" id="q" placeholder="Поиск: компания, город, контакт, комментарий" aria-label="Поиск">
    <button class="btn btn--gh btn--sm" id="add">+ Сделка</button>
  </div>
  <div class="tbl"><div class="tbl-scroll">
    <table>
      <thead><tr>
        <th>№</th><th>Компания</th><th>Этап</th><th>Было</th><th>Стало</th>
        <th>PageSpeed</th><th>Предложение</th><th>Последнее</th>
      </tr></thead>
      <tbody id="rows"></tbody>
    </table>
  </div><div class="empty" id="empty" hidden>Ничего не найдено</div></div>
</div>

<dialog id="dlg"><div class="dlg">
  <div class="dlg__h">
    <div><h2 id="d-co"></h2><div class="mini" id="d-city"></div></div>
    <button class="x" id="d-x" aria-label="Закрыть">&times;</button>
  </div>
  <div class="dlg__b">
    <div class="stagebar">
      <label for="d-stage"><b>Этап сделки</b></label>
      <select id="d-stage"></select>
      <span class="saved" id="d-saved">сохранено</span>
    </div>
    <div class="ba">
      <div class="col">
        <h3>Было</h3>
        <div class="row"><em>Адрес сайта</em><textarea class="ed" data-f="was_url" rows="1"></textarea></div>
        <div class="row"><em>Что не так</em><textarea class="ed" data-f="was_problems" rows="4"></textarea></div>
        <div class="row"><em>Источник замера</em><textarea class="ed" data-f="measure_src" rows="2"></textarea></div>
      </div>
      <div class="col col--now">
        <h3>Стало</h3>
        <div class="row"><em>Адрес демо</em><textarea class="ed" data-f="now_url" rows="1"></textarea></div>
        <div class="row"><em>Что сделали / план</em><textarea class="ed" data-f="now_done" rows="4"></textarea></div>
        <div class="row"><em>Что осталось</em><textarea class="ed" data-f="left_todo" rows="2"></textarea></div>
      </div>
      <div class="col">
        <h3>Контакты</h3>
        <div class="row"><textarea class="ed" data-f="contacts" rows="3"></textarea></div>
        <div class="row"><em>Город</em><textarea class="ed" data-f="city" rows="1"></textarea></div>
      </div>
      <div class="col">
        <h3>Деньги</h3>
        <div class="row"><em>Предложение, ₽</em><textarea class="ed" data-f="offer" rows="1"></textarea></div>
        <div class="row"><em>Компания</em><textarea class="ed" data-f="company" rows="1"></textarea></div>
      </div>
    </div>
    <details class="script" id="d-script-box">
      <summary><b>Скрипт звонка</b><span id="d-script-goal"></span></summary>
      <div id="d-script"></div>
    </details>
    <div class="log">
      <h3>История</h3>
      <div id="d-log"></div>
    </div>
  </div>
  <div class="dlg__f">
    <div class="quick" id="d-quick"></div>
    <textarea id="d-note" placeholder="Комментарий: о чём договорились, что обещали, когда перезвонить"></textarea>
    <div style="margin-top:10px"><button class="btn" id="d-send">Добавить комментарий</button></div>
  </div>
</div></dialog>

<script>
const DATA = <?= json_encode($data, JSON_UNESCAPED_UNICODE) ?>;
const CSRF = <?= json_encode(crm_csrf()) ?>;
const SCRIPTS = <?= json_encode(require __DIR__ . '/scripts.php', JSON_UNESCAPED_UNICODE) ?>;
</script>
<script src="app.js" defer></script>
<?php endif; ?>
<script>
document.querySelectorAll('[data-eye]').forEach(function (b) {
  b.addEventListener('click', function () {
    var i = document.getElementById(b.dataset.eye), show = i.type === 'password';
    i.type = show ? 'text' : 'password'; b.textContent = show ? 'скрыть' : 'показать';
  });
});
</script>
</body>
</html>
