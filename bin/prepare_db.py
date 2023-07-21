#!/usr/bin/env python3

import argparse
import sqlite3
from os.path import exists

parser = argparse.ArgumentParser(description="Prepare a sqlite3 db for reconciliation")
parser.add_argument('-db', metavar='filename', nargs=1, type=str,
                    help='the sqlite3 file to save data.',
                    required=True)

args = parser.parse_args()
db = args.db[0]

if (exists(db)):
    print(f"File {db} already exists.")
    exit(1)

connection = sqlite3.connect(db)
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE humans (
      id INTEGER PRIMARY KEY,
      wiki_id TEXT,
      qnames TEXT,
      qsurnames TEXT,
      name TEXT,
      surname TEXT,
      label TEXT,
      year_of_birth INT,
      year_of_death INT,
      description TEXT,
      occupations TEXT,
      wikipedia_url TEXT,
      nreferences INTEGER
    )""")

cursor.execute("""
    CREATE TABLE names (
      id INTEGER PRIMARY KEY,
      human_id INTEGER,
      name TEXT
    )""")

cursor.execute("""
    CREATE TABLE wditems (
      id INTEGER PRIMARY KEY,
      wiki_id TEXT, 
      labels TEXT
    )""")

cursor.execute("""
    CREATE TABLE viafs (
      id INTEGER PRIMARY KEY,
      viaf_id TEXT,
      human_id INTEGER,
      wiki_id TEXT
    )""")

cursor.execute("CREATE UNIQUE INDEX idx_humans_wid ON humans (wiki_id)")
cursor.execute("CREATE INDEX idx_names_human ON names (human_id)")
cursor.execute("CREATE INDEX idx_names_name ON names (name)")
cursor.execute("CREATE UNIQUE INDEX idx_wditems_wid ON wditems (wiki_id)")
cursor.execute("CREATE INDEX idx_viafs_viaf ON viafs (viaf_id)")
cursor.execute("CREATE INDEX idx_viafs_wiki ON viafs (wiki_id)")
cursor.execute("CREATE INDEX idx_viafs_human ON viafs (human_id)")
