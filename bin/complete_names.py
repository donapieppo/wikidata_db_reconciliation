#!/usr/bin/env python3

# extract names and surnames from qids and check if 
# "name1 name2 surname" is already in names database. If not it is added

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
        # print(f"{qval} -> {labels}")
        return labels[0]

    return None


cursor_human.execute("SELECT * from humans")

for row in cursor_human:
    # print(f"{row['id']} --- qnames: {row['qnames']} --- qsurnames: {row['qsurnames']} ---  {row['wiki_id']}")

    qnames = json.loads(row['qnames']) if row['qnames'] != 'null' else []
    qsurnames = json.loads(row['qsurnames']) if row['qsurnames'] != 'null' else []

    all_names = []
    for qval in qnames + qsurnames:
        r = get_wdname(qval)
        if r:
            all_names.append(r)

    if len(all_names) < 2:
        print(f"{row['id']}: not enough names (<2)")
        print(all_names)
        continue
        
    name = " ".join(all_names).lower()
    print(f"{row['id']} -> {name} <-")

    cursor_name.execute("SELECT count(*) as c FROM names "
                        "WHERE name = ? AND human_id = ? LIMIT 1",
                        (name, row['id']))
    res = cursor_name.fetchone()

    if res['c'] == 0:
        print("To add to names")
        # print("Actual names:")
        # cursor_name.execute("SELECT * FROM names WHERE human_id = ?", (row['id'], ))
        # for x in cursor_name.fetchall():
        #    print(x["name"])
        cursor_name.execute("INSERT INTO names (human_id, name) VALUES (?, ?)", (row['id'], name))
        connection.commit()
    else:
        print("Already in names")
        # print(dict(res))

    input(".")

connection.commit()
connection.close()
