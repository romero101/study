<?php
/* Скан подписанного документа: /admin/file.php?d=d1&i=0. Файлы лежат вне веб-корня, отдаём только вошедшим. */
require __DIR__ . '/lib.php';
crm_boot();
if (!crm_logged_in() || crm_must_change()) { http_response_code(401); exit('Нужен вход'); }
$D = crm_docs();
$i = crm_doc_find($D, (string)($_GET['d'] ?? ''));
$k = (int)($_GET['i'] ?? -1);
$f = $i >= 0 ? ($D['docs'][$i]['files'][$k] ?? null) : null;
$path = $f ? crm_files_dir() . '/' . basename($f['stored']) : '';
if (!$f || !is_file($path)) { http_response_code(404); exit('Файл не найден'); }
$ext = strtolower(pathinfo($f['name'], PATHINFO_EXTENSION));
$mime = ['pdf' => 'application/pdf', 'jpg' => 'image/jpeg', 'jpeg' => 'image/jpeg', 'png' => 'image/png',
         'docx' => 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
         'xlsx' => 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'][$ext] ?? 'application/octet-stream';
header('Content-Type: ' . $mime);
header('Content-Length: ' . filesize($path));
header('X-Content-Type-Options: nosniff');
header('Content-Disposition: ' . (in_array($ext, ['pdf', 'jpg', 'jpeg', 'png']) && empty($_GET['dl']) ? 'inline' : 'attachment') .
       "; filename*=UTF-8''" . rawurlencode($f['name']));
readfile($path);
