#!/usr/bin/env python3

"""
Read from a list of common first names and deletes them from names table
if they appear more that 2 times
"""

import argparse
import sqlite3
from os.path import exists

args = argparse.ArgumentParser(description="Claar local wikidata db from common names.")
args.add_argument('-db', dest='db', metavar='filename', nargs=1, type=str,
                  help='the sqlite3 file with wikidata.',
                  required=True)

args = args.parse_args()
db = args.db[0]

if (not exists(db)):
    print(f"No file {db}")
    exit(1)

connection = sqlite3.connect(db)
connection.row_factory = sqlite3.Row
cursor = connection.cursor()
cursor_delete = connection.cursor()

for name in open("data/names.txt", mode='r'):
    name = name.strip().lower()
    res = cursor.execute("""
        SELECT count(*) AS c FROM names WHERE name = ?
        """, (name, )).fetchone()

    if (res["c"] < 3):
        continue
    
    print(f"{res['c']} -> {name}")

    cursor_delete.execute("""
        DELETE FROM names where name = ?
        """, (name, ))

connection.commit()
