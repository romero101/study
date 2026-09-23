<?php
/* index.php вложенной страницы (project/, terms/): общая проверка входа лежит уровнем выше */
require dirname(__DIR__) . '/gate.php';
etalon_gate();
readfile(__DIR__ . '/page.html');
