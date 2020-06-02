import bz2
import json
import os

import mwbase


def getPropertyValue(entity):
    prop_val = ''
    properties = list(entity.properties.keys())
    for prop in properties:
        values = ''
        for statement in entity.properties[prop]:
            claim = statement.claim
            if claim.datatype == 'wikibase-item':
                datavalue = claim.datavalue
                if datavalue:
                    value = datavalue.id
                    values += (' ' + prop + ' ' + value)
        if not values:
            prop_val += ' ' + prop
        else:
            prop_val += values
    return prop_val[1:]


def isRelevantEntity(entity):
    sitelinks = [l[:-4] for l in list(entity.sitelinks.keys()) 
                 if l.endswith('wiki') and 
                 l != 'commonswiki' and l != 'specieswiki']
    return (len(sitelinks) > 0)


def preprocess_wikidata(WIKIDATA_DIR):
    with bz2.open(os.path.join(WIKIDATA_DIR, 'latest-all.json.bz2'), 'rt') as fin:
        next(fin)
        for idx, line in enumerate(fin, start=1):
            try:
                item_json = json.loads(line)
            except Exception:
                try:
                    item_json = json.loads(line[:-2])
                except Exception:
                    print("Error:", idx)
                    continue

            qid = item_json.get('id', None)
            if not qid:
                continue

            entity = mwbase.Entity.from_json(item_json)
            if isRelevantEntity(entity):
                prop_val = getPropertyValue(entity)
                yield qid + ": " + prop_val
