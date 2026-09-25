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

/* ------------------------------------------------------------ бухгалтерия */
/* Первичка лежит в data/docs.php: договоры, спецификации, счета, акты. Сканы подписанных
   документов — вне веб-корня (../../../crm-files), чтобы nginx не отдал их по прямой ссылке. */
function crm_docs()          { return crm_load('docs', ['docs' => []]); }
function crm_docs_write($d)  { return crm_save('docs', $d); }
function crm_doc_types()     { return ['contract' => 'Договор', 'spec' => 'Спецификация', 'invoice' => 'Счёт', 'act' => 'Акт']; }
function crm_doc_statuses($type) {
    return $type === 'invoice' ? ['Черновик', 'Выставлен', 'Оплачен', 'Отменён'] : ['Черновик', 'Отправлен', 'Подписан', 'Отменён'];
}
function crm_company() {
    return array_merge([
        'brand' => 'Форма сайта', 'name' => 'Индивидуальный предприниматель Кочкин Роман Андреевич', 'short' => 'ИП Кочкин Р. А.',
        'inn' => '526109316232', 'ogrn' => '318527500132392', 'address' => 'г. Нижний Новгород',
        'email' => '', 'phone' => '+7 (929) 053-76-03', 'site' => 'formasaita.ru',
        'bank' => '', 'bik' => '', 'ks' => '', 'rs' => '',
        'signer' => 'Кочкин Роман Андреевич', 'signer_short' => 'Р. А. Кочкин', 'basis' => 'ОГРНИП 318527500132392',
        'tax' => 'НДС не облагается (применяется упрощённая система налогообложения)',
    ], crm_load('company', []));
}
function crm_company_fields() { return ['brand', 'name', 'short', 'inn', 'ogrn', 'address', 'email', 'phone', 'site', 'bank', 'bik', 'ks', 'rs', 'signer', 'signer_short', 'basis', 'tax']; }
function crm_party_fields()   { return ['name', 'short', 'inn', 'ogrn', 'kpp', 'address', 'email', 'phone', 'bank', 'bik', 'ks', 'rs', 'signer', 'signer_short', 'basis']; }
function crm_doc_find(&$D, $id) {
    foreach ($D['docs'] as $i => $d) if ($d['id'] === $id) return $i;
    return -1;
}
/* Следующий номер: сквозной по типу документа в пределах года. */
function crm_doc_next_number($D, $type, $date) {
    $year = substr($date, -4); $max = 0;
    foreach ($D['docs'] as $d) {
        if ($d['type'] !== $type || substr($d['date'], -4) !== $year) continue;
        $max = max($max, (int)preg_replace('/\D.*$/', '', (string)$d['n']));
    }
    return (string)($max + 1);
}
function crm_files_dir() {
    $root = dirname(__DIR__, 3) . '/crm-files';
    if (!is_dir($root)) @mkdir($root, 0700, true);
    if (is_dir($root) && is_writable($root)) return $root;
    $f = __DIR__ . '/data/files';                       // запасной вариант: имена файлов случайные
    if (!is_dir($f)) { @mkdir($f, 0700, true); @file_put_contents($f . '/index.php', CRM_GUARD); }
    return $f;
}
function crm_money($n) { return number_format((float)$n, 2, ',', ' '); }
function crm_date_ru($d) {   // 24.09.2026 -> «24» сентября 2026 г.
    $m = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
    if (!preg_match('/^(\d\d)\.(\d\d)\.(\d{4})$/', $d, $x)) return h($d);
    return '«' . $x[1] . '» ' . $m[(int)$x[2] - 1] . ' ' . $x[3] . ' г.';
}
/* Сумма прописью: рубли и копейки. */
function crm_words($n) {
    $n = round((float)$n, 2); $rub = (int)floor($n); $kop = (int)round(($n - $rub) * 100);
    $ones = [['', 'один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять'],
             ['', 'одна', 'две', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять']];
    $teens = ['десять', 'одиннадцать', 'двенадцать', 'тринадцать', 'четырнадцать', 'пятнадцать', 'шестнадцать', 'семнадцать', 'восемнадцать', 'девятнадцать'];
    $tens = ['', '', 'двадцать', 'тридцать', 'сорок', 'пятьдесят', 'шестьдесят', 'семьдесят', 'восемьдесят', 'девяносто'];
    $hund = ['', 'сто', 'двести', 'триста', 'четыреста', 'пятьсот', 'шестьсот', 'семьсот', 'восемьсот', 'девятьсот'];
    $units = [['рубль', 'рубля', 'рублей', 0], ['тысяча', 'тысячи', 'тысяч', 1], ['миллион', 'миллиона', 'миллионов', 0], ['миллиард', 'миллиарда', 'миллиардов', 0]];
    $plural = function ($k, $f) { $k = $k % 100; if ($k > 10 && $k < 20) return $f[2]; $k %= 10; return $k == 1 ? $f[0] : ($k >= 2 && $k <= 4 ? $f[1] : $f[2]); };
    if ($rub === 0) $out = 'ноль рублей';
    else {
        $out = ''; $i = 0; $r = $rub;
        while ($r > 0 && $i < 4) {
            $t = $r % 1000; $r = intdiv($r, 1000);
            if ($t) {
                $g = $units[$i][3];
                $s = trim($hund[intdiv($t, 100)] . ' ' . ($t % 100 >= 10 && $t % 100 < 20 ? $teens[$t % 10] : trim($tens[intdiv($t % 100, 10)] . ' ' . $ones[$g][$t % 10])));
                $out = $s . ' ' . $plural($t, $units[$i]) . ' ' . $out;
            } elseif ($i === 0) $out = 'рублей ' . $out;
            $i++;
        }
        $out = trim($out);
    }
    $out .= ' ' . str_pad((string)$kop, 2, '0', STR_PAD_LEFT) . ' ' . $plural($kop, ['копейка', 'копейки', 'копеек']);
    return mb_strtoupper(mb_substr($out, 0, 1)) . mb_substr($out, 1);
}
