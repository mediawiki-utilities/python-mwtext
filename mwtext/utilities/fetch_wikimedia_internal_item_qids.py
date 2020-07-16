from SPARQLWrapper import SPARQLWrapper, JSON
import re
import sys

MWTEXT_UA = "mwtext fetch_qid <ahalfaker@wikimedia.org>"


def get_qids():
    url = "https://query.wikidata.org/sparql"
    query = """SELECT ?subclasses
                WHERE
                {
                  # any subclass of "Wikimedia internal item"
                  ?subclasses wdt:P279* wd:Q17442446.
                }
            """
    sparql = SPARQLWrapper(url, agent=MWTEXT_UA)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    qids = []
    for result in results['results']['bindings']:
        link = result.get('subclasses').get('value')
        qid = re.search('Q[0-9]+', link).group()
        qids.append(qid)

    return qids


def main():
    qids = get_qids()
    for qid in qids:
        sys.stdout.write(qid + "\n")


main()
