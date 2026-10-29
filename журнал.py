#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Запись в журнал СГЛА.

    python3 "2. Сервисы/Задачник/журнал.py" "Заголовок" "Подробности на пару предложений" тег1 тег2
    python3 "2. Сервисы/Задачник/журнал.py" --push ...     # сразу выложить на сайт

Пишет в journal-sgla.json и обновляет встроенную копию в index.html,
чтобы страница работала и локально, и на GitHub Pages.
"""
import io, json, os, re, subprocess, sys, datetime

КОРЕНЬ = os.path.dirname(os.path.abspath(__file__))
JSON = os.path.join(КОРЕНЬ, "journal-sgla.json")
HTML = os.path.join(КОРЕНЬ, "index.html")

def добавить(заголовок, текст, теги, дата=None, пушить=False):
    дата = дата or datetime.date.today().isoformat()
    д = json.load(io.open(JSON, encoding="utf-8")) if os.path.exists(JSON) else {"записи": []}
    д["записи"] = [{"дата": дата, "заголовок": заголовок, "текст": текст, "теги": теги}] + д["записи"]
    д["обновлено"] = дата
    io.open(JSON, "w", encoding="utf-8").write(json.dumps(д, ensure_ascii=False, indent=1))
    s = io.open(HTML, encoding="utf-8").read()
    s = re.sub(r"const JOURNAL_INLINE=.*?;\nlet JOURNAL=JOURNAL_INLINE",
               "const JOURNAL_INLINE=" + json.dumps(д, ensure_ascii=False) + ";\nlet JOURNAL=JOURNAL_INLINE",
               s, flags=re.S)
    io.open(HTML, "w", encoding="utf-8").write(s)
    print(f"записано: {заголовок} [{', '.join(теги)}]  всего записей: {len(д['записи'])}")
    if пушить:
        subprocess.run(["git", "add", "journal-sgla.json", "index.html"], cwd=КОРЕНЬ, check=True)
        subprocess.run(["git", "commit", "-m", "журнал: " + заголовок], cwd=КОРЕНЬ, check=True)
        subprocess.run(["git", "push", "origin"], cwd=КОРЕНЬ, check=True)
        print("выложено на сайт")

if __name__ == "__main__":
    а = sys.argv[1:]
    пушить = "--push" in а
    а = [x for x in а if x != "--push"]
    if len(а) < 2:
        print(__doc__); sys.exit(1)
    добавить(а[0], а[1], а[2:], пушить=пушить)
