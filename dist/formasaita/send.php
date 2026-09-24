<?php
/* Заявки с сайта студии. Каждая заявка сразу становится сделкой в воронке (/admin/),
   плюс дублируется в Telegram и на почту, если они настроены ниже. */
$TO       = '';            // почта для копий заявок
$TG_TOKEN = '';            // токен Telegram-бота
$TG_CHAT  = '';            // id чата
$SUBJECT  = 'Заявка с сайта formasaita.ru';

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { http_response_code(405); exit('{"ok":false}'); }

/* антиспам: скрытое поле и слишком быстрая отправка. Боту отвечаем «ок», чтобы не подбирал обход */
if (!empty($_POST['_gotcha'])) exit('{"ok":true}');
if (isset($_POST['_elapsed']) && (int)$_POST['_elapsed'] < 2) exit('{"ok":true}');

$clean = function ($key, $max) {
    $v = $_POST[$key] ?? '';
    return is_string($v) ? mb_substr(trim(strip_tags($v)), 0, $max) : '';
};
$phone = $clean('phone', 40);
$digits = preg_replace('/\D+/', '', $phone);
if (strlen($digits) !== 11) { http_response_code(422); exit('{"ok":false,"error":"phone"}'); }

$name = $clean('name', 80);  $company = $clean('company', 200);  $site = $clean('site', 300);
$service = $clean('service', 120);  $message = $clean('message', 2000);
$page = $clean('page', 120);
if ($page !== '' && !preg_match('~^/[a-z0-9/_-]*$~', $page)) $page = '';
$ip = $_SERVER['REMOTE_ADDR'] ?? '0';

/* повтор того же номера в течение минуты вторую сделку не создаёт */
$dup = sys_get_temp_dir() . '/fs_lead_' . md5($digits);
$isDup = file_exists($dup) && (time() - filemtime($dup)) < 60;
@touch($dup);
if ($isDup) exit('{"ok":true}');

$body = implode("\n", array_filter([
    $service ? "Услуга: $service" : '', "Телефон: $phone", $name ? "Имя: $name" : '',
    $company ? "Компания: $company" : '', $site ? "Сайт: $site" : '', $message ? "Задача: $message" : '', $page ? "Страница: $page" : '',
    'Время: ' . date('d.m.Y H:i'), "IP: $ip",
]));

/* 1. сделка в воронке */
require __DIR__ . '/admin/lib.php';
crm_migrate();
$data = crm_read();
if (!$data['stages']) $data['stages'] = ['Не связывались', 'Дозвонился до ЛПР', 'Отправил лендинг',
    'Взял обратную связь', 'Счёт выставлен', 'Оплачено', 'В работе', 'Отказ'];
crm_add_lead($data, [
    'company' => $company ?: ($name ?: 'Заявка с сайта'), 'was_url' => $site,
    'contacts' => trim("$name $phone"), 'source' => 'site',
], 'сайт', 'Заявка с сайта' . ($service ? " · $service" : '') . ($page ? "\nСо страницы: $page" : '') . ($message ? "\n$message" : ''));
$saved = crm_write($data);

/* 2. журнал — закрытый .php-файл, снаружи не читается */
$log = __DIR__ . '/leads.log.php';
if (!file_exists($log)) @file_put_contents($log, "<?php exit; ?>\n", LOCK_EX);
if (@file_put_contents($log, $body . "\n" . str_repeat('-', 40) . "\n", FILE_APPEND | LOCK_EX)) $saved = true;

/* 3. уведомления */
if ($TG_TOKEN && $TG_CHAT) {
    $ctx = stream_context_create(['http' => ['method' => 'POST', 'timeout' => 8,
        'header' => "Content-Type: application/x-www-form-urlencoded\r\n",
        'content' => http_build_query(['chat_id' => $TG_CHAT, 'text' => $SUBJECT . "\n\n" . $body])]]);
    if (@file_get_contents("https://api.telegram.org/bot$TG_TOKEN/sendMessage", false, $ctx) !== false) $saved = true;
}
if ($TO) {
    $headers = "MIME-Version: 1.0\r\nContent-Type: text/plain; charset=utf-8\r\nFrom: site@formasaita.ru\r\n";
    if (@mail($TO, '=?UTF-8?B?' . base64_encode($SUBJECT) . '?=', $body, $headers)) $saved = true;
}

if (!$saved) { http_response_code(502); exit('{"ok":false,"error":"delivery"}'); }
echo '{"ok":true}';
