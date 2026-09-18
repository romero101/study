/* Клиентская часть админки: фильтры, карточка сделки, автосохранение. */
"use strict";

var STAGES = DATA.stages, LEADS = DATA.leads;
var filter = null, query = "", current = null;

/* цвет этапа: от «холодного» к «оплачено», отказ — красный */
var COLORS = ["#8a96a3", "#3b82c4", "#2f6fb5", "#7c5cc4", "#c98a12", "#2f9e52", "#c02b1d"];
function stageColor(s) { var i = STAGES.indexOf(s); return COLORS[i] || "#8a96a3"; }

/* быстрые комментарии под нашу воронку — чтобы не печатать руками */
var QUICK = [
  "Дозвонился до ЛПР, договорились созвониться повторно",
  "Отправил ссылку на демо, ждём обратную связь",
  "Взял обратную связь: правки по тексту и ценам",
  "Не дозвонился, перезвонить завтра",
  "Согласовали состав работ, готовлю счёт",
  "Отказ: делают своими силами",
];

function money(n) { return n ? new Intl.NumberFormat("ru-RU").format(n) + " ₽" : "—"; }
function esc(s) { var d = document.createElement("div"); d.textContent = s == null ? "" : s; return d.innerHTML; }
function last(l) {
  var c = l.comments || [];
  return c.length ? c[c.length - 1] : null;
}

/* --------------------------------------------------------------- воронка */
function drawFunnel() {
  var el = document.getElementById("funnel");
  el.innerHTML = STAGES.map(function (s) {
    var inSt = LEADS.filter(function (l) { return l.stage === s; });
    var sum = inSt.reduce(function (a, l) { return a + (+l.offer || 0); }, 0);
    return '<button class="fst" data-s="' + esc(s) + '" aria-pressed="' + (filter === s) + '">' +
      '<i><span class="dot" style="background:' + stageColor(s) + '"></span>' + esc(s) + "</i>" +
      "<b>" + inSt.length + "</b><s>" + money(sum) + "</s></button>";
  }).join("");
}

/* --------------------------------------------------------------- таблица */
function visible() {
  var q = query.trim().toLowerCase();
  return LEADS.filter(function (l) {
    if (filter && l.stage !== filter) return false;
    if (!q) return true;
    var hay = [l.company, l.city, l.contacts, l.was_url, l.now_url,
      l.was_problems, l.now_done, l.left_todo]
      .concat((l.comments || []).map(function (c) { return c.text; })).join(" ").toLowerCase();
    return hay.indexOf(q) > -1;
  });
}

function psClass(v) { return v == null ? "" : v < 50 ? "ps--bad" : v < 80 ? "ps--mid" : "ps--ok"; }

function drawRows() {
  var rows = visible();
  document.getElementById("empty").hidden = rows.length > 0;
  document.getElementById("rows").innerHTML = rows.map(function (l) {
    var c = last(l);
    return '<tr data-id="' + l.id + '">' +
      '<td class="num">' + esc(l.n) + "</td>" +
      '<td class="co">' + esc(l.company) + (l.source === "site" ? '<span class="src">с сайта</span>' : "") +
        "<s>" + esc(l.city) + "</s></td>" +
      "<td><span class=\"pill\" style=\"background:" + stageColor(l.stage) + "22;color:" +
        stageColor(l.stage) + '">' + esc(l.stage) + "</span></td>" +
      '<td class="mini">' + (l.was_url ? '<a href="' + esc(l.was_url) + '" target="_blank" rel="noopener">'
        + esc(l.was_url.replace(/^https?:\/\//, "").replace(/\/$/, "")) + "</a>" : "—") + "</td>" +
      '<td class="mini">' + (l.now_url ? '<a href="' + esc(l.now_url) + '" target="_blank" rel="noopener">'
        + esc(l.now_url.replace(/^https?:\/\//, "").replace(/\/$/, "")) + "</a>"
        : '<span style="color:#b0bbc6">не собран</span>') + "</td>" +
      '<td class="num ps ' + psClass(l.pagespeed) + '">' + (l.pagespeed == null ? "—" : l.pagespeed) + "</td>" +
      '<td class="num">' + money(+l.offer) + "</td>" +
      '<td class="mini">' + (c ? esc(c.at) + " · " + esc(c.text.slice(0, 60)) : "—") + "</td>" +
      "</tr>";
  }).join("");
}

/* --------------------------------------------------------------- карточка */
var dlg = document.getElementById("dlg");

function drawLog(l) {
  var c = l.comments || [];
  document.getElementById("d-log").innerHTML = c.length ? c.slice().reverse().map(function (x) {
    return '<div class="note' + (x.kind === "stage" ? " note--stage" : "") + '">' +
      '<div class="av">' + esc((x.who || "?").slice(0, 2).toUpperCase()) + "</div>" +
      '<div class="tx"><b>' + esc(x.who) + "</b><s>" + esc(x.at) + "</s>" +
      "<p>" + esc(x.text) + "</p></div></div>";
  }).join("") : '<div class="mini" style="padding:10px 0">Пока пусто. Первый комментарий — после звонка.</div>';
}

/* ---------------------------------------------------------- скрипт звонка */
function scList(title, items) {
  return items && items.length ? "<h4>" + title + "</h4><ul>" + items.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + "</ul>" : "";
}
function scSay(title, text) { return text ? "<h4>" + title + '</h4><div class="say">' + esc(text) + "</div>" : ""; }
function scObj(list, own) {
  return list.map(function (o) {
    return "<details" + (own ? ' class="own"' : "") + "><summary>" + esc(o.q) + '</summary><div class="say">' + esc(o.a) + "</div></details>";
  }).join("");
}
function drawScript(l) {
  var C = SCRIPTS.common, S = SCRIPTS.leads[l.id] || (l.source === "site" ? C.inbound : null);
  var hasDemo = /formasaita\.ru/.test(l.now_url || ""), html = '<div class="sc">';
  document.getElementById("d-script-goal").textContent = S ? S.goal : "Индивидуального скрипта нет — общие правила и возражения";
  var K = C.core;
  html += '<h4 style="margin-top:4px">' + esc(K.title) + "</h4>" + '<div class="say">' + esc(K.pitch) + "</div>" +
    '<details><summary>Арифметика: сколько заявок теряется</summary><div class="say">' + esc(K.math) + "</div></details>" +
    scList("Проверить до звонка", K.check) + scList("Спросить про рекламу", K.ask);
  if (S) {
    if (S.caution) html += '<p class="warn2"><b>Осторожно:</b> ' + esc(S.caution) + "</p>";
    html += scSay("Начало разговора", S.opener) + scList("Факты о сайте — перепроверить перед звонком", S.hook) +
      (S.show ? "<h4>Что показываем и обещаем</h4><p>" + esc(S.show) + "</p>" : "") +
      scList("Вопросы клиенту", S.questions);
  }
  html += scSay(C.gatekeeper.title, C.gatekeeper.text) + "<h4>Цена</h4><p>" + esc(C.price) + "</p>";
  var own = (S && S.objections ? S.objections : []).concat(hasDemo ? [C.demo_objection] : []);
  if (own.length) html += "<h4>Возражения именно этого клиента</h4>" + scObj(own, true);
  html += "<h4>Частые возражения</h4>" + scObj(C.objections, false);
  if (S && S.next) html += "<h4>Чем закончить звонок</h4><p>" + esc(S.next) + "</p>";
  html += scList("Правила", C.rules) + "</div>";
  document.getElementById("d-script").innerHTML = html;
  document.getElementById("d-script-box").open = false;
}

function open(id) {
  var l = LEADS.filter(function (x) { return x.id === id; })[0];
  if (!l) return;
  current = l;
  document.getElementById("d-co").textContent = l.company;
  document.getElementById("d-city").textContent =
    l.city + (l.n ? " · сделка №" + l.n : "") + (l.updated ? " · изменено " + l.updated : "");
  var sel = document.getElementById("d-stage");
  sel.innerHTML = STAGES.map(function (s) {
    return '<option' + (s === l.stage ? " selected" : "") + ">" + esc(s) + "</option>";
  }).join("");
  document.querySelectorAll(".ed").forEach(function (t) { t.value = l[t.dataset.f] == null ? "" : l[t.dataset.f]; });
  document.getElementById("d-quick").innerHTML = QUICK.map(function (q) {
    return "<button type=\"button\">" + esc(q) + "</button>";
  }).join("");
  drawScript(l);
  drawLog(l);
  document.getElementById("d-note").value = "";
  dlg.showModal();
}

function post(body) {
  body.csrf = CSRF;
  return fetch("api.php", {
    method: "POST",
    body: new URLSearchParams(body),
  }).then(function (r) {
    if (r.status === 401) { location.reload(); throw new Error("auth"); }
    if (!r.ok) throw new Error("http " + r.status);
    return r.json();
  });
}

function flash() {
  var s = document.getElementById("d-saved");
  s.classList.add("on");
  clearTimeout(flash.t);
  flash.t = setTimeout(function () { s.classList.remove("on"); }, 1400);
}

/* --------------------------------------------------------------- события */
document.getElementById("funnel").addEventListener("click", function (e) {
  var b = e.target.closest(".fst"); if (!b) return;
  filter = filter === b.dataset.s ? null : b.dataset.s;
  drawFunnel(); drawRows();
});

document.getElementById("q").addEventListener("input", function (e) {
  query = e.target.value; drawRows();
});

document.getElementById("rows").addEventListener("click", function (e) {
  if (e.target.closest("a")) return;            // ссылку открываем, карточку не трогаем
  var tr = e.target.closest("tr"); if (tr) open(tr.dataset.id);
});

document.getElementById("d-x").addEventListener("click", function () { dlg.close(); });
dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });

document.getElementById("d-stage").addEventListener("change", function (e) {
  var stage = e.target.value;
  post({ action: "stage", id: current.id, stage: stage }).then(function (r) {
    current.stage = stage;
    current.comments = r.comments || current.comments;
    drawLog(current); drawFunnel(); drawRows(); flash();
  }).catch(function () { alert("Не удалось сохранить этап. Проверьте связь и повторите."); });
});

/* правки полей сохраняются сами, когда уходит фокус */
document.querySelectorAll(".ed").forEach(function (t) {
  t.addEventListener("blur", function () {
    if (!current) return;
    var f = t.dataset.f, v = t.value;
    if (String(current[f] == null ? "" : current[f]) === v) return;
    post({ action: "field", id: current.id, field: f, value: v }).then(function () {
      current[f] = f === "offer" ? +v.replace(/\D+/g, "") : v;
      drawRows(); flash();
    }).catch(function () { alert("Правка не сохранилась, повторите."); });
  });
});

document.getElementById("d-quick").addEventListener("click", function (e) {
  var b = e.target.closest("button"); if (!b) return;
  var n = document.getElementById("d-note");
  n.value = (n.value ? n.value + "\n" : "") + b.textContent;
  n.focus();
});

document.getElementById("d-send").addEventListener("click", function () {
  var n = document.getElementById("d-note"), text = n.value.trim();
  if (!text || !current) return;
  var btn = this; btn.disabled = true;
  post({ action: "comment", id: current.id, text: text }).then(function (r) {
    current.comments = r.comments;
    n.value = ""; drawLog(current); drawRows(); flash();
  }).catch(function () { alert("Комментарий не сохранился, повторите."); })
    .then(function () { btn.disabled = false; });
});

document.getElementById("add").addEventListener("click", function () {
  var company = prompt("Название компании");
  if (!company) return;
  var city = prompt("Город") || "";
  var url = prompt("Действующий сайт (можно пропустить)") || "";
  post({ action: "create", company: company, city: city, was_url: url, offer: "60000" })
    .then(function (r) { LEADS.push(r.lead); drawFunnel(); drawRows(); open(r.lead.id); })
    .catch(function () { alert("Не удалось создать сделку."); });
});

drawFunnel();
drawRows();
