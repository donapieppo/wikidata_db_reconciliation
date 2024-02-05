# Wikidata Local Reconciliation

From a wikidata database dump we build a sqlite3 db useful for local reconciliation of authors.

From the wikidata dump we take all names and aliases of humans(Q5) with all occupations, birth and death dates and some "references number" 
in order to query for wikidata id given a name.

As an example, given `/home/data/wd.db` as the sqlite3 created:

```python
from wikidata_local_reconciliator import WikidataLocalReconciliator

reconciliator = WikidataLocalReconciliator(db_file='/home/data/wd.db')
result = reconciliator.ask('martin scorsese', 2000, 'film_director')
```

returns the following result (main data):

```python3
'id': 697, 
'wiki_id': 'Q41148', 
'viaf_id': '111716145', 
'label': 'Martin Scorsese', 
'year_of_birth': 1942, 
'description': 'regista, attore, sceneggiatore e produttore cinematografico italo-statunitense (1942-)', 
'occupations': {'Q3282637', 'Q7042855', 'Q10800557', 'Q28389', 'Q2059704', 'Q3455803', 'Q2405480', 'Q2526255'}, 
'wikipedia_url': 'https://it.wikipedia.org/wiki/Martin_Scorsese'
```

## Dowload wikidata dump

Visit [https://www.wikidata.org/wiki/Wikidata:Database_download] and get
latest json.bz2. You can also split it while downloading

```
mkdir -p wikidata/data
wget -O - https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.bz2 | bzcat | split -l 100000 -d -a 4 --filter='bzip2 > wikidata/data/$FILE.json.bz2' - split-
```

If you already have downloaded the dump, you can just split with:

```bash
mkdir wikidata
bzcat latest-all.json.bz2 | split -l 100000 -d -a 4 --filter='bzip2 > wikidata/data/$FILE.json.bz2' - split-
```

## Prepare the database

With the command

```bash
./bin/prepare_db.py -db wikidata/wikidata.db
```

you create a `wikidata.db` sqlite3 database with this schema:

```sql
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
  wikpedia_url TEXT,
  nreferences INT
);

CREATE UNIQUE INDEX idx_humans_wid ON humans (wiki_id);

CREATE TABLE names (
  id INTEGER PRIMARY KEY,
  human_id INTEGER,
  name TEXT
);

CREATE INDEX idx_names_name ON names (name);
CREATE INDEX idx_names_human ON names (human_id);

CREATE TABLE wditems (
  id INTEGER PRIMARY KEY,
  wiki_id TEXT, 
  labels TEXT
);

CREATE UNIQUE INDEX idx_wditems_wid ON wditems (wiki_id);

CREATE TABLE viafs (
  id INTEGER PRIMARY KEY,
  viaf_id TEXT,
  human_id INTEGER,
  wiki_id TEXT
);

CREATE INDEX idx_viafs_viaf ON viafs (viaf_id);
CREATE INDEX idx_viafs_wiki ON viafs (wiki_id);
CREATE INDEX idx_viafs_human ON viafs (human_id);
```

## Parse the wikidata dump

To start parsing

```bash
for f in wikidata/data/split*.json.bz2
do
        ./bin/parse.py -db ./wikidata/wikidata.db $f
done
```

Then we must add the names/surnames from given name and family name
that are not in the `names` table.

```
./bin/complete_names.py
```

Now you can also remove the `wikidata/data` dir that contains the dump.

The size of the `wikidata.db` file is about 2.5G and contains something like
10 millions of person and 14 millions of names.

## Use the library

The following snippet asks to reconciliate the string `martin scorsese` with
the request that the author is a `film_director` and that it is born after year 2000.

```python
from wikidata_local_reconciliator import WikidataLocalReconciliator

reconciliator = WikidataLocalReconciliator(db_file='/home/data/wd.db')
result = reconciliator.ask('martin scorsese', 2000, 'film_director')
```

In `src/wikidata_occupation/defaults.py` you find the most common 
occupations for my reconciliation interest. Feel free to add yours to
the file. You can also add occupations for a specific search with

```python
reconciliator = WikidataLocalReconciliator(db_file='/home/data/wd.db')
reconciliator.add_occupation('lithographe', 'Q16947657')
result = reconciliator.ask('john doe', 2000, 'lithographe')
```

## Observations on the DB 

`humans` on the first pass is filled with `qnames` and `qsurnames` which are the wikidata ids of name and surname of the human.

  - 'P734' (name)
  - 'Q101352' (family name)
  - 'Q12308941' (male given name)
  - 'Q11879590' (female given name)
  - 'P735' (surname)

For example Douglas Adams has wikidata_id: Q42 

  - qnames: `['Q463035', 'Q19688263']` 
  - qsurnames: `['Q351735']`

since `Q463035` -> `Douglas` but on the first pass we don't know. 
We have to reach the item `Q463035` on the wikidata dump to register 
it in the `wditems` table.

## Credits and other stuff

  - [https://akbaritabar.netlify.app/how_to_use_a_wikidata_dump] uses pydash to read json data more 
  - [https://madflex.de/splitting-a-big-file-with-split] for splitting the big wikidata file

## TODO

  - [https://github.com/ijl/orjson]
  - ...
