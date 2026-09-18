<?php
/* Общая часть админки: вход, хранилище, вспомогательные функции.
   Базы данных нет — всё лежит в data/leads.json, этого хватает на сотни сделок. */

/* ------------------------------------------------------------------ доступ */
const CRM_USER = 'админ';
const CRM_USER_LAT = 'admin';          // тот же пользователь латиницей
const CRM_PASS = 'admin';              // СМЕНИТЬ ПЕРЕД ВЫКЛАДКОЙ НА ДОМЕН
const CRM_TITLE = 'Форма сайта — воронка';

function crm_boot() {
    if (session_status() === PHP_SESSION_NONE) {
        session_set_cookie_params(['httponly' => true, 'samesite' => 'Lax',
            'secure' => (($_SERVER['HTTPS'] ?? '') === 'on')]);
        session_start();
    }
    header('X-Frame-Options: DENY');
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: no-referrer');
}

function crm_logged_in() { return !empty($_SESSION['crm_ok']); }

function crm_login($u, $p) {
    $u = trim($u);
    $okUser = ($u === CRM_USER || strcasecmp($u, CRM_USER_LAT) === 0);
    if ($okUser && hash_equals(CRM_PASS, $p)) {
        session_regenerate_id(true);
        $_SESSION['crm_ok'] = true;
        $_SESSION['crm_user'] = $u;
        $_SESSION['crm_csrf'] = bin2hex(random_bytes(16));
        return true;
    }
    usleep(400000);                     // притормаживаем перебор
    return false;
}

function crm_csrf() { return $_SESSION['crm_csrf'] ?? ''; }
function crm_csrf_ok($t) { return crm_csrf() && hash_equals(crm_csrf(), (string)$t); }

/* --------------------------------------------------------------- хранилище */
function crm_path() { return __DIR__ . '/data/leads.json'; }

function crm_read() {
    $f = crm_path();
    if (!file_exists($f)) return ['stages' => [], 'leads' => []];
    $d = json_decode(file_get_contents($f), true);
    return is_array($d) ? $d : ['stages' => [], 'leads' => []];
}

/* Запись под блокировкой: два менеджера не затрут правки друг друга. */
function crm_write($data) {
    $f = crm_path();
    $fh = fopen($f, 'c+');
    if (!$fh) return false;
    flock($fh, LOCK_EX);
    ftruncate($fh, 0); rewind($fh);
    fwrite($fh, json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
    fflush($fh); flock($fh, LOCK_UN); fclose($fh);
    return true;
}

function crm_find(&$data, $id) {
    foreach ($data['leads'] as $i => $l) if ($l['id'] === $id) return $i;
    return -1;
}

function crm_now() { return date('d.m.Y H:i'); }
function h($s) { return htmlspecialchars((string)$s, ENT_QUOTES, 'UTF-8'); }

/* Поля, которые менеджер правит руками в карточке. */
function crm_editable() {
    return ['company', 'city', 'was_url', 'now_url', 'was_problems',
            'now_done', 'left_todo', 'contacts', 'offer', 'measure_src'];
}
