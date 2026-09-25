<?php
/* JSON-интерфейс админки: смена этапа, правка полей, комментарии, новая сделка. */
require __DIR__ . '/lib.php';
crm_boot();
header('Content-Type: application/json; charset=utf-8');

if (!crm_logged_in() || crm_must_change()) { http_response_code(401); exit(json_encode(['error' => 'auth'])); }
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') { http_response_code(405); exit('{}'); }
if (!crm_csrf_ok($_POST['csrf'] ?? '')) { http_response_code(403); exit(json_encode(['error' => 'csrf'])); }

$action = $_POST['action'] ?? '';
$data   = crm_read();
$user   = $_SESSION['crm_name'] ?? ($_SESSION['crm_user'] ?? 'админ');
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
    $lead = crm_add_lead($data, [
        'company' => mb_substr($company, 0, 200),
        'city' => mb_substr(trim((string)($_POST['city'] ?? '')), 0, 100),
        'was_url' => mb_substr(trim((string)($_POST['was_url'] ?? '')), 0, 500),
        'contacts' => mb_substr(trim((string)($_POST['contacts'] ?? '')), 0, 500),
        'offer' => (int)preg_replace('/\D+/', '', (string)($_POST['offer'] ?? '')),
    ], $user, 'Сделка заведена');
    $out['lead'] = $lead;

} elseif ($action === 'brief_link') {
    /* Личная ссылка клиента на анкету запуска. Ключ создаётся один раз; повторный вызов возвращает тот же. */
    $i = crm_find($data, $_POST['id'] ?? '');
    if ($i < 0) { http_response_code(422); exit(json_encode(['error' => 'bad'])); }
    $b = $data['leads'][$i]['brief'] ?? [];
    if (empty($b['key'])) {
        $b = array_merge($b, ['key' => bin2hex(random_bytes(10)), 'created' => crm_now(), 'by' => $user,
                              'hints' => $b['hints'] ?? []]);
        $data['leads'][$i]['comments'][] = ['at' => crm_now(), 'who' => $user, 'kind' => 'note',
            'text' => 'Создана личная ссылка на анкету запуска — отправить клиенту'];
        $data['leads'][$i]['updated'] = crm_now();
    }
    if (isset($_POST['name'])) $b['name'] = mb_substr(trim((string)$_POST['name']), 0, 80);
    $data['leads'][$i]['brief'] = $b;
    $out['brief'] = $b;
    $out['comments'] = $data['leads'][$i]['comments'];

} elseif ($action === 'company_save') {
    /* Реквизиты студии для печатных форм. Хранилище сделок не трогаем. */
    $c = crm_load('company', []);
    foreach (crm_company_fields() as $f) if (isset($_POST[$f])) $c[$f] = mb_substr(trim((string)$_POST[$f]), 0, 300);
    if (!crm_save('company', $c)) { http_response_code(500); exit(json_encode(['error' => 'write'])); }
    exit(json_encode(['ok' => true, 'company' => crm_company()], JSON_UNESCAPED_UNICODE));

} elseif ($action === 'party_save') {
    /* Реквизиты контрагента живут в сделке; в документ попадает их снимок при сохранении. */
    $i = crm_find($data, $_POST['id'] ?? '');
    if ($i < 0) { http_response_code(422); exit(json_encode(['error' => 'bad'])); }
    $p = $data['leads'][$i]['party'] ?? [];
    foreach (crm_party_fields() as $f) if (isset($_POST[$f])) $p[$f] = mb_substr(trim((string)$_POST[$f]), 0, 300);
    $data['leads'][$i]['party'] = $p;
    $data['leads'][$i]['updated'] = crm_now();
    $out['party'] = $p;

} elseif ($action === 'doc_save') {
    $in = json_decode((string)($_POST['doc'] ?? ''), true);
    $types = crm_doc_types();
    if (!is_array($in) || !isset($types[$in['type'] ?? ''])) { http_response_code(422); exit(json_encode(['error' => 'type'])); }
    $type = $in['type'];
    $li = crm_find($data, (string)($in['lead_id'] ?? ''));
    if ($li < 0) { http_response_code(422); exit(json_encode(['error' => 'lead'])); }
    $D  = crm_docs();
    $id = (string)($in['id'] ?? '');
    $di = $id !== '' ? crm_doc_find($D, $id) : -1;
    $str = function ($k, $max = 400) use ($in) { return mb_substr(trim(strip_tags((string)($in[$k] ?? ''))), 0, $max); };
    $num = function ($v) { return round((float)str_replace([' ', "\xC2\xA0", ','], ['', '', '.'], (string)$v), 2); };
    $date = $str('date', 10);
    if (!preg_match('/^\d\d\.\d\d\.\d{4}$/', $date)) $date = date('d.m.Y');
    $items = [];
    foreach ((array)($in['items'] ?? []) as $it) {
        if (!is_array($it)) continue;
        $name = mb_substr(trim(strip_tags((string)($it['name'] ?? ''))), 0, 600);
        if ($name === '') continue;
        $qty = $num($it['qty'] ?? 1);
        $items[] = ['name' => $name, 'qty' => $qty > 0 ? $qty : 1, 'unit' => mb_substr(trim(strip_tags((string)($it['unit'] ?? 'усл.'))), 0, 20) ?: 'усл.', 'price' => $num($it['price'] ?? 0)];
    }
    $monthly = [];
    foreach ((array)($in['monthly'] ?? []) as $it) {
        if (!is_array($it)) continue;
        $name = mb_substr(trim(strip_tags((string)($it['name'] ?? ''))), 0, 600);
        if ($name === '') continue;
        $monthly[] = ['name' => $name, 'price' => $num($it['price'] ?? 0), 'start' => mb_substr(trim(strip_tags((string)($it['start'] ?? ''))), 0, 60)];
    }
    $total = 0; foreach ($items as $it) $total += $it['qty'] * $it['price'];
    $mtotal = 0; foreach ($monthly as $it) $mtotal += $it['price'];
    $lead  = $data['leads'][$li];
    $party = array_merge(['name' => $lead['company'], 'short' => $lead['company']], array_filter($lead['party'] ?? [], 'strlen'));
    if ($di >= 0) $doc = $D['docs'][$di];
    else {
        $max = 0; foreach ($D['docs'] as $d) $max = max($max, (int)substr($d['id'], 1));
        $doc = ['id' => 'd' . ($max + 1), 'files' => [], 'log' => [], 'status' => 'Черновик', 'created' => ['at' => crm_now(), 'by' => $user]];
    }
    $n = $str('n', 20);
    if ($n === '') $n = $di >= 0 ? $doc['n'] : crm_doc_next_number($D, $type, $date);
    $parent = $str('parent', 20);
    if ($parent !== '' && crm_doc_find($D, $parent) < 0) $parent = '';
    $doc = array_merge($doc, [
        'type' => $type, 'n' => $n, 'date' => $date, 'lead_id' => $lead['id'], 'parent' => $parent,
        'title' => $str('title', 2000), 'basis' => $str('basis', 400), 'period' => $str('period', 200),
        'due' => $str('due', 20), 'prepay' => $str('prepay', 3), 'note' => $str('note', 4000),
        'items' => $items, 'monthly' => $monthly, 'total' => round($total, 2), 'monthly_total' => round($mtotal, 2),
        'company' => crm_company(), 'party' => $party, 'updated' => crm_now(),
    ]);
    if ($di >= 0) $D['docs'][$di] = $doc; else $D['docs'][] = $doc;
    if (!crm_docs_write($D)) { http_response_code(500); exit(json_encode(['error' => 'write'])); }
    if ($di < 0) {
        $data['leads'][$li]['comments'][] = ['at' => crm_now(), 'who' => $user, 'kind' => 'doc',
            'text' => $types[$type] . ' № ' . $n . ' от ' . $date . ($total ? ' на ' . crm_money($total) . ' ₽' : '') .
                      ($mtotal ? ($total ? ', ' : ' — ') . 'ежемесячно ' . crm_money($mtotal) . ' ₽' : '') . ' — создан, черновик'];
        $data['leads'][$li]['updated'] = crm_now();
    }
    $out['doc'] = $doc; $out['docs'] = $D['docs']; $out['comments'] = $data['leads'][$li]['comments'];

} elseif ($action === 'doc_status') {
    $D = crm_docs(); $di = crm_doc_find($D, (string)($_POST['id'] ?? ''));
    $st = (string)($_POST['status'] ?? '');
    if ($di < 0 || !in_array($st, crm_doc_statuses($D['docs'][$di]['type']), true)) { http_response_code(422); exit(json_encode(['error' => 'bad'])); }
    $doc = &$D['docs'][$di]; $was = $doc['status']; $li = crm_find($data, $doc['lead_id']);
    if ($was !== $st) {
        $doc['status'] = $st; $doc['updated'] = crm_now();
        $doc['log'][] = ['at' => crm_now(), 'by' => $user, 'status' => $st];
        if (!crm_docs_write($D)) { http_response_code(500); exit(json_encode(['error' => 'write'])); }
        if ($li >= 0) {
            $data['leads'][$li]['comments'][] = ['at' => crm_now(), 'who' => $user, 'kind' => 'doc',
                'text' => crm_doc_types()[$doc['type']] . ' № ' . $doc['n'] . ' от ' . $doc['date'] . ': ' . $was . ' → ' . $st];
            $data['leads'][$li]['updated'] = crm_now();
        }
    }
    $out['doc'] = $doc; $out['docs'] = $D['docs'];
    if ($li >= 0) $out['comments'] = $data['leads'][$li]['comments'];
    unset($doc);

} elseif ($action === 'doc_delete') {
    $D = crm_docs(); $di = crm_doc_find($D, (string)($_POST['id'] ?? ''));
    if ($di < 0) { http_response_code(422); exit(json_encode(['error' => 'bad'])); }
    if ($D['docs'][$di]['status'] !== 'Черновик') { http_response_code(422); exit(json_encode(['error' => 'Удалять можно только черновики. Ненужный документ переведите в «Отменён».'])); }
    foreach ($D['docs'][$di]['files'] ?? [] as $f) @unlink(crm_files_dir() . '/' . basename($f['stored']));
    array_splice($D['docs'], $di, 1);
    if (!crm_docs_write($D)) { http_response_code(500); exit(json_encode(['error' => 'write'])); }
    exit(json_encode(['ok' => true, 'docs' => $D['docs']], JSON_UNESCAPED_UNICODE));

} elseif ($action === 'doc_file') {
    /* Скан подписанного документа. Кладём вне веб-корня под случайным именем, оригинальное имя — в записи. */
    $D = crm_docs(); $di = crm_doc_find($D, (string)($_POST['id'] ?? ''));
    $f = $_FILES['file'] ?? null;
    if ($di < 0 || !$f || ($f['error'] ?? 1) !== UPLOAD_ERR_OK) { http_response_code(422); exit(json_encode(['error' => 'Файл не получен'])); }
    if ($f['size'] > 15 * 1024 * 1024) { http_response_code(422); exit(json_encode(['error' => 'Файл больше 15 МБ'])); }
    $ext = strtolower(pathinfo($f['name'], PATHINFO_EXTENSION));
    if (!in_array($ext, ['pdf', 'jpg', 'jpeg', 'png', 'docx', 'xlsx'], true)) { http_response_code(422); exit(json_encode(['error' => 'Можно PDF, JPG, PNG, DOCX, XLSX'])); }
    $stored = $D['docs'][$di]['id'] . '-' . bin2hex(random_bytes(6)) . '.' . $ext;
    if (!move_uploaded_file($f['tmp_name'], crm_files_dir() . '/' . $stored)) { http_response_code(500); exit(json_encode(['error' => 'Не удалось сохранить файл'])); }
    $D['docs'][$di]['files'][] = ['name' => mb_substr(preg_replace('/[\/\\\\:*?"<>|]+/', '_', $f['name']), 0, 120), 'stored' => $stored,
                                  'size' => (int)$f['size'], 'at' => crm_now(), 'by' => $user];
    $D['docs'][$di]['updated'] = crm_now();
    if (!crm_docs_write($D)) { http_response_code(500); exit(json_encode(['error' => 'write'])); }
    exit(json_encode(['ok' => true, 'doc' => $D['docs'][$di], 'docs' => $D['docs']], JSON_UNESCAPED_UNICODE));

} elseif ($action === 'doc_file_del') {
    $D = crm_docs(); $di = crm_doc_find($D, (string)($_POST['id'] ?? '')); $k = (int)($_POST['i'] ?? -1);
    if ($di < 0 || !isset($D['docs'][$di]['files'][$k])) { http_response_code(422); exit(json_encode(['error' => 'bad'])); }
    @unlink(crm_files_dir() . '/' . basename($D['docs'][$di]['files'][$k]['stored']));
    array_splice($D['docs'][$di]['files'], $k, 1);
    $D['docs'][$di]['updated'] = crm_now();
    if (!crm_docs_write($D)) { http_response_code(500); exit(json_encode(['error' => 'write'])); }
    exit(json_encode(['ok' => true, 'doc' => $D['docs'][$di], 'docs' => $D['docs']], JSON_UNESCAPED_UNICODE));

} elseif ($action === 'company_file') {
    $kind = ($_POST['kind'] ?? '') === 'stamp' ? 'stamp' : 'sign';
    $f = $_FILES['file'] ?? null;
    if (!$f || ($f['error'] ?? 1) !== UPLOAD_ERR_OK) { http_response_code(422); exit(json_encode(['error' => 'Файл не получен'])); }
    if ($f['size'] > 3 * 1024 * 1024) { http_response_code(422); exit(json_encode(['error' => 'Файл больше 3 МБ'])); }
    $ext = strtolower(pathinfo($f['name'], PATHINFO_EXTENSION));
    if (!in_array($ext, ['png', 'jpg', 'jpeg'], true)) { http_response_code(422); exit(json_encode(['error' => 'Нужен PNG или JPG'])); }
    if (!@getimagesize($f['tmp_name'])) { http_response_code(422); exit(json_encode(['error' => 'Это не картинка'])); }
    $old = crm_company_file($kind); if ($old) @unlink($old);
    if (!move_uploaded_file($f['tmp_name'], crm_files_dir() . '/company-' . $kind . '.' . $ext)) { http_response_code(500); exit(json_encode(['error' => 'Не удалось сохранить'])); }
    exit(json_encode(['ok' => true, 'kind' => $kind, 'has' => true]));

} elseif ($action === 'company_file_del') {
    $kind = ($_POST['kind'] ?? '') === 'stamp' ? 'stamp' : 'sign';
    $old = crm_company_file($kind); if ($old) @unlink($old);
    exit(json_encode(['ok' => true, 'kind' => $kind, 'has' => false]));

} elseif ($action === 'doc_month') {
    /* Счёт или акт за месяц по ежемесячным услугам спецификации. */
    $D = crm_docs(); $di = crm_doc_find($D, (string)($_POST['id'] ?? ''));
    $kind = ($_POST['kind'] ?? 'invoice') === 'act' ? 'act' : 'invoice';
    if ($di < 0 || $D['docs'][$di]['type'] !== 'spec' || empty($D['docs'][$di]['monthly'])) { http_response_code(422); exit(json_encode(['error' => 'В спецификации нет ежемесячных услуг'])); }
    if (!preg_match('/^(\d{4})-(\d\d)$/', (string)($_POST['month'] ?? ''), $m)) { http_response_code(422); exit(json_encode(['error' => 'Месяц в виде ГГГГ-ММ'])); }
    $names = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
    $nom   = ['январь', 'февраль', 'март', 'апрель', 'май', 'июнь', 'июль', 'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'];
    $mi = (int)$m[2]; if ($mi < 1 || $mi > 12) { http_response_code(422); exit(json_encode(['error' => 'month'])); }
    $spec = $D['docs'][$di]; $par = null; if ($spec['parent']) { $pi = crm_doc_find($D, $spec['parent']); if ($pi >= 0) $par = $D['docs'][$pi]; }
    $period = $nom[$mi - 1] . ' ' . $m[1];
    $items = []; $total = 0;
    foreach ($spec['monthly'] as $it) { $items[] = ['name' => $it['name'] . ' за ' . $period, 'qty' => 1, 'unit' => 'мес', 'price' => $it['price']]; $total += $it['price']; }
    $max = 0; foreach ($D['docs'] as $d) $max = max($max, (int)substr($d['id'], 1));
    $date = $kind === 'invoice' ? date('d.m.Y') : date('t.m.Y', mktime(0, 0, 0, $mi, 1, (int)$m[1]));
    $doc = ['id' => 'd' . ($max + 1), 'type' => $kind, 'n' => crm_doc_next_number($D, $kind, $date), 'date' => $date,
        'lead_id' => $spec['lead_id'], 'parent' => $spec['parent'], 'title' => '',
        'basis' => ($par ? 'Договор № ' . $par['n'] . ' от ' . $par['date'] . ', ' : '') . 'спецификация № ' . $spec['n'] . ' от ' . $spec['date'],
        'period' => $period, 'due' => $kind === 'invoice' ? '05.' . $m[2] . '.' . $m[1] : '', 'prepay' => '', 'note' => '',
        'items' => $items, 'monthly' => [], 'total' => round($total, 2), 'monthly_total' => 0,
        'company' => crm_company(), 'party' => $spec['party'], 'files' => [], 'log' => [], 'status' => 'Черновик',
        'created' => ['at' => crm_now(), 'by' => $user], 'updated' => crm_now()];
    $D['docs'][] = $doc;
    if (!crm_docs_write($D)) { http_response_code(500); exit(json_encode(['error' => 'write'])); }
    $li = crm_find($data, $doc['lead_id']);
    if ($li >= 0) {
        $data['leads'][$li]['comments'][] = ['at' => crm_now(), 'who' => $user, 'kind' => 'doc',
            'text' => crm_doc_types()[$kind] . ' № ' . $doc['n'] . ' за ' . $period . ' на ' . crm_money($total) . ' ₽ — создан, черновик'];
        $out['comments'] = $data['leads'][$li]['comments'];
    }
    $out['doc'] = $doc; $out['docs'] = $D['docs'];

} else {
    http_response_code(400); exit(json_encode(['error' => 'action']));
}

if (!crm_write($data)) { http_response_code(500); exit(json_encode(['error' => 'write'])); }
echo json_encode($out, JSON_UNESCAPED_UNICODE);
