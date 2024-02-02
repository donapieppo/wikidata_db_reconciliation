import json
from wikidata_json_helpers import extract_datavalue, extract_value, check_value

OCCUPATIONS = {
    'Q28640',    # profession (Q28640)
    'Q12737077'  # occupation (Q12737077)
}

QNAMES = {
    'P735',       # given name
    'Q12308941',  # male given name (Q12308941)
    'Q11879590',  # female given name (Q11879590)
    'Q1471689',   # ancient Egyptian name (Q1471689)
    'Q3409032',   # unisex given name (Q3409032) 
    'Q18972207'   # female family name (Q18972207)
}

QSURNAMES = {
    'P734',       # family name
    'Q101352',    # family name
    'Q202444',    # given name
    'Q18972207',  # female family name (Q18972207) 
    'Q106319018', # hyphenated surname (Q106319018) 
    'Q66480858',  # affixed family name (Q66480858)
}

QNAMES_AND_SURNAMES = QNAMES.union(QSURNAMES)

class WikidataItem:
    def __init__(self, j, languages, first_label=False):
        self.json = j
        self.languages = languages
        self.first_label = first_label
        self.wiki_id = self.json["id"]
        self.labels = self.extract_labels()

    # {'mainsnak': {... 'datavalue': {'value': {... 'id': 'Q5'} ...
    def extract_labels(self):
        # return labels if interesting item (name, surname, occupation)
        for x in self.json['claims']['P31']:
            qid = extract_value(x, "mainsnak.datavalue.value.id")
            if not qid:
                print("NO QUID")
                print(x)
            elif qid in QNAMES_AND_SURNAMES:
                labels = self.json['labels']
                res = set()
                for lang in self.languages:
                    if lang in labels:
                        if self.first_label:
                            return labels[lang]['value']
                        else:
                            res.add(labels[lang]['value'])
                return res
            elif qid in OCCUPATIONS:
                labels = self.json['labels']
                res = set()
                for lang in ['it', 'en']:
                    if lang in labels:
                        if self.first_label:
                            return labels[lang]['value']
                        else:
                            res.add(labels[lang]['value'])
                return res
        return None

    def save(self, cursor):
        cursor.execute("""
          INSERT INTO wditems (wiki_id, labels) VALUES (?, ?)
          """, (self.wiki_id, json.dumps(list(self.labels))))


    def __str__(self):
        return("wikiitem id: " + str(self.wiki_id) +
               " labels: " + str(self.labels))
