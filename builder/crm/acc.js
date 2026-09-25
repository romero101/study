/* Бухгалтерия: первичка по сделкам — договоры, спецификации, счета, акты, сканы подписанных. */
"use strict";

var accLead = "", accQ = "", curDoc = null;

function showView(v) {
  document.getElementById("v-funnel").hidden = v !== "funnel";
  document.getElementById("v-acc").hidden = v !== "acc";
  document.querySelectorAll(".tabs button").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.v === v)); });
  if (v === "acc") drawAcc();
  history.replaceState(null, "", v === "acc" ? "#acc" : location.pathname + location.search);
}
function leadOf(id) { return LEADS.filter(function (l) { return l.id === id; })[0]; }
function statuses(t) { return t === "invoice" ? DOCSTATUSES.invoice : DOCSTATUSES.other; }
function stClass(s) { return { "Оплачен": "st-ok", "Подписан": "st-ok", "Выставлен": "st-wait", "Отправлен": "st-wait", "Отменён": "st-off" }[s] || "st-draft"; }
function today() { var d = new Date(); return [d.getDate(), d.getMonth() + 1].map(function (x) { return (x < 10 ? "0" : "") + x; }).join(".") + "." + d.getFullYear(); }
function dkey(d) { var p = (d.date || "").split("."); return p.length === 3 ? p[2] + p[1] + p[0] : ""; }
function fmt(n) { return new Intl.NumberFormat("ru-RU", { minimumFractionDigits: 0, maximumFractionDigits: 2 }).format(+n || 0); }
function docSum(d) {
  if (d.type === "spec") return (d.total ? fmt(d.total) + " ₽" : "") + (d.monthly_total ? (d.total ? " + " : "") + fmt(d.monthly_total) + " ₽/мес" : "") || "—";
  return d.total ? fmt(d.total) + " ₽" : "—";
}
function docName(d) { return DOCTYPES[d.type] + " № " + d.n + " от " + d.date; }
function docWhat(d) {
  var s = (d.items || []).map(function (i) { return i.name; }).concat((d.monthly || []).map(function (i) { return i.name + " (ежемес.)"; })).join("; ");
  if (!s) s = d.type === "contract" ? "Рамочный договор на услуги" : "";
  return s.length > 110 ? s.slice(0, 108) + "…" : s;
}
function replaceDocs(list) { DOCS.length = 0; list.forEach(function (d) { DOCS.push(d); }); }

/* --------------------------------------------------------------- сводка и таблица */
function drawKpi() {
  var unpaid = DOCS.filter(function (d) { return d.type === "invoice" && d.status === "Выставлен"; });
  var us = unpaid.reduce(function (a, d) { return a + (+d.total || 0); }, 0);
  var monthly = DOCS.filter(function (d) { return d.type === "spec" && d.status === "Подписан"; }).reduce(function (a, d) { return a + (+d.monthly_total || 0); }, 0);
  var signed = DOCS.filter(function (d) { return d.type === "contract" && d.status === "Подписан"; }).length;
  var paid = DOCS.filter(function (d) { return d.type === "invoice" && d.status === "Оплачен"; }).reduce(function (a, d) { return a + (+d.total || 0); }, 0);
  document.getElementById("acc-kpi").innerHTML =
    '<div><i>Ждут оплаты</i><b>' + fmt(us) + ' ₽</b><s>' + unpaid.length + ' сч.</s></div>' +
    '<div><i>Ежемесячно по подписанным</i><b>' + fmt(monthly) + ' ₽</b><s>в месяц</s></div>' +
    '<div><i>Договоров подписано</i><b>' + signed + '</b><s>из ' + DOCS.filter(function (d) { return d.type === "contract"; }).length + '</s></div>' +
    '<div><i>Оплачено всего</i><b>' + fmt(paid) + ' ₽</b><s>по счетам</s></div>';
}
function drawCocard() {
  var c = COMPANY;
  document.getElementById("acc-cocard").innerHTML = "<b>" + esc(c.brand || "") + (c.brand ? " · " : "") + esc(c.name) + "</b>" +
    "<span>ИНН " + esc(c.inn) + "</span><span>ОГРНИП " + esc(c.ogrn) + "</span>" +
    (c.rs ? "<span>р/с …" + esc(String(c.rs).slice(-4)) + " · " + esc(c.bank) + "</span>" : '<span class="no">банк не заполнен — счёт печатается с прочерками</span>') +
    "<span>" + esc(c.tax) + "</span>";
}
function drawAcc() {
  drawCocard();
  var sel = document.getElementById("acc-lead");
  if (!sel.options.length) {
    sel.innerHTML = '<option value="">Все клиенты</option>' + LEADS.slice().sort(function (a, b) { return a.company.localeCompare(b.company, "ru"); })
      .map(function (l) { return '<option value="' + l.id + '">' + esc(l.company) + "</option>"; }).join("");
    sel.value = accLead;
  }
  drawKpi();
  var q = accQ.trim().toLowerCase();
  var rows = DOCS.filter(function (d) {
    if (accLead && d.lead_id !== accLead) return false;
    if (!q) return true;
    var l = leadOf(d.lead_id);
    return (docName(d) + " " + (l ? l.company : "") + " " + docWhat(d) + " " + d.status + " " + (d.basis || "")).toLowerCase().indexOf(q) > -1;
  }).sort(function (a, b) { return dkey(b).localeCompare(dkey(a)) || (+b.id.slice(1)) - (+a.id.slice(1)); });
  document.getElementById("acc-empty").hidden = rows.length > 0;
  document.getElementById("acc-rows").innerHTML = rows.map(function (d) {
    var l = leadOf(d.lead_id);
    return '<tr data-id="' + d.id + '">' +
      '<td class="co">' + esc(DOCTYPES[d.type]) + " № " + esc(d.n) + "<s>" + esc(d.date) + "</s></td>" +
      '<td>' + (l ? esc(l.company) + "<s>" + esc(l.city) + "</s>" : "—") + "</td>" +
      '<td class="mini what">' + esc(docWhat(d)) + (d.period ? "<s>" + esc(d.period) + "</s>" : "") + "</td>" +
      '<td class="num">' + docSum(d) + "</td>" +
      '<td><select class="st ' + stClass(d.status) + '" data-id="' + d.id + '">' + statuses(d.type).map(function (s) { return "<option" + (s === d.status ? " selected" : "") + ">" + esc(s) + "</option>"; }).join("") + "</select></td>" +
      '<td class="mini">' + ((d.files || []).length ? (d.files || []).map(function (f, i) { return '<a href="file.php?d=' + d.id + '&i=' + i + '" target="_blank" rel="noopener">' + esc(f.name.length > 22 ? f.name.slice(0, 20) + "…" : f.name) + "</a>"; }).join("<br>") : '<span style="color:#b0bbc6">нет скана</span>') + "</td>" +
      '<td class="act"><a class="btn btn--gh btn--sm" href="doc.php?id=' + d.id + '" target="_blank" rel="noopener">Открыть</a> ' +
        '<button type="button" class="btn btn--gh btn--sm" data-edit="' + d.id + '">Изменить</button>' +
        (d.type === "spec" && (d.monthly || []).length ? ' <button type="button" class="btn btn--gh btn--sm" data-month="' + d.id + '">Счёт за месяц</button>' : "") + "</td></tr>";
  }).join("");
}

/* ------------------------------------------------------------------ карточка документа */
var ddlg = document.getElementById("ddlg");
function itemRow(it) {
  it = it || { name: "", qty: 1, unit: "усл.", price: "" };
  return '<tr><td><textarea class="i-name" rows="1" placeholder="Услуга">' + esc(it.name) + '</textarea></td>' +
    '<td><input class="i-qty" inputmode="decimal" value="' + esc(it.qty) + '"></td><td><input class="i-unit" value="' + esc(it.unit) + '"></td>' +
    '<td><input class="i-price" inputmode="decimal" value="' + esc(it.price) + '"></td><td class="i-sum num"></td>' +
    '<td><button type="button" class="i-del" aria-label="Убрать строку">×</button></td></tr>';
}
function monthRow(it) {
  it = it || { name: "", price: "", start: "" };
  return '<tr><td><textarea class="m-name" rows="1" placeholder="Ежемесячная услуга">' + esc(it.name) + '</textarea></td>' +
    '<td><input class="m-price" inputmode="decimal" value="' + esc(it.price) + '"></td><td><input class="m-start" placeholder="с октября 2026" value="' + esc(it.start || "") + '"></td>' +
    '<td><button type="button" class="i-del" aria-label="Убрать строку">×</button></td></tr>';
}
function num(v) { return +String(v).replace(/\s/g, "").replace(",", ".") || 0; }
function recalc() {
  var t = 0;
  ddlg.querySelectorAll("#dd-items tbody tr").forEach(function (tr) {
    var s = num(tr.querySelector(".i-qty").value) * num(tr.querySelector(".i-price").value); t += s;
    tr.querySelector(".i-sum").textContent = s ? fmt(s) : "";
  });
  var m = 0;
  ddlg.querySelectorAll("#dd-monthly tbody tr").forEach(function (tr) { m += num(tr.querySelector(".m-price").value); });
  document.getElementById("dd-total").textContent = (t ? "Итого " + fmt(t) + " ₽" : "") + (m ? (t ? " · " : "") + "ежемесячно " + fmt(m) + " ₽" : "");
}
function partySummary(l) {
  var p = l.party || {};
  return p.name ? esc(p.name) + (p.inn ? ", ИНН " + esc(p.inn) : "") + (p.address ? ", " + esc(p.address) : "") + (p.signer ? " · подписант " + esc(p.signer) : "")
    : '<span class="warn3">Реквизиты клиента не заполнены — в документе будет только название компании.</span>';
}
function fillParents(leadId, chosen) {
  var sel = document.getElementById("dd-parent");
  var list = DOCS.filter(function (d) { return d.type === "contract" && d.lead_id === leadId; });
  sel.innerHTML = '<option value="">без договора</option>' + list.map(function (d) { return '<option value="' + d.id + '"' + (d.id === chosen ? " selected" : "") + ">" + esc(docName(d)) + "</option>"; }).join("");
  if (!chosen && list.length && !curDoc.id) sel.value = list[list.length - 1].id;
}
function openDoc(d) {
  curDoc = d;
  var t = d.type, isNew = !d.id;
  document.getElementById("dd-title-h").textContent = (isNew ? "Новый документ: " : "") + (isNew ? DOCTYPES[t] : docName(d));
  document.getElementById("dd-status").textContent = isNew ? "черновик" : d.status;
  var ls = document.getElementById("dd-lead");
  ls.innerHTML = LEADS.slice().sort(function (a, b) { return a.company.localeCompare(b.company, "ru"); }).map(function (l) {
    return '<option value="' + l.id + '"' + (l.id === d.lead_id ? " selected" : "") + ">" + esc(l.company) + " · " + esc(l.city) + "</option>";
  }).join("");
  ls.disabled = !isNew;
  document.getElementById("dd-n").value = d.n || "";
  document.getElementById("dd-n").placeholder = isNew ? "авто" : "";
  document.getElementById("dd-date").value = d.date || today();
  ddlg.querySelectorAll("[data-for]").forEach(function (el) { el.hidden = el.dataset.for.split(" ").indexOf(t) < 0; });
  fillParents(d.lead_id, d.parent || "");
  document.getElementById("dd-title").value = d.title || "";
  document.getElementById("dd-basis").value = d.basis || "";
  document.getElementById("dd-period").value = d.period || "";
  document.getElementById("dd-due").value = d.due || "";
  document.getElementById("dd-prepay").value = d.prepay == null || d.prepay === "" ? "50" : d.prepay;
  document.getElementById("dd-note").value = d.note || "";
  var items = (d.items && d.items.length) ? d.items : (t === "contract" ? [] : [null]);
  ddlg.querySelector("#dd-items tbody").innerHTML = items.map(itemRow).join("");
  ddlg.querySelector("#dd-monthly tbody").innerHTML = ((d.monthly && d.monthly.length) ? d.monthly : (t === "spec" ? [null] : [])).map(monthRow).join("");
  document.getElementById("dd-party").innerHTML = partySummary(leadOf(d.lead_id) || {});
  drawFiles();
  document.getElementById("dd-open").hidden = isNew;
  document.getElementById("dd-open").href = "doc.php?id=" + (d.id || "");
  document.getElementById("dd-del").hidden = isNew || d.status !== "Черновик";
  document.getElementById("dd-files-box").hidden = isNew;
  recalc();
  ddlg.querySelectorAll("textarea").forEach(grow);
  ddlg.showModal();
}
function grow(t) { t.style.height = "auto"; t.style.height = Math.max(38, t.scrollHeight + 2) + "px"; }
function drawFiles() {
  var d = curDoc, box = document.getElementById("dd-files");
  box.innerHTML = (d.files || []).length ? d.files.map(function (f, i) {
    return '<div class="file"><a href="file.php?d=' + d.id + "&i=" + i + '" target="_blank" rel="noopener">' + esc(f.name) + "</a><s>" + Math.round(f.size / 1024) + " КБ · " + esc(f.at) + " · " + esc(f.by) + '</s><button type="button" data-fdel="' + i + '" aria-label="Удалить файл">×</button></div>';
  }).join("") : '<p class="mini">Сканов пока нет. Подписанный документ загрузите сюда — PDF или фото.</p>';
}
function collect() {
  var d = {
    id: curDoc.id || "", type: curDoc.type, lead_id: document.getElementById("dd-lead").value,
    n: document.getElementById("dd-n").value.trim(), date: document.getElementById("dd-date").value.trim(),
    parent: document.getElementById("dd-parent").value, title: document.getElementById("dd-title").value,
    basis: document.getElementById("dd-basis").value, period: document.getElementById("dd-period").value,
    due: document.getElementById("dd-due").value, prepay: document.getElementById("dd-prepay").value, note: document.getElementById("dd-note").value,
    items: [], monthly: [],
  };
  ddlg.querySelectorAll("#dd-items tbody tr").forEach(function (tr) {
    d.items.push({ name: tr.querySelector(".i-name").value, qty: tr.querySelector(".i-qty").value, unit: tr.querySelector(".i-unit").value, price: tr.querySelector(".i-price").value });
  });
  ddlg.querySelectorAll("#dd-monthly tbody tr").forEach(function (tr) {
    d.monthly.push({ name: tr.querySelector(".m-name").value, price: tr.querySelector(".m-price").value, start: tr.querySelector(".m-start").value });
  });
  return d;
}
function afterDocs(r) {
  if (r.docs) replaceDocs(r.docs);
  if (r.comments && r.doc) { var l = leadOf(r.doc.lead_id); if (l) { l.comments = r.comments; if (current && current.id === l.id) { drawLog(current); drawDocs(current); } } }
  if (current && !r.doc) drawDocs(current);
  drawAcc(); drawRows(); flash();
}
function saveDoc() {
  var d = collect(), btn = document.getElementById("dd-save");
  if (!d.date.match(/^\d\d\.\d\d\.\d{4}$/)) { alert("Дата в виде ДД.ММ.ГГГГ"); return; }
  btn.disabled = true;
  post({ action: "doc_save", doc: JSON.stringify(d) }).then(function (r) {
    afterDocs(r); openDoc(r.doc);
  }).catch(function () { alert("Документ не сохранился, повторите."); }).then(function () { btn.disabled = false; });
}

/* --------------------------------------------------------- документы в карточке сделки */
function drawDocs(l) {
  var box = document.getElementById("d-docs"), list = DOCS.filter(function (d) { return d.lead_id === l.id; })
    .sort(function (a, b) { return dkey(a).localeCompare(dkey(b)) || (+a.id.slice(1)) - (+b.id.slice(1)); });
  box.innerHTML = "<h3>Документы</h3>" + (list.length ? '<div class="dlist">' + list.map(function (d) {
    return '<div class="drow"><a href="doc.php?id=' + d.id + '" target="_blank" rel="noopener">' + esc(docName(d)) + "</a><s>" + docSum(d) + '</s><span class="pill ' + stClass(d.status) + '">' + esc(d.status) + "</span>" +
      ((d.files || []).length ? '<a class="mini" href="file.php?d=' + d.id + '&i=0" target="_blank" rel="noopener">скан</a>' : "") +
      '<button type="button" class="btn btn--gh btn--sm" data-edit="' + d.id + '">Изменить</button></div>';
  }).join("") + "</div>" : '<p class="mini" style="margin:0 0 10px">Документов ещё нет.</p>') +
    '<div class="quick" style="margin:10px 0 0">' + Object.keys(DOCTYPES).map(function (t) { return '<button type="button" data-newdoc="' + t + '">+ ' + esc(DOCTYPES[t]) + "</button>"; }).join("") + "</div>";
}

/* ------------------------------------------------------------- реквизиты студии и клиента */
var cdlg = document.getElementById("cdlg"), pdlg = document.getElementById("pdlg"), partyLead = null;
function openCompany() {
  cdlg.querySelectorAll("[name]").forEach(function (i) { i.value = COMPANY[i.name] || ""; });
  cdlg.showModal();
}
function openParty(l) {
  partyLead = l; var p = l.party || {};
  document.getElementById("pd-co").textContent = l.company;
  pdlg.querySelectorAll("[name]").forEach(function (i) { i.value = p[i.name] || ""; });
  if (!p.name) {   // подсказки из карточки: юрлицо из поля ЛПР
    var m = (l.lpr || "").match(/(ИП|ООО)\s+[«"]?[^,\n]+/); if (m) pdlg.querySelector('[name="name"]').value = m[0].replace(/^ИП\s+/, "Индивидуальный предприниматель ");
    var inn = (l.lpr || "").match(/ИНН\s*(\d{10,12})/); if (inn) pdlg.querySelector('[name="inn"]').value = inn[1];
    var og = (l.lpr || "").match(/ОГРН(?:ИП)?\s*(\d{13,15})/); if (og) pdlg.querySelector('[name="ogrn"]').value = og[1];
  }
  pdlg.showModal();
}

/* ----------------------------------------------------------------------- события */
document.querySelector(".tabs").addEventListener("click", function (e) { var b = e.target.closest("button"); if (b) showView(b.dataset.v); });
document.getElementById("acc-lead").addEventListener("change", function (e) { accLead = e.target.value; drawAcc(); });
document.getElementById("acc-q").addEventListener("input", function (e) { accQ = e.target.value; drawAcc(); });
document.getElementById("acc-company").addEventListener("click", openCompany);
document.querySelector(".acc-new").addEventListener("click", function (e) {
  var b = e.target.closest("button[data-new]"); if (!b) return;
  var lead = accLead || (LEADS[0] && LEADS[0].id);
  openDoc({ type: b.dataset.new, lead_id: lead, date: today() });
});
document.getElementById("acc-rows").addEventListener("click", function (e) {
  var b = e.target.closest("button"); if (!b) return;
  var d = DOCS.filter(function (x) { return x.id === (b.dataset.edit || b.dataset.month); })[0]; if (!d) return;
  if (b.dataset.edit) openDoc(d);
  else {
    var n = new Date(); n.setMonth(n.getMonth() + 1);
    var def = n.getFullYear() + "-" + (n.getMonth() < 9 ? "0" : "") + (n.getMonth() + 1);
    var m = prompt("За какой месяц счёт? В виде ГГГГ-ММ", def); if (!m) return;
    post({ action: "doc_month", id: d.id, kind: "invoice", month: m.trim() }).then(function (r) { afterDocs(r); openDoc(r.doc); })
      .catch(function () { alert("Не удалось создать счёт."); });
  }
});
document.getElementById("acc-rows").addEventListener("change", function (e) {
  var s = e.target.closest("select.st"); if (!s) return;
  post({ action: "doc_status", id: s.dataset.id, status: s.value }).then(afterDocs).catch(function () { alert("Статус не сохранился."); drawAcc(); });
});
document.getElementById("d-docs").addEventListener("click", function (e) {
  var b = e.target.closest("button"); if (!b || !current) return;
  if (b.dataset.newdoc) openDoc({ type: b.dataset.newdoc, lead_id: current.id, date: today() });
  else if (b.dataset.edit) { var d = DOCS.filter(function (x) { return x.id === b.dataset.edit; })[0]; if (d) openDoc(d); }
});
ddlg.addEventListener("click", function (e) {
  if (e.target === ddlg) { ddlg.close(); return; }
  var b = e.target.closest("button"); if (!b) return;
  if (b.id === "dd-x") ddlg.close();
  else if (b.id === "dd-save") saveDoc();
  else if (b.id === "dd-add") { ddlg.querySelector("#dd-items tbody").insertAdjacentHTML("beforeend", itemRow()); }
  else if (b.id === "dd-madd") { ddlg.querySelector("#dd-monthly tbody").insertAdjacentHTML("beforeend", monthRow()); }
  else if (b.classList.contains("i-del")) { b.closest("tr").remove(); recalc(); }
  else if (b.id === "dd-party-edit") { var l = leadOf(document.getElementById("dd-lead").value); if (l) openParty(l); }
  else if (b.id === "dd-del") {
    if (!confirm("Удалить черновик " + docName(curDoc) + "?")) return;
    post({ action: "doc_delete", id: curDoc.id }).then(function (r) { replaceDocs(r.docs); ddlg.close(); if (current) drawDocs(current); drawAcc(); flash(); })
      .catch(function () { alert("Не удалилось: удалять можно только черновики."); });
  } else if (b.dataset.fdel != null) {
    if (!confirm("Удалить файл?")) return;
    post({ action: "doc_file_del", id: curDoc.id, i: b.dataset.fdel }).then(function (r) { replaceDocs(r.docs); curDoc = r.doc; drawFiles(); drawAcc(); if (current) drawDocs(current); });
  }
});
ddlg.addEventListener("input", function (e) { if (e.target.tagName === "TEXTAREA") grow(e.target); recalc(); });
document.getElementById("dd-lead").addEventListener("change", function (e) {
  curDoc.lead_id = e.target.value; fillParents(e.target.value, ""); document.getElementById("dd-party").innerHTML = partySummary(leadOf(e.target.value) || {});
});
document.getElementById("dd-file").addEventListener("change", function (e) {
  var f = e.target.files[0]; if (!f || !curDoc.id) return;
  var fd = new FormData(); fd.append("action", "doc_file"); fd.append("csrf", CSRF); fd.append("id", curDoc.id); fd.append("file", f);
  var lbl = document.getElementById("dd-file-lbl"); lbl.textContent = "Загружаю…";
  fetch("api.php", { method: "POST", body: fd }).then(function (r) { return r.json().then(function (j) { if (!r.ok) throw new Error(j.error || r.status); return j; }); })
    .then(function (r) { replaceDocs(r.docs); curDoc = r.doc; drawFiles(); drawAcc(); if (current) drawDocs(current); flash(); })
    .catch(function (err) { alert("Файл не загрузился: " + err.message); })
    .then(function () { lbl.textContent = "Загрузить скан"; e.target.value = ""; });
});
cdlg.addEventListener("click", function (e) {
  if (e.target === cdlg) cdlg.close();
  var b = e.target.closest("button"); if (!b) return;
  if (b.id === "cd-x") cdlg.close();
  else if (b.id === "cd-save") {
    var body = { action: "company_save" }; cdlg.querySelectorAll("[name]").forEach(function (i) { body[i.name] = i.value; });
    post(body).then(function (r) { Object.keys(r.company).forEach(function (k) { COMPANY[k] = r.company[k]; }); cdlg.close(); drawCocard(); flash(); })
      .catch(function () { alert("Реквизиты не сохранились."); });
  }
});
pdlg.addEventListener("click", function (e) {
  if (e.target === pdlg) pdlg.close();
  var b = e.target.closest("button"); if (!b) return;
  if (b.id === "pd-x") pdlg.close();
  else if (b.id === "pd-save") {
    var body = { action: "party_save", id: partyLead.id }; pdlg.querySelectorAll("[name]").forEach(function (i) { body[i.name] = i.value; });
    post(body).then(function (r) { partyLead.party = r.party; pdlg.close(); if (ddlg.open) document.getElementById("dd-party").innerHTML = partySummary(partyLead); flash(); })
      .catch(function () { alert("Реквизиты не сохранились."); });
  }
});

if (location.hash === "#acc") showView("acc");
