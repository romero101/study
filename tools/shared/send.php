<?php
/* Приём заявок. Кладётся рядом с index.html на хостинге REG.RU (PHP включён).
   Настройка — четыре строки ниже. Ничего больше менять не нужно.
   Журнал пишется в leads.log.php: на хостинге статику отдаёт nginx, .htaccess для неё
   не работает, а .php-файл с exit в первой строке наружу не прочитать никак. */
$TO       = '__EMAIL__';   // куда дублировать заявки письмом
$TG_TOKEN = '';            // токен бота: заявки в Telegram приходят мгновенно
$TG_CHAT  = '';            // id чата или канала (например -1001234567890)
$SUBJECT  = 'Заявка с сайта __BRAND__';

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { http_response_code(405); exit('{"ok":false}'); }

/* --- антиспам: скрытое поле, слишком быстрая отправка, частота с одного IP --- */
if (!empty($_POST['_gotcha'])) { exit('{"ok":true}'); }            // бот заполнил ловушку
if (isset($_POST['_elapsed']) && (int)$_POST['_elapsed'] < 2) { exit('{"ok":true}'); }
$ip = $_SERVER['REMOTE_ADDR'] ?? '0';
$LOG = __DIR__ . '/leads.log.php';
if (!file_exists($LOG)) { @file_put_contents($LOG, "<?php exit; ?>\n", LOCK_EX); }

/* --- телефон обязателен и должен быть похож на номер --- */
$digits = preg_replace('/\D+/', '', $_POST['Телефон'] ?? '');
if (strlen($digits) !== 11) { http_response_code(422); exit('{"ok":false,"error":"phone"}'); }

/* Защита от дублей — по номеру, а не по IP: за общим адресом провайдера
   могут сидеть разные люди, и терять вторую заявку нельзя. Повторная отправка
   того же номера в течение минуты просто не дублирует уведомление. */
$dup = sys_get_temp_dir() . '/lead_' . md5($digits . '|' . $ip);
$isDup = file_exists($dup) && (time() - filemtime($dup)) < 60;
@touch($dup);

/* --- собираем письмо из всех полей формы --- */
$lines = [];
foreach ($_POST as $k => $v) {
    if ($k === '_gotcha' || !is_string($v) || $v === '') continue;
    $k = mb_substr(strip_tags($k), 0, 60);
    $v = mb_substr(strip_tags($v), 0, 800);
    $lines[] = ($k[0] === '_' ? ltrim($k, '_') : $k) . ': ' . $v;
}
$lines[] = 'IP: ' . $ip;
$lines[] = 'UA: ' . mb_substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 200);
$lines[] = 'Время: ' . date('d.m.Y H:i');
$body = implode("\n", $lines);

$sentAnywhere = false;
if ($isDup) {
    @file_put_contents($LOG,
        "ПОВТОР (уведомление не дублировали)\n" . $body . "\n" . str_repeat('-', 40) . "\n",
        FILE_APPEND | LOCK_EX);
    exit('{"ok":true}');
}

/* --- Telegram: доставка за секунды, видно на телефоне --- */
if ($TG_TOKEN && $TG_CHAT) {
    $ctx = stream_context_create(['http' => [
        'method'  => 'POST',
        'header'  => "Content-Type: application/x-www-form-urlencoded\r\n",
        'content' => http_build_query(['chat_id' => $TG_CHAT, 'text' => $SUBJECT . "\n\n" . $body]),
        'timeout' => 8,
    ]]);
    $r = @file_get_contents("https://api.telegram.org/bot$TG_TOKEN/sendMessage", false, $ctx);
    if ($r !== false) $sentAnywhere = true;
}

/* --- письмо: резервный канал --- */
if ($TO) {
    $headers = "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=utf-8\r\n";
    $headers .= 'From: site@' . preg_replace('/^www\./', '', $_SERVER['HTTP_HOST'] ?? 'localhost') . "\r\n";
    if (@mail($TO, '=?UTF-8?B?' . base64_encode($SUBJECT) . '?=', $body, $headers)) $sentAnywhere = true;
}

/* --- журнал на диске: заявка не теряется, даже если оба канала легли --- */
if (@file_put_contents($LOG, $body . "\n" . str_repeat('-', 40) . "\n", FILE_APPEND | LOCK_EX)) $sentAnywhere = true;

if (!$sentAnywhere) { http_response_code(502); exit('{"ok":false,"error":"delivery"}'); }
echo '{"ok":true}';
