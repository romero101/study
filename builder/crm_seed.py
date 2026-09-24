# -*- coding: utf-8 -*-
"""Перенос таблицы продаж из Excel в базу мини-CRM.
Запускать один раз: дальше данные живут в admin/data/store.php (закрытый файл) и правятся в админке.
Повторный запуск НЕ затирает комментарии и этапы — обновляет только пустые поля."""
import json, os, sys
import xlrd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLS = os.path.join(ROOT, "builder", "data", "forma-saita-sales.xls")
OUT = os.path.join(ROOT, "builder", "crm", "seed", "leads.json")  # на сервер не заливается: там данные живут в data/store.php

# Этапы воронки. Порядок = порядок колонок на доске.
STAGES = ["Не связывались", "Дозвонился до ЛПР", "Отправил лендинг",
          "Взял обратную связь", "Счёт выставлен", "Оплачено", "В работе", "Отказ"]

FIELDS = ["n", "company", "city", "was_url", "now_url", "was_problems",
          "now_done", "left_todo", "contacts", "pagespeed", "offer", "stage", "measure_src"]

def cell(sh, r, c):
    if c >= sh.ncols: return ""
    v = sh.cell_value(r, c)
    if isinstance(v, float) and v == int(v): v = int(v)
    return str(v).strip()

def main():
    book = xlrd.open_workbook(XLS)
    sh = book.sheet_by_name("Было-стало")
    rows, header_row = [], None
    for r in range(sh.nrows):
        if cell(sh, r, 0) == "№":
            header_row = r; break
    if header_row is None:
        sys.exit("не нашёл шапку таблицы в листе «Было-стало»")

    for r in range(header_row + 1, sh.nrows):
        if not cell(sh, r, 1): continue
        d = {FIELDS[i]: cell(sh, r, i) for i in range(len(FIELDS))}
        d["id"] = "l%02d" % (int(d["n"]) if d["n"].isdigit() else r)
        d["offer"] = int(d["offer"] or 0)
        d["pagespeed"] = int(d["pagespeed"]) if d["pagespeed"].isdigit() else None
        if d["stage"] not in STAGES: d["stage"] = STAGES[0]
        d["comments"] = []
        d["updated"] = ""
        if d["now_url"] in ("", "Не создан"):
            d["now_url"] = ""
        rows.append(d)

    # бережное слияние: то, что менял менеджер, остаётся
    if os.path.exists(OUT):
        old = json.load(open(OUT, encoding="utf-8"))
        by_id = {x["id"]: x for x in old.get("leads", [])}
        for d in rows:
            o = by_id.get(d["id"])
            if not o: continue
            d["comments"] = o.get("comments", [])
            d["stage"] = o.get("stage", d["stage"])
            d["updated"] = o.get("updated", "")
            for k in FIELDS:
                if o.get(k) and k not in ("stage",):
                    d[k] = o[k]      # правки менеджера приоритетнее таблицы

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({"stages": STAGES, "leads": rows}, open(OUT, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("перенесено сделок: %d -> %s" % (len(rows), OUT))
    for d in rows[:3]:
        print("  %s  %-16s %-18s %s" % (d["id"], d["company"], d["city"], d["stage"]))

if __name__ == "__main__":
    main()
