<?php
/* JSON-интерфейс админки: смена этапа, правка полей, комментарии, новая сделка. */
require __DIR__ . '/lib.php';
crm_boot();
header('Content-Type: application/json; charset=utf-8');

if (!crm_logged_in()) { http_response_code(401); exit(json_encode(['error' => 'auth'])); }
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { http_response_code(405); exit('{}'); }
if (!crm_csrf_ok($_POST['csrf'] ?? '')) { http_response_code(403); exit(json_encode(['error' => 'csrf'])); }

$action = $_POST['action'] ?? '';
$data   = crm_read();
$user   = $_SESSION['crm_user'] ?? 'админ';
$out    = ['ok' => true];

if ($action === 'stage') {
    $i = crm_find($data, $_POST['id'] ?? '');
    $stage = $_POST['stage'] ?? '';
    if ($i < 0 || !in_array($stage, $data['stages'], true)) {
        http_response_code(422); exit(json_encode(['error' => 'bad']));
    }
    $was = $data['leads'][$i]['stage'];
    if ($was !== $stage) {
        $data['leads'][$i]['stage'] = $stage;
        $data['leads'][$i]['updated'] = crm_now();
        // смена этапа сама попадает в историю — видно, кто и когда двинул сделку
        $data['leads'][$i]['comments'][] = [
            'at' => crm_now(), 'who' => $user, 'kind' => 'stage',
            'text' => 'Этап: ' . $was . ' → ' . $stage,
        ];
    }
    $out['comments'] = $data['leads'][$i]['comments'];

} elseif ($action === 'comment') {
    $i = crm_find($data, $_POST['id'] ?? '');
    $text = trim((string)($_POST['text'] ?? ''));
    if ($i < 0 || $text === '') { http_response_code(422); exit(json_encode(['error' => 'bad'])); }
    $data['leads'][$i]['comments'][] = [
        'at' => crm_now(), 'who' => $user, 'kind' => 'note',
        'text' => mb_substr($text, 0, 4000),
    ];
    $data['leads'][$i]['updated'] = crm_now();
    $out['comments'] = $data['leads'][$i]['comments'];

} elseif ($action === 'field') {
    $i = crm_find($data, $_POST['id'] ?? '');
    $field = $_POST['field'] ?? '';
    if ($i < 0 || !in_array($field, crm_editable(), true)) {
        http_response_code(422); exit(json_encode(['error' => 'bad']));
    }
    $val = (string)($_POST['value'] ?? '');
    $val = $field === 'offer' ? (int)preg_replace('/\D+/', '', $val) : mb_substr(trim($val), 0, 4000);
    $data['leads'][$i][$field] = $val;
    $data['leads'][$i]['updated'] = crm_now();

} elseif ($action === 'create') {
    $company = trim((string)($_POST['company'] ?? ''));
    if ($company === '') { http_response_code(422); exit(json_encode(['error' => 'company'])); }
    $max = 0;
    foreach ($data['leads'] as $l) $max = max($max, (int)($l['n'] ?? 0));
    $lead = ['id' => 'l' . str_pad((string)($max + 1), 2, '0', STR_PAD_LEFT),
             'n' => $max + 1, 'company' => mb_substr($company, 0, 200),
             'city' => mb_substr(trim((string)($_POST['city'] ?? '')), 0, 100),
             'was_url' => mb_substr(trim((string)($_POST['was_url'] ?? '')), 0, 500),
             'now_url' => '', 'was_problems' => '', 'now_done' => '', 'left_todo' => '',
             'contacts' => mb_substr(trim((string)($_POST['contacts'] ?? '')), 0, 500),
             'pagespeed' => null, 'offer' => (int)preg_replace('/\D+/', '', (string)($_POST['offer'] ?? '')),
             'stage' => $data['stages'][0] ?? 'Не связывались', 'measure_src' => '',
             'comments' => [['at' => crm_now(), 'who' => $user, 'kind' => 'stage', 'text' => 'Сделка заведена']],
             'updated' => crm_now()];
    $data['leads'][] = $lead;
    $out['lead'] = $lead;

} else {
    http_response_code(400); exit(json_encode(['error' => 'action']));
}

crm_write($data);
echo json_encode($out, JSON_UNESCAPED_UNICODE);
