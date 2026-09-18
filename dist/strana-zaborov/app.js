'use strict';
/* Страна Заборов: калькулятор, подбор забора, цвет, галерея, заявки. Без библиотек. */
const DEMO = true, WA = '79524477974', opened = Date.now();
const $ = id => document.getElementById(id);
const money = n => new Intl.NumberFormat('ru-RU').format(n);

/* Цены «от» за погонный метр — с прайса на сайте компании. null = считают по смете. */
const TYPES = {
  prof: {name: 'Профнастил', rate: 1900},
  evro: {name: 'Евроштакетник', rate: 2100},
  rab: {name: 'Сетка-рабица', rate: 1150},
  pvh: {name: 'Сетка ПВХ', rate: 1350},
  d3: {name: '3D-панели', rate: null},
};
const GIFTS = [[150, 'распашные ворота и мангал'], [100, 'калитка с врезным замком'], [50, 'калитка']];
const COLORS = [['8017', 'шоколад', '#45322e'], ['6005', 'зелёный мох', '#2f4538'], ['7024', 'графит', '#474a51'], ['5005', 'синий', '#1e4d8c'],
  ['5024', 'пастельно-синий', '#5d8aa8'], ['9003', 'белый', '#f1f1ee'], ['9006', 'серебристый', '#a5a8a6'], ['7004', 'серый', '#969992'],
  ['6002', 'зелёный лист', '#2d572c'], ['5021', 'морская волна', '#256d7b'], ['5002', 'ультрамарин', '#20214f'], ['6020', 'хвойный', '#2e3a23']]
let color = COLORS[0], mode = 'calc';

/* ---------------------------------------------------------------- калькулятор */
const val = name => document.querySelector(`input[name=${name}]:checked`).value;
function state() {
  const type = val('type'), len = Math.round(Number($('len').value));
  return {type, t: TYPES[type], len, valid: len >= 5 && len <= 400, height: val('height'),
    extras: [['x-gate', 'Калитка'], ['x-doors', 'Ворота'], ['x-demo', 'Демонтаж старого забора']].filter(x => $(x[0]).checked).map(x => x[1])};
}
function giftFor(len) { return GIFTS.find(g => len >= g[0]); }

function drawFence(type) {
  const c = color[2], dark = 'rgba(0,0,0,.22)', svg = $('fence-svg');
  let s = '';
  for (let x = 0; x <= 320; x += 80) s += `<rect x="${x - 3}" y="14" width="6" height="66" fill="#3a3f3c"/>`;
  if (type === 'prof') {
    s += `<rect x="0" y="18" width="320" height="58" fill="${c}"/>`;
    for (let x = 0; x < 320; x += 10) s += `<rect x="${x}" y="18" width="3" height="58" fill="${dark}"/>`;
  } else if (type === 'evro') {
    s += `<rect x="0" y="30" width="320" height="4" fill="#3a3f3c"/><rect x="0" y="62" width="320" height="4" fill="#3a3f3c"/>`;
    for (let x = 2; x < 320; x += 13) s += `<path d="M${x} 78V22l4.5-5 4.5 5v56z" fill="${c}"/>`;
  } else {
    const step = type === 'd3' ? 12 : 9;
    s += `<g stroke="${c}" stroke-width="${type === 'd3' ? 1.6 : 1.1}" fill="none">`;
    if (type === 'd3') { for (let x = 0; x <= 320; x += step) s += `<path d="M${x} 18v58"/>`; for (let y = 18; y <= 76; y += 14.5) s += `<path d="M0 ${y}h320"/>`; }
    else for (let x = -80; x <= 320; x += step) s += `<path d="M${x} 76l58-58M${x + 58} 76l-58-58"/>`;
    s += '</g>';
  }
  svg.innerHTML = s;
}

function summary() {
  const s = state(), lines = [`Забор: ${s.t.name}, ${s.len} м, высота ${s.height}`, `Цвет: RAL ${color[0]} (${color[1]})`];
  if (s.extras.length) lines.push('Дополнительно: ' + s.extras.join(', '));
  lines.push(s.t.rate ? `Предварительно: от ${money(s.len * s.t.rate)} ₽ (по прайсу «от ${money(s.t.rate)} ₽/п.м.»)` : 'Цена: по смете после замера');
  const g = giftFor(s.len); if (g) lines.push('Подарок за метраж: ' + g[1]);
  if (quiz.done) lines.push('', 'Из подбора: ' + quiz.keys.map(k => answers[k]).filter(Boolean).join('; '));
  return lines.join('\n');
}

function update() {
  const s = state();
  $('len-range').value = Math.min(400, Math.max(5, s.len || 5));
  drawFence(s.type);
  $('out-label').textContent = (mode === 'quiz' && !quiz.done) ? 'ПОДБОР ЗАБОРА' : 'ПРЕДВАРИТЕЛЬНО · ' + s.t.name.toUpperCase();
  if (!s.valid) { $('out-price').textContent = 'Укажите длину'; $('out-formula').textContent = 'От 5 до 400 метров. Больше — позвоните, посчитаем отдельно.'; $('gift').textContent = ''; $('out-list').replaceChildren(); return; }
  $('out-price').textContent = s.t.rate ? `от ${money(s.len * s.t.rate)} ₽` : 'По смете';
  $('out-formula').textContent = s.t.rate ? `${s.len} м × от ${money(s.t.rate)} ₽ за метр с монтажом` : '3D-панели считаем по толщине прутка и высоте — смета после замера, бесплатно.';
  const g = giftFor(s.len), next = [...GIFTS].reverse().find(x => x[0] > s.len), gift = $('gift');
  gift.className = 'gift' + (g ? ' on' : '');
  gift.textContent = (g ? `🎁 В подарок: ${g[1]}. ` : '') + (next && next[0] - s.len <= 25 ? `Ещё ${next[0] - s.len} м — и в подарок ${next[1]}.` : '');
  const rows = [['Столбы, шаг 2,5 м', `≈ ${Math.ceil(s.len / 2.5) + 1} шт`], ['Замер и смета', 'бесплатно'], ['Предоплата', 'не нужна']].concat(s.extras.map(e => [e, 'в смете']));
  $('out-list').replaceChildren(...rows.map(r => { const li = document.createElement('li'), b = document.createElement('b'); li.textContent = r[0]; b.textContent = r[1]; li.append(b); return li; }));
  const text = 'Здравствуйте! Посчитал забор на сайте:\n' + summary();
  $('wa-link').href = $('bar-wa').href = `https://wa.me/${WA}?text=${encodeURIComponent(text)}`;
}

$('len').addEventListener('input', update);
$('len-range').addEventListener('input', () => { $('len').value = $('len-range').value; update(); });
document.querySelectorAll('#panel-calc input[type=radio],#panel-calc input[type=checkbox]').forEach(i => i.addEventListener('change', update));

/* длина по соткам: периметр квадратного участка */
function plot() { const a = Math.min(100, Math.max(1, Number($('sotki').value) || 0)), p = Math.round(4 * Math.sqrt(a * 100)); $('len').value = p; $('plot-hint').textContent = `Квадратный участок ${a} сот. — около ${p} м по периметру. Если часть уже огорожена соседями, уменьшите длину.`; update(); }
$('plot-help').addEventListener('click', () => { $('plot-box').hidden = !$('plot-box').hidden; if (!$('plot-box').hidden) { plot(); $('sotki').focus(); } });
$('sotki').addEventListener('input', plot);

/* цвет */
$('swatches').replaceChildren(...COLORS.map(c => { const b = document.createElement('button'); b.type = 'button'; b.style.background = c[2]; b.setAttribute('role', 'radio'); b.setAttribute('aria-label', `RAL ${c[0]}, ${c[1]}`); b.setAttribute('aria-checked', String(c === color));
  b.addEventListener('click', () => { color = c; document.querySelectorAll('#swatches button').forEach(x => x.setAttribute('aria-checked', String(x === b))); $('color-name').textContent = `RAL ${c[0]} · ${c[1]}`; update(); }); return b; }));

function pick(type) { document.querySelector(`input[name=type][value=${type}]`).checked = true; setMode('calc'); update(); $('calc').scrollIntoView({behavior: 'smooth'}); }
document.querySelectorAll('[data-pick]').forEach(b => b.addEventListener('click', () => pick(b.dataset.pick)));

/* ---------------------------------------------------------------- подбор забора */
const answers = {}, quiz = {step: 0, done: false, keys: ['goal', 'place', 'size', 'entry']};
const QUESTIONS = [
  {key: 'goal', title: 'Что важнее всего?', options: [['Закрыться от улицы и соседей', 'глухой забор', 'prof'], ['Красиво и чтобы продувалось', 'как деревянный, но металл', 'evro'], ['Обозначить границу недорого', 'дача, огород', 'rab'], ['Современно и чтобы участок просматривался', 'дом, территория, парковка', 'd3']]},
  {key: 'place', title: 'Где будет забор?', options: [['Дача или СНТ'], ['Частный дом'], ['Организация, склад, площадка']]},
  {key: 'size', title: 'Какой примерно периметр?', options: [['До 50 м', '', 30], ['50–100 м', 'от 50 м — калитка в подарок', 70], ['100–150 м', 'калитка с замком в подарок', 120], ['Больше 150 м', 'ворота и мангал в подарок', 170], ['Не знаю — нужен замер', '', 60]]},
  {key: 'entry', title: 'Въезд и вход нужны?', options: [['Калитка и ворота', '', 'gd'], ['Только калитка', '', 'g'], ['Уже есть / не нужны', '', '']]},
];
function renderQuiz() {
  const q = QUESTIONS[quiz.step], body = $('quiz-body');
  $('quiz-step').textContent = `Вопрос ${quiz.step + 1} из ${QUESTIONS.length}`;
  $('quiz-fill').style.width = `${(quiz.step + 1) / QUESTIONS.length * 100}%`;
  $('quiz-back').hidden = quiz.step === 0; $('quiz-error').textContent = '';
  $('quiz-next').textContent = quiz.step === QUESTIONS.length - 1 ? 'Показать подбор →' : 'Далее →';
  const h = document.createElement('h3'); h.textContent = q.title;
  const box = document.createElement('div'); box.className = 'quiz-options'; box.setAttribute('role', 'radiogroup'); box.setAttribute('aria-label', q.title);
  q.options.forEach(o => { const l = document.createElement('label'), i = document.createElement('input'), s = document.createElement('span'); l.className = 'quiz-choice'; i.type = 'radio'; i.name = q.key; i.value = o[0]; i.checked = answers[q.key] === o[0]; s.textContent = o[0];
    if (o[1]) { const sm = document.createElement('small'); sm.textContent = o[1]; s.append(sm); } l.append(i, s); box.append(l); });
  body.replaceChildren(h, box);
}
$('quiz-form').addEventListener('submit', e => {
  e.preventDefault();
  const q = QUESTIONS[quiz.step], chosen = document.querySelector(`#quiz-body input[name=${q.key}]:checked`);
  if (!chosen) { $('quiz-error').textContent = 'Выберите вариант, чтобы продолжить.'; return; }
  answers[q.key] = chosen.value;
  if (quiz.step < QUESTIONS.length - 1) { quiz.step++; renderQuiz(); return; }
  const opt = (k, v) => QUESTIONS.find(x => x.key === k).options.find(o => o[0] === v);
  document.querySelector(`input[name=type][value=${opt('goal', answers.goal)[2]}]`).checked = true;
  $('len').value = opt('size', answers.size)[2];
  const entry = opt('entry', answers.entry)[2]; $('x-gate').checked = entry.includes('g'); $('x-doors').checked = entry.includes('d');
  quiz.done = true; goal('quiz'); setMode('calc'); update();
  $('calc').scrollIntoView({behavior: 'smooth'});
});
$('quiz-back').addEventListener('click', () => { quiz.step = Math.max(0, quiz.step - 1); renderQuiz(); });
function setMode(next) { mode = next; for (const t of ['calc', 'quiz']) { $(`tab-${t}`).setAttribute('aria-selected', String(t === mode)); $(`tab-${t}`).tabIndex = t === mode ? 0 : -1; $(`panel-${t}`).hidden = t !== mode; } if (mode === 'quiz') renderQuiz(); update(); }
['calc', 'quiz'].forEach(t => $(`tab-${t}`).addEventListener('click', () => setMode(t)));
document.querySelectorAll('[data-start-quiz]').forEach(b => b.addEventListener('click', () => { quiz.step = 0; setMode('quiz'); $('calc').scrollIntoView({behavior: 'smooth'}); }));

/* ---------------------------------------------------------------- галерея */
const SHOTS = [['prof-09', 'prof'], ['evro-13', 'evro'], ['d3-07', 'd3'], ['prof-18', 'prof'], ['evro-16', 'evro'], ['prof-05', 'prof'], ['evro-04', 'evro'], ['d3-06', 'd3'],
  ['prof-01', 'prof'], ['evro-09', 'evro'], ['rab-07', 'rab'], ['prof-14', 'prof'], ['evro-19', 'evro'], ['d3-02', 'd3'], ['prof-19', 'prof'], ['rab-01', 'rab']];
$('gallery').replaceChildren(...SHOTS.map(([file, type]) => { const b = document.createElement('button'), img = document.createElement('img'), tag = document.createElement('span');
  b.className = 'shot'; b.type = 'button'; b.dataset.type = type; b.setAttribute('aria-label', `Увеличить фото: ${TYPES[type].name}`);
  img.loading = 'lazy'; img.decoding = 'async'; img.alt = `${TYPES[type].name} — работа «Страны Заборов»`; img.width = 640; img.height = 480;
  img.srcset = `img/${file}-640.webp 640w, img/${file}-1280.webp 1280w`; img.sizes = '(max-width:760px) 50vw, 25vw'; img.src = `img/${file}-640.webp`;
  tag.textContent = TYPES[type].name; b.append(img, tag);
  b.addEventListener('click', () => { $('photo-large').src = `img/${file}-1280.webp`; $('photo-large').alt = img.alt; $('photo-caption').textContent = `${TYPES[type].name} · фото компании`; $('photo-dialog').showModal(); }); return b; }));
document.querySelectorAll('[data-filter]').forEach(f => f.addEventListener('click', () => { document.querySelectorAll('[data-filter]').forEach(x => x.setAttribute('aria-selected', String(x === f)));
  document.querySelectorAll('.shot').forEach(s => { s.hidden = f.dataset.filter !== 'all' && s.dataset.type !== f.dataset.filter; }); }));

/* ---------------------------------------------------------------- заявки */
function goal(name) { try { if (window.ym && window.YM_ID) ym(window.YM_ID, 'reachGoal', name); } catch {} }
document.querySelectorAll('[data-goal]').forEach(a => a.addEventListener('click', () => goal(a.dataset.goal)));
function formatPhone(v) { let d = v.replace(/\D/g, ''); if (!d) return ''; if (d[0] === '8') d = '7' + d.slice(1); if (d[0] !== '7') d = '7' + d; d = d.slice(0, 11); let s = '+7'; if (d.length > 1) s += ' (' + d.slice(1, 4); if (d.length >= 5) s += ') ' + d.slice(4, 7); if (d.length >= 8) s += '-' + d.slice(7, 9); if (d.length >= 10) s += '-' + d.slice(9, 11); return s; }
$('phone').addEventListener('input', () => { const i = $('phone'), end = i.selectionStart === i.value.length, next = formatPhone(i.value); if (end || next.length < i.value.length) i.value = next; });
$('to-lead').addEventListener('click', () => { if (mode === 'quiz' && !quiz.done) { $('quiz-error').textContent = 'Ответьте на вопросы — или переключитесь на «Знаю, какой нужен».'; return; } $('summary').value = summary(); goal('calc'); $('request').scrollIntoView({behavior: 'smooth'}); $('phone').focus({preventScroll: true}); });

function showResult(sent, text) {
  $('lead-state').textContent = sent ? 'ЗАЯВКА ОТПРАВЛЕНА' : 'НЕ УДАЛОСЬ ОТПРАВИТЬ';
  $('lead-title').textContent = sent ? 'Спасибо! Перезвоним.' : 'Связь подвела. Позвоните нам.';
  $('lead-note').textContent = sent ? (DEMO ? 'Это демонстрация: заявку получила студия «Форма сайта», а не компания.' : 'Перезвоним в рабочее время и договоримся о замере.') : 'Заявка не ушла. Проверьте интернет и нажмите ещё раз — данные в форме сохранились. Или позвоните: +7 (952) 447-79-74.';
  $('lead-text').textContent = text; $('lead-dialog').showModal();
}
$('lead-form').addEventListener('submit', async e => {
  e.preventDefault();
  const form = e.target, err = $('form-error'), button = form.querySelector('[type=submit]');
  if (!/^7\d{10}$/.test($('phone').value.replace(/\D/g, ''))) { err.textContent = 'Введите номер полностью: +7 и 10 цифр.'; $('phone').focus(); return; }
  err.textContent = ''; if (form._gotcha.value) return;
  if (!$('summary').value.trim()) $('summary').value = summary();
  const data = new FormData(form); data.append('_Страница', location.href); data.append('_elapsed', String(Math.round((Date.now() - opened) / 1000)));
  const text = [`Телефон: ${$('phone').value}`, $('name').value.trim() && `Имя: ${$('name').value.trim()}`, $('place').value.trim() && `Участок: ${$('place').value.trim()}`, '', $('summary').value.trim()].filter(x => x !== false && x !== undefined).join('\n');
  button.disabled = true; let sent = true;
  try { const r = await fetch('send.php', {method: 'POST', body: data}), j = await r.json().catch(() => ({})); if (!r.ok || !j.ok) throw new Error(); goal('lead'); } catch { sent = false; }
  button.disabled = false; if (sent) form.reset(); showResult(sent, text);
});
document.querySelectorAll('dialog').forEach(d => { d.addEventListener('click', e => { if (e.target === d || e.target.closest('[data-close]')) d.close(); }); });
/* клавиатура телефона не должна упираться в закреплённую панель */
document.addEventListener('focusin', e => { if (e.target.matches('input:not([type=range]):not([type=checkbox]):not([type=radio]),textarea')) document.body.classList.add('kbd'); });
document.addEventListener('focusout', () => document.body.classList.remove('kbd'));
update();
