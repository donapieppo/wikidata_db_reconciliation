#!/usr/bin/env python3

import json
import sqlite3

connection = sqlite3.connect("/home/backup/wikidata.db")
connection.row_factory = sqlite3.Row
cursor_human = connection.cursor()
cursor_viaf = connection.cursor()

cursor.execute("SELECT * from humans")

exit(0)

for row in cursor:
    if row['viaf_id'] and row['viaf_id'] != 'null':
        for x in json.loads(row['viaf_id']):
            print(x)
            cursor2.execute("""
              INSERT INTO viafs (human_id, viaf_id, wiki_id) VALUES (?, ?, ?)
              """, (row['id'], x, row['wiki_id']))

connection.commit()
connection.close()
