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
$docs = crm_docs()['docs'];
$company = crm_company();
?><!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title><?= h(CRM_TITLE) ?></title>
<style>
*,*::before,*::after{box-sizing:border-box}
[hidden]{display:none!important}
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

.ed--lpr{background:#fff8e6;border-color:#f0d79b;font-weight:600}

/* ---------- скорость: было / стало ---------- */
.speed{margin:18px 0 0;border:2px solid #d9ead9;border-radius:14px;background:#f5fbf5;padding:14px 18px}
.speed h3{font-size:15px;margin:0 0 10px}
.speed table{min-width:0;width:100%;border-collapse:collapse}
.speed th,.speed td{padding:7px 8px;font-size:14px;border-bottom:1px solid #e3efe3;background:none;position:static;text-transform:none;letter-spacing:0}
.speed th{color:#6a7686;font-size:12.5px;font-weight:600}
.speed td:nth-child(n+2),.speed th:nth-child(n+2){text-align:right;white-space:nowrap}
.speed .bad{color:#b3261e;font-weight:700}.speed .ok{color:#1d7a3a;font-weight:700}
.speed .x{color:#1d7a3a;font-weight:800}
.speed th.sub{text-align:left!important;color:#2b3a4a;font-size:13px;padding-top:14px}
.speed p{font-size:12.5px;color:#6a7686;margin:10px 0 0}

/* ---------- анкета на запуск ---------- */
.brief{margin:18px 0 0;border:2px solid #e3dbf3;border-radius:14px;background:#faf8ff;padding:14px 18px}
.brief h3{font-size:15px;margin:0 0 8px}
.brief h4{margin:14px 0 6px;font-size:12.5px;text-transform:uppercase;letter-spacing:.06em;color:#6b4fb3}
.brief dl{margin:0;display:grid;grid-template-columns:minmax(150px,1fr) 2fr;gap:6px 14px;font-size:14px}
.brief dt{color:#6a7686}
.brief dd{margin:0;white-space:pre-wrap;word-break:break-word}
.b-link{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:6px}
.b-link a{word-break:break-all;font-size:14px}
.brief details{margin-top:10px;font-size:13.5px;color:#6a7686}
.brief details summary{cursor:pointer}
.brief ul{margin:6px 0 0;padding-left:18px}
.note--brief .av{background:#e2f3e8;color:#1d7a3a}
@media (max-width:640px){.brief dl{grid-template-columns:1fr;gap:2px}.brief dd{margin-bottom:8px}}

/* ---------- бухгалтерия ---------- */
.tabs{display:flex;gap:6px;margin-left:10px}
.tabs button{background:transparent;border:0;color:#9aa8b6;font-weight:700;padding:8px 12px;border-radius:8px;cursor:pointer;min-height:38px}
.tabs button[aria-pressed=true]{background:#2a3a4c;color:#fff}
.kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:18px}
.kpi div{background:#fff;border:2px solid #e4ebf1;border-radius:12px;padding:12px 14px}
.kpi i{display:block;font-style:normal;font-size:12.5px;color:#6a7686;margin-bottom:5px}
.kpi b{font-size:22px;letter-spacing:-.02em}
.kpi s{display:block;text-decoration:none;font-size:12.5px;color:#6a7686}
.tools select{min-height:44px;padding:8px 12px;border:2px solid #d9e2ec;border-radius:10px;background:#fff;max-width:260px}
.acc-new{display:flex;gap:6px;flex-wrap:wrap}
.cocard{background:#fff;border:2px solid #e4ebf1;border-radius:12px;padding:12px 16px;margin-bottom:14px;display:flex;gap:18px;flex-wrap:wrap;align-items:center;font-size:13.5px;color:#41586e}
.cocard b{font-size:15px;color:#16202b}
.cocard span{white-space:nowrap}
.cocard .no{color:#b3261e;font-weight:700}
.fac{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.fac-pv{height:90px;border:1px dashed #c3d3e0;border-radius:10px;background:#fff;display:grid;place-items:center;margin-bottom:8px;color:#8a96a3;font-size:13px;overflow:hidden}
.fac-pv img{max-height:84px;max-width:100%}
table.acc{min-width:980px}
table.acc td.what s{display:block;text-decoration:none;color:#8a96a3}
table.acc td.act{white-space:nowrap}
table.acc tbody tr{cursor:default}
select.st{border:1px solid transparent;border-radius:99px;padding:4px 8px;font-size:12.5px;font-weight:700;background:#eef2f6;cursor:pointer;color:#41586e}
.st-ok{background:#e3f4e8!important;color:#166534!important}.st-wait{background:#fff0d6!important;color:#8a5a00!important}.st-off{background:#f1f1f1!important;color:#8a96a3!important}
.fg{display:grid;grid-template-columns:repeat(6,1fr);gap:12px}
.fg .f{grid-column:span 3;margin:0}.fg .f--s{grid-column:span 1}.fg .f--w{grid-column:1/-1}
.fg .f label,.dlg__b .f label{font-size:13px}
.fg .f label small{font-weight:400;color:#6a7686}
.party{font-size:14px;background:#f7fafc;border:1px solid #e4ebf1;border-radius:10px;padding:10px 12px}
.warn3{color:#8a5a00}
.lnk{background:none;border:0;color:#1c4d85;text-decoration:underline;cursor:pointer;padding:0 4px;font-size:13px;font-weight:400}
h3.sub{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:#6a7686;margin:18px 0 8px}
table.items{min-width:0;width:100%}
table.items th{position:static;font-size:11.5px;padding:6px 6px}
table.items td{padding:4px 4px;border-bottom:0;vertical-align:middle}
table.items textarea,table.items input{width:100%;min-height:38px;padding:7px 9px;border:1px solid #d9e2ec;border-radius:8px;background:#fff;font-size:14px;resize:none;overflow:hidden}
table.items td:nth-child(2),table.items td:nth-child(3){width:70px}
#dd-items td:nth-child(4){width:110px}#dd-items td.i-sum{width:100px;text-align:right;font-weight:700;font-size:14px}
#dd-monthly td:nth-child(2){width:120px}#dd-monthly td:nth-child(3){width:180px}
.i-del{background:none;border:0;color:#b3261e;font-size:20px;cursor:pointer;min-width:36px;min-height:36px}
.tot{font-weight:800;text-align:right;margin:10px 0}
.file{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px solid #eef2f6;font-size:14px}
.file s{text-decoration:none;color:#8a96a3;font-size:12.5px;flex:1}
.file button{background:none;border:0;color:#b3261e;font-size:20px;cursor:pointer;min-width:36px;min-height:36px}
.up{cursor:pointer;margin-top:10px}
.acts{display:flex;gap:10px;flex-wrap:wrap}
.dlist{display:grid;gap:6px}
.drow{display:flex;align-items:center;gap:10px;flex-wrap:wrap;background:#fff;border:1px solid #e4ebf1;border-radius:10px;padding:8px 12px;font-size:14px}
.drow s{text-decoration:none;color:#41586e;font-weight:700}
.drow .btn{margin-left:auto}
.docs{margin:18px 0 0;border:2px solid #e4ebf1;border-radius:14px;background:#f7fafc;padding:14px 18px}
.docs h3{font-size:15px;margin:0 0 10px}
.note--doc .av{background:#fff0d6;color:#8a5a00}
@media (max-width:640px){.fg{grid-template-columns:1fr 1fr}.fg .f{grid-column:1/-1}.fg .f--s{grid-column:span 1}.tabs{margin-left:0;width:100%}.top .sp{margin-left:0}}

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
.speed h4{margin:14px 0 6px;font-size:14px}.speed ul{margin:0 0 8px;padding-left:18px;font-size:14px}.speed li{margin:3px 0}
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
  <nav class="tabs" aria-label="Разделы"><button type="button" data-v="funnel" aria-pressed="true">Воронка</button><button type="button" data-v="acc" aria-pressed="false">Бухгалтерия</button></nav>
  <span class="sp">
    <span><?= h($_SESSION['crm_name'] ?? '') ?></span>
    <a href="?password=1">Сменить пароль</a>
    <form method="post" class="out"><input type="hidden" name="csrf" value="<?= h(crm_csrf()) ?>">
      <button type="submit" name="logout" value="1">Выйти</button></form>
  </span>
</div></div>
<?php if ($ok): ?><div class="warn warn--ok"><?= h($ok) ?></div><?php endif; ?>

<div class="wrap" id="v-funnel">
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

<div class="wrap" id="v-acc" hidden>
  <div class="kpi" id="acc-kpi"></div>
  <div class="tools">
    <select id="acc-lead" aria-label="Клиент"></select>
    <input type="search" id="acc-q" placeholder="Поиск: номер, клиент, услуга" aria-label="Поиск по документам">
    <span class="acc-new">
      <button type="button" class="btn btn--sm" data-new="contract">+ Договор</button>
      <button type="button" class="btn btn--sm" data-new="spec">+ Спецификация</button>
      <button type="button" class="btn btn--sm" data-new="invoice">+ Счёт</button>
      <button type="button" class="btn btn--sm" data-new="act">+ Акт</button>
    </span>
    <button type="button" class="btn btn--gh btn--sm" id="acc-company">Карточка компании</button>
  </div>
  <div class="cocard" id="acc-cocard"></div>
  <div class="tbl"><div class="tbl-scroll">
    <table class="acc">
      <thead><tr><th>Документ</th><th>Клиент</th><th>Содержание</th><th>Сумма</th><th>Статус</th><th>Скан</th><th></th></tr></thead>
      <tbody id="acc-rows"></tbody>
    </table>
  </div><div class="empty" id="acc-empty" hidden>Документов пока нет. Начните с «+ Договор».</div></div>
  <p class="mini" style="margin:12px 4px">Печатная форма — кнопка «Открыть», в браузере «Печать → Сохранить как PDF». Подписанный скан загружается в карточку документа («Изменить»). Удалять можно только черновики, остальное переводите в «Отменён». Номера идут по порядку в пределах года отдельно для договоров, спецификаций, счетов и актов.</p>
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
        <div class="row"><em>Кто решает (ЛПР) и как обращаться</em><textarea class="ed ed--lpr" data-f="lpr" rows="4"></textarea></div>
        <div class="row"><em>Телефоны, почта, мессенджеры</em><textarea class="ed" data-f="contacts" rows="3"></textarea></div>
        <div class="row"><em>Город</em><textarea class="ed" data-f="city" rows="1"></textarea></div>
      </div>
      <div class="col">
        <h3>Деньги</h3>
        <div class="row"><em>Предложение, ₽</em><textarea class="ed" data-f="offer" rows="1"></textarea></div>
        <div class="row"><em>Компания</em><textarea class="ed" data-f="company" rows="1"></textarea></div>
      </div>
    </div>
    <div class="speed" id="d-speed" hidden></div>
    <div class="brief" id="d-brief"></div>
    <div class="docs" id="d-docs"></div>
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

<dialog id="ddlg"><div class="dlg">
  <div class="dlg__h"><div><h2 id="dd-title-h"></h2><div class="mini">Статус: <span id="dd-status"></span></div></div><button class="x" id="dd-x" aria-label="Закрыть">&times;</button></div>
  <div class="dlg__b">
    <div class="fg">
      <div class="f"><label for="dd-lead">Клиент</label><select id="dd-lead"></select></div>
      <div class="f f--s"><label for="dd-n">Номер</label><input id="dd-n"></div>
      <div class="f f--s"><label for="dd-date">Дата</label><input id="dd-date" placeholder="ДД.ММ.ГГГГ"></div>
      <div class="f" data-for="spec invoice act"><label for="dd-parent">К договору</label><select id="dd-parent"></select></div>
      <div class="f f--w"><label>Реквизиты клиента <button type="button" class="lnk" id="dd-party-edit">изменить</button></label><div class="party" id="dd-party"></div></div>
      <div class="f f--w" data-for="spec"><label for="dd-title">Предмет спецификации <small>(необязательно)</small></label><textarea id="dd-title" rows="2" placeholder="Например: сайт на домене клиента и реклама в Яндекс Директе"></textarea></div>
      <div class="f f--w" data-for="invoice act"><label for="dd-basis">Основание</label><input id="dd-basis" placeholder="Договор № 1 от 24.09.2026, спецификация № 1"></div>
      <div class="f" data-for="invoice act spec"><label for="dd-period">Период <small>(для спецификации — срок разовых услуг)</small></label><input id="dd-period" placeholder="октябрь 2026 · 10 рабочих дней с момента получения материалов"></div>
      <div class="f f--s" data-for="invoice"><label for="dd-due">Оплатить до</label><input id="dd-due" placeholder="ДД.ММ.ГГГГ"></div>
      <div class="f f--s" data-for="spec"><label for="dd-prepay">Предоплата, %</label><input id="dd-prepay" inputmode="numeric"></div>
    </div>
    <div data-for="spec invoice act">
      <h3 class="sub">Услуги</h3>
      <table class="items" id="dd-items"><thead><tr><th>Наименование</th><th>Кол-во</th><th>Ед.</th><th>Цена, ₽</th><th>Сумма</th><th></th></tr></thead><tbody></tbody></table>
      <button type="button" class="btn btn--gh btn--sm" id="dd-add">+ строка</button>
    </div>
    <div data-for="spec">
      <h3 class="sub">Ежемесячные услуги</h3>
      <table class="items" id="dd-monthly"><thead><tr><th>Наименование</th><th>В месяц, ₽</th><th>Начало</th><th></th></tr></thead><tbody></tbody></table>
      <button type="button" class="btn btn--gh btn--sm" id="dd-madd">+ строка</button>
    </div>
    <p class="tot" id="dd-total"></p>
    <div class="f" style="margin-top:14px"><label for="dd-note">Примечание <small>(в договоре — раздел «Особые условия», в остальных — абзац перед подписями)</small></label><textarea id="dd-note" rows="2"></textarea></div>
    <div id="dd-files-box"><h3 class="sub">Сканы подписанного</h3><div id="dd-files"></div>
      <label class="btn btn--gh btn--sm up"><span id="dd-file-lbl">Загрузить скан</span><input type="file" id="dd-file" accept=".pdf,.jpg,.jpeg,.png,.docx,.xlsx" hidden></label></div>
  </div>
  <div class="dlg__f acts"><button type="button" class="btn" id="dd-save">Сохранить</button><a class="btn btn--gh" id="dd-open" target="_blank" rel="noopener">Открыть печатную форму</a><button type="button" class="btn btn--gh" id="dd-del">Удалить черновик</button></div>
</div></dialog>

<dialog id="cdlg"><div class="dlg">
  <div class="dlg__h"><div><h2>Карточка компании</h2><div class="mini">Печатаются в договорах, счетах и актах. Снимок реквизитов сохраняется в документ при его сохранении.</div></div><button class="x" id="cd-x" aria-label="Закрыть">&times;</button></div>
  <div class="dlg__b"><div class="fg">
    <div class="f"><label>Бренд</label><input name="brand" placeholder="Форма сайта"></div>
    <div class="f"><label>Сайт</label><input name="site"></div>
    <div class="f f--w"><label>Полное наименование</label><input name="name"></div>
    <div class="f"><label>Короткое</label><input name="short"></div>
    <div class="f f--s"><label>ИНН</label><input name="inn"></div>
    <div class="f f--s"><label>ОГРНИП / ОГРН</label><input name="ogrn"></div>
    <div class="f f--w"><label>Адрес</label><input name="address"></div>
    <div class="f"><label>Телефон</label><input name="phone"></div>
    <div class="f"><label>E-mail</label><input name="email"></div>
    <div class="f f--w"><label>Банк</label><input name="bank" placeholder="Название банка"></div>
    <div class="f f--s"><label>БИК</label><input name="bik"></div>
    <div class="f f--s"><label>Корр. счёт</label><input name="ks"></div>
    <div class="f f--s"><label>Расчётный счёт</label><input name="rs"></div>
    <div class="f"><label>Подписант (ФИО полностью)</label><input name="signer"></div>
    <div class="f"><label>Подпись (И. О. Фамилия)</label><input name="signer_short"></div>
    <div class="f f--w"><label>Действует на основании</label><input name="basis"></div>
    <div class="f f--w"><label>Строка про НДС</label><input name="tax"></div>
  </div>
  <h3 class="sub">Подпись и печать <small style="font-weight:400;text-transform:none;letter-spacing:0">— встают в документы автоматически. Нужны PNG с прозрачным фоном или фото на белом листе</small></h3>
  <div class="fac">
    <div><div class="fac-pv" id="fac-sign"></div><label class="btn btn--gh btn--sm up"><span>Загрузить подпись</span><input type="file" data-kind="sign" accept=".png,.jpg,.jpeg" hidden></label> <button type="button" class="lnk" data-facdel="sign">убрать</button></div>
    <div><div class="fac-pv" id="fac-stamp"></div><label class="btn btn--gh btn--sm up"><span>Загрузить печать</span><input type="file" data-kind="stamp" accept=".png,.jpg,.jpeg" hidden></label> <button type="button" class="lnk" data-facdel="stamp">убрать</button></div>
  </div></div>
  <div class="dlg__f acts"><button type="button" class="btn" id="cd-save">Сохранить</button></div>
</div></dialog>

<dialog id="pdlg"><div class="dlg">
  <div class="dlg__h"><div><h2>Реквизиты клиента</h2><div class="mini" id="pd-co"></div></div><button class="x" id="pd-x" aria-label="Закрыть">&times;</button></div>
  <div class="dlg__b"><div class="fg">
    <div class="f f--w"><label>Полное наименование <small>как в договоре: «Индивидуальный предприниматель Иванов Иван Иванович», «ООО «Ромашка»»</small></label><input name="name"></div>
    <div class="f"><label>Короткое</label><input name="short" placeholder="ИП Иванов И. И."></div>
    <div class="f f--s"><label>ИНН</label><input name="inn"></div>
    <div class="f f--s"><label>КПП</label><input name="kpp"></div>
    <div class="f f--s"><label>ОГРНИП / ОГРН</label><input name="ogrn"></div>
    <div class="f f--w"><label>Адрес</label><input name="address"></div>
    <div class="f"><label>Телефон</label><input name="phone"></div>
    <div class="f"><label>E-mail</label><input name="email"></div>
    <div class="f"><label>Подписант (ФИО полностью)</label><input name="signer"></div>
    <div class="f"><label>Подпись (И. О. Фамилия)</label><input name="signer_short"></div>
    <div class="f f--w"><label>Действует на основании</label><input name="basis" placeholder="ОГРНИП … / Устава"></div>
    <div class="f f--w"><label>Банк</label><input name="bank"></div>
    <div class="f f--s"><label>БИК</label><input name="bik"></div>
    <div class="f f--s"><label>Корр. счёт</label><input name="ks"></div>
    <div class="f f--s"><label>Расчётный счёт</label><input name="rs"></div>
  </div></div>
  <div class="dlg__f acts"><button type="button" class="btn" id="pd-save">Сохранить</button></div>
</div></dialog>

<script>
const DATA = <?= json_encode($data, JSON_UNESCAPED_UNICODE) ?>;
const CSRF = <?= json_encode(crm_csrf()) ?>;
const SCRIPTS = <?= json_encode(require __DIR__ . '/scripts.php', JSON_UNESCAPED_UNICODE) ?>;
const QUESTIONS = <?= json_encode(require __DIR__ . '/questions.php', JSON_UNESCAPED_UNICODE) ?>;
const DOCS = <?= json_encode($docs, JSON_UNESCAPED_UNICODE) ?>;
const COMPANY = <?= json_encode($company, JSON_UNESCAPED_UNICODE) ?>;
const DOCTYPES = <?= json_encode(crm_doc_types(), JSON_UNESCAPED_UNICODE) ?>;
const FAC = <?= json_encode(['sign' => (bool)crm_company_file('sign'), 'stamp' => (bool)crm_company_file('stamp')]) ?>;
const DOCSTATUSES = <?= json_encode(['invoice' => crm_doc_statuses('invoice'), 'other' => crm_doc_statuses('act')], JSON_UNESCAPED_UNICODE) ?>;
</script>
<script src="app.js?v=<?= substr(md5_file(__DIR__ . "/app.js"), 0, 8) ?>" defer></script>
<script src="acc.js?v=<?= substr(md5_file(__DIR__ . "/acc.js"), 0, 8) ?>" defer></script>
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
