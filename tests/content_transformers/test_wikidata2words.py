import json
import os

from mwtext.content_transformers import Wikidata2Words

local_dir = os.path.dirname(os.path.realpath(__file__))


def load_wikidata_content(id):
    doc = json.load(open(os.path.join(local_dir, "data/{0}.json".format(id))))
    return json.dumps(list(doc['entities'].values())[0])


def test_preprocessing_english():
    Q18627581 = load_wikidata_content("Q18627581")
    wd2w = Wikidata2Words()
    words = list(sorted(wd2w.transform(Q18627581)))

    assert words == \
        [('P106', 'Q82594'), ('P108', 'Q180'), ('P1153',),
         ('P1416', 'Q21561406'), ('P18',), ('P184', 'Q14282656'),
         ('P19', 'Q986681'), ('P1960',), ('P2002',), ('P2037',),
         ('P2038',), ('P21', 'Q6581097'), ('P27', 'Q30'), ('P31', 'Q5'),
         ('P373',), ('P496',), ('P569',), ('P646',), ('P69', 'Q238101'),
         ('P69', 'Q7726780'), ('P735', 'Q905085'), ('P800', 'Q21679410'),
         ('P856',), ('P864',), ('P990',)]
