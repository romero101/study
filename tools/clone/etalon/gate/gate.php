<?php
/* Вход на закрытую копию: логин и пароль сверяются без учёта регистра (телефон сам ставит заглавную).
   Подключается из index.php каждой страницы: require 'gate.php'; etalon_gate(); readfile('page.html'); */
function etalon_gate() {
    $L = 'etalon'; $P = 'etalon'; $C = 'etalon_ok'; $base = '/demo/etalon/';
    $token = hash('sha256', $L . '|' . $P . '|' . __DIR__);
    if (($_SERVER['REQUEST_METHOD'] ?? '') === 'POST' && isset($_POST['u'])) {
        if (strtolower(trim($_POST['u'])) === $L && strtolower(trim($_POST['p'] ?? '')) === $P) {
            setcookie($C, $token, ['expires' => time() + 86400 * 30, 'path' => $base, 'secure' => true, 'httponly' => true, 'samesite' => 'Lax']);
            header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?')); exit;
        }
        $err = 'Неверный логин или пароль';
    }
    header('X-Robots-Tag: noindex, nofollow, noarchive');
    if (($_COOKIE[$C] ?? '') === $token) return;
    http_response_code(401);
    ?><!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Вход</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;font:16px/1.5 -apple-system,Arial,sans-serif;background:#f3f5f8;color:#16202b}form{background:#fff;padding:28px;border-radius:14px;width:min(92vw,340px);box-shadow:0 10px 30px rgba(0,0,0,.08)}h1{font-size:20px;margin:0 0 14px}input{width:100%;box-sizing:border-box;min-height:46px;padding:10px 12px;border:2px solid #d9e2ec;border-radius:10px;font:inherit;margin-bottom:12px}button{width:100%;min-height:46px;border:0;border-radius:10px;background:#1a9bff;color:#fff;font:700 16px/1 inherit}p.e{color:#b3261e;margin:0 0 10px}</style></head>
<body><form method="post"><h1>Закрытая страница</h1><?php if (!empty($err)) echo '<p class="e">' . $err . '</p>'; ?>
<input name="u" placeholder="Логин" autocomplete="username" autocapitalize="none" autocorrect="off" required><input name="p" type="password" placeholder="Пароль" autocomplete="current-password" required><button>Войти</button></form></body></html><?php
    exit;
}
