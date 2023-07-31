import json
from .defaults import OCCUPATIONS

class WikidataOccupation():
    def __init__(self):
        self.occupations_by_name = OCCUPATIONS
        self.occupations_by_qcode = {value: key for key, value in OCCUPATIONS.items()}
        self.qcodes = set(OCCUPATIONS.values())

    def add_occupation(self, name, wiki_id):
        self.occupations_by_name[name] = wiki_id
        self.occupations_by_qcode[wiki_id] = name
        self.qcodes.add(wiki_id)

    def get_name_by_qcode(self, q):
        if q in self.occupations_by_qcode:
            return self.occupations_by_qcode[q]
        return None

    def get_qcode_by_name(self, n):
        if n in self.occupations_by_name:
            return self.occupations_by_name[n]
        return None

    def list_occupations(self):
        print(self.occupations_by_name)
        print(self.occupations_by_qcode)

    # True / False
    def check(self, row, occupations):
        if not occupations:
            return True
        if 'occupations' not in row:
            return False
        if not row['occupations'] or row['occupations'] == 'null':
            return False

        if occupations:
            occupations = occupations.split(', ')
            occupations = [OCCUPATIONS[k] for k in occupations]
        else:
            occupations = self.qcodes

        row['occupations'] = set(json.loads(row['occupations']))
        return len(row['occupations'].intersection(occupations)) > 0

    def describe(self, names):
        """ can receive json.dump of array of occupatons or a list"""

        if isinstance(names, str):
            if names[0] == '[':
                names = json.loads(names)
            else:
                names = names.split(', ')

        if list(names)[0][0] == 'Q':
            return([self.get_name_by_qcode(name) for name in names])
        return([self.get_qcode_by_name(name) for name in names])
