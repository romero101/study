<?php
/* Общая часть админки: вход, хранилище, вспомогательные функции.
   Базы данных нет — всё лежит в data/*.php, этого хватает на сотни сделок.

   Почему .php, а не .json: на хостинге статику отдаёт nginx, .htaccess для неё не работает,
   и data/leads.json открывался по прямой ссылке всем желающим. Файл .php с «exit» в первой
   строке сервер исполняет, а не отдаёт — снаружи приходит пустая страница. */

const CRM_TITLE = 'Форма сайта — воронка';
const CRM_GUARD = "<?php exit; ?>\n";
const CRM_MIN_PASS = 8;
const CRM_MAX_FAILS = 5;               // неудачных входов с одного адреса
const CRM_LOCK_MIN = 15;               // на сколько минут после этого закрываем вход

function crm_boot() {
    if (session_status() === PHP_SESSION_NONE) {
        session_name('fs_crm');
        session_set_cookie_params(['httponly' => true, 'samesite' => 'Strict',
            'secure' => (($_SERVER['HTTPS'] ?? '') === 'on')]);
        session_start();
    }
    header('X-Frame-Options: DENY');
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: no-referrer');
    header('Cache-Control: no-store');
    crm_migrate();
}

/* --------------------------------------------------------------- хранилище */
function crm_file($name) { return __DIR__ . '/data/' . $name . '.php'; }

function crm_load($name, $default) {
    $f = crm_file($name);
    if (!file_exists($f)) return $default;
    $raw = file_get_contents($f);
    if (strpos($raw, CRM_GUARD) === 0) $raw = substr($raw, strlen(CRM_GUARD));
    $d = json_decode($raw, true);
    return is_array($d) ? $d : $default;
}

/* Запись под блокировкой: два менеджера не затрут правки друг друга. */
function crm_save($name, $data) {
    $fh = fopen(crm_file($name), 'c+');
    if (!$fh) return false;
    flock($fh, LOCK_EX);
    ftruncate($fh, 0); rewind($fh);
    fwrite($fh, CRM_GUARD . json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
    fflush($fh); flock($fh, LOCK_UN); fclose($fh);
    return true;
}

function crm_read()       { return crm_load('store', ['stages' => [], 'leads' => []]); }
function crm_write($data) { return crm_save('store', $data); }

/* Первый запуск после обновления: переносим открытый leads.json в закрытый файл и удаляем его. */
function crm_migrate() {
    $old = __DIR__ . '/data/leads.json';
    if (!file_exists($old)) return;
    if (!file_exists(crm_file('store'))) {
        $d = json_decode(file_get_contents($old), true);
        if (!is_array($d) || !crm_save('store', $d)) return;   // не перенесли — старый файл не трогаем
    }
    @unlink($old);
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
            'now_done', 'left_todo', 'contacts', 'lpr', 'offer', 'measure_src'];
}

/* Новая сделка: и из админки, и из формы на сайте студии. */
function crm_add_lead(&$data, $fields, $who, $firstNote) {
    $max = 0;
    foreach ($data['leads'] as $l) $max = max($max, (int)($l['n'] ?? 0));
    $lead = array_merge([
        'id' => 'l' . str_pad((string)($max + 1), 2, '0', STR_PAD_LEFT), 'n' => $max + 1,
        'company' => '', 'city' => '', 'was_url' => '', 'now_url' => '', 'was_problems' => '',
        'now_done' => '', 'left_todo' => '', 'contacts' => '', 'lpr' => '', 'pagespeed' => null, 'offer' => 0,
        'stage' => $data['stages'][0] ?? 'Не связывались', 'measure_src' => '', 'source' => 'manual',
    ], $fields);
    $lead['comments'] = [['at' => crm_now(), 'who' => $who, 'kind' => 'stage', 'text' => $firstNote]];
    $lead['updated'] = crm_now();
    $data['leads'][] = $lead;
    return $lead;
}

/* ------------------------------------------------------------------ доступ */
/* Пользователи лежат в data/users.php, пароли — только хешами. Пока файла нет, действует
   стартовая пара админ / admin, и сразу после входа система требует задать свой пароль. */
function crm_users() {
    $u = crm_load('users', []);
    if (!$u) {
        $u = ['админ' => ['hash' => password_hash('admin', PASSWORD_DEFAULT), 'name' => 'Администратор',
                          'aliases' => ['admin'], 'must_change' => true]];
        crm_save('users', $u);
    }
    return $u;
}

function crm_user_key($users, $login) {
    $login = mb_strtolower(trim((string)$login));
    foreach ($users as $key => $u) {
        if (mb_strtolower($key) === $login) return $key;
        foreach ($u['aliases'] ?? [] as $a) if (mb_strtolower($a) === $login) return $key;
    }
    return null;
}

function crm_ip() { return $_SERVER['REMOTE_ADDR'] ?? '0'; }

/* Сколько минут ещё закрыт вход для этого адреса (0 — открыт). */
function crm_locked_for() {
    $t = crm_load('throttle', [])[crm_ip()] ?? null;
    if (!$t || $t['fails'] < CRM_MAX_FAILS) return 0;
    $left = CRM_LOCK_MIN * 60 - (time() - $t['last']);
    return $left > 0 ? (int)ceil($left / 60) : 0;
}

function crm_note_fail($reset = false) {
    $all = crm_load('throttle', []);
    foreach ($all as $ip => $t) if (time() - $t['last'] > CRM_LOCK_MIN * 60) unset($all[$ip]);
    if ($reset) unset($all[crm_ip()]);
    else $all[crm_ip()] = ['fails' => ($all[crm_ip()]['fails'] ?? 0) + 1, 'last' => time()];
    crm_save('throttle', $all);
}

function crm_logged_in() { return !empty($_SESSION['crm_ok']); }
function crm_must_change() { return !empty($_SESSION['crm_must_change']); }

/* Возвращает '' при успехе или текст ошибки для человека. */
function crm_login($login, $pass) {
    if ($min = crm_locked_for()) return "Слишком много попыток. Вход закрыт ещё на $min мин.";
    $users = crm_users();
    $key = crm_user_key($users, $login);
    // проверяем хеш и для несуществующего логина — чтобы по времени ответа нельзя было угадать логин
    $hash = $key !== null ? $users[$key]['hash'] : '$2y$12$GO4VcCk5MCpTIzRKB0NvC.W510K03Knd69Rsmj/oDz/X7OG4KToWO';
    if (!password_verify((string)$pass, $hash) || $key === null) {
        crm_note_fail();
        return 'Неверный логин или пароль';
    }
    crm_note_fail(true);
    session_regenerate_id(true);
    $_SESSION['crm_ok'] = true;
    $_SESSION['crm_user'] = $key;
    $_SESSION['crm_name'] = $users[$key]['name'] ?? $key;
    $_SESSION['crm_must_change'] = !empty($users[$key]['must_change']);
    $_SESSION['crm_csrf'] = bin2hex(random_bytes(16));
    return '';
}

function crm_change_password($current, $new, $repeat) {
    $users = crm_users();
    $key = $_SESSION['crm_user'] ?? '';
    if (!isset($users[$key]) || !password_verify((string)$current, $users[$key]['hash'])) return 'Текущий пароль введён неверно';
    if (mb_strlen($new) < CRM_MIN_PASS) return 'Новый пароль короче ' . CRM_MIN_PASS . ' символов';
    if ($new !== $repeat) return 'Пароли не совпадают';
    if (mb_strtolower($new) === 'admin' || $new === $current) return 'Нужен новый пароль, не стартовый';
    $users[$key]['hash'] = password_hash($new, PASSWORD_DEFAULT);
    $users[$key]['must_change'] = false;
    if (!crm_save('users', $users)) return 'Не удалось сохранить: нет прав на запись в admin/data';
    $_SESSION['crm_must_change'] = false;
    session_regenerate_id(true);
    return '';
}

function crm_csrf() { return $_SESSION['crm_csrf'] ?? ''; }
function crm_csrf_ok($t) { return crm_csrf() && hash_equals(crm_csrf(), (string)$t); }
