#!/usr/bin/env python3

import argparse
import json
import sqlite3
from os.path import exists

args = argparse.ArgumentParser(description='Add qnames and qsurnames in names.')

args.add_argument('-db', metavar='filename', nargs=1, type=str,
                   help='the sqlite3 file to read/rwite data.',
                   required=True)

args = args.parse_args()
db = args.db[0]

if (not exists(db)):
    print(f"No file {db}.")
    exit(1)


connection = sqlite3.connect(db)
connection.row_factory = sqlite3.Row

cursor_human = connection.cursor()
cursor_name = connection.cursor()
cursor_wditem = connection.cursor()

def update_human(human_id, name, surname):
    if not (human_id and name and surname):
        return False

    cursor_human.execute("""
        UPDATE humans SET (
            name=?
            surname=?
            ) WHERE id=?
        """, (name, surname, human_id))
    connection.commit()


def get_wdname(qval):
    if not qval:
        return None

    cursor_wditem.execute("SELECT * FROM wditems WHERE wiki_id = ?", (qval,))
    row = cursor_wditem.fetchone()

    if row:
        labels = json.loads(row['labels'])
        print(f"{qval} -> {labels}")
        return labels[0]

    return None


cursor_human.execute("SELECT * from humans")

for row in cursor_human:
    print(f"{row['id']} --- qnames: {row['qnames']} --- qsurnames: {row['qsurnames']} ---  {row['wiki_id']}")

    qnames = json.loads(row['qnames']) if row['qnames'] != 'null' else []
    qsurnames = json.loads(row['qsurnames']) if row['qsurnames'] != 'null' else []

    names = []
    for qval in qnames + qsurnames:
        r = get_wdname(qval)
        if r:
            names.append(r)

    if len(names) < 2:
        print("not enough")
        continue
        
    name = " ".join(names).lower()

    cursor_name.execute("SELECT count(*) as c FROM names "
                        "WHERE name = ? AND human_id = ? LIMIT 1",
                        (name, row['id']))
    res = cursor_name.fetchone()

    if res['c'] == 0:
        print(name)
    else:
        print(dict(res))
    input(".")

connection.commit()
connection.close()
