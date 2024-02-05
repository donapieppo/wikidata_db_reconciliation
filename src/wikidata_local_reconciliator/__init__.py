import sqlite3
import re
from unidecode import unidecode

from wikidata_occupation import WikidataOccupation

LOCAL_FILE = "/home/rails/OpenMlol/tmp/wikidata.db"


class WikidataLocalReconciliator():
    def __init__(self, db_file=LOCAL_FILE):
        connection = sqlite3.connect(db_file)
        connection.row_factory = sqlite3.Row
        self.cursor = connection.cursor()
        self.wd_occupation = WikidataOccupation()

    def add_occupation(self, name, wiki_id):
        self.wd_occupation.add_occupation(name, wiki_id)

    def check_year(self, row, year):
        """Returns True id checks if row['year_of_birth'] > year

        It usually cheks if the person was already born in the year of the opera
        """

        if year and row['year_of_birth']:
            return row['year_of_birth'] < year
        else:
            return(True)

    def clear_name(self, name, replace_dash=False, with_unidecode=False):
        """Clear the name and return it"""
        # fist lower the name since in db they are lowercase
        name = name.lower()
        # take off brackets (200xii)
        name = re.sub(r'\(.*?\)', '', name)
        # strip spaces and 2... spaces becomes one
        name = re.sub(r'\s{2,}', ' ', name).strip()
        if replace_dash:
            name = re.sub(r'-', ' ', name)
        if with_unidecode:
            name = unidecode(name)
        return(name)

    def check_name_from_wiki_id(self, wiki_id, name):
        """Check if human identified by wiki_id has the name"""
        res = self.cursor.execute("""
            SELECT id FROM names WHERE wiki_id = ? AND name = ?
            """, (wiki_id, name.lower())).fetchone()
        return(res)

    def get_by_wiki_id(self, wiki_id):
        res = self.cursor.execute("""
                SELECT * from humans WHERE wiki_id = ?
                """, (wiki_id, )).fetchone()
        return res if res else None

    def get_by_viaf_id(self, viaf_id):
        res = self.cursor.execute("""
            SELECT humans.* FROM humans
            LEFT JOIN viafs ON viafs.human_id = humans.id
            WHERE viafs.viaf_id = ?
            """, (viaf_id, )).fetchone()
        return res if res else None

    # re.sub(r'-',' ', name)
    # unidecode(name)
    def search(self, name, year=None, occupations=None):
        name = self.clear_name(name)
        all_rows = self.cursor.execute("""
            SELECT DISTINCT humans.*, viafs.viaf_id FROM humans
            LEFT JOIN names ON humans.id = names.human_id
            LEFT JOIN viafs ON humans.id = viafs.human_id
            WHERE names.name = ?
            """, (name, )).fetchall()
        # COLLATE NOCASE

        best = None
        second = None

        for row in all_rows:
            row = dict(row)
            if self.wd_occupation.check(row, occupations) and self.check_year(row, year):
                if (not best) or (row['nreferences'] > best['nreferences']):
                    second = best
                    best = row
                else:
                    second = row
        return(best if best else second)

    def ask(self, name, year=None, occupations=None):
        cname = self.clear_name(name)
        res = self.search(cname, year=year, occupations=occupations)
        if not res:
            cname = self.clear_name(name, replace_dash=True)
            if cname != name:
                res = self.search(cname, year=year, occupations=occupations)
        
        if not res:
            cname = self.clear_name(name, replace_dash=True, with_unidecode=True)
            if cname != name:
                res = self.search(cname, year=year, occupations=occupations)
        return res
        
    def show_occupations(self, res):
        if res:
            print(res["occupations"])
            print(self.wd_occupation.describe(res["occupations"]))

    def show_res(self, res):
        if res:
            return(f"{res['wiki_id']}: {res['label']} ({res['year_of_birth']}) {res['description']} viaf: {res['viaf_id']}")
        else:
            return("No Result")
