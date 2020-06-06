r"""
``$ mwtext preprocess_wikidata -h``
::
    Converts WIkidata JSON dumps to string of property/value pairs.
    Usage:
        preprocess_wikidata (-h|--help)
        preprocess_wikidata [<input-file>...]
                            [--threads=<num>] [--output=<path>]
                            [--compress=<type>] [--verbose] [--debug]
    Options:
        -h|--help           Print this documentation
        <input-file>        The path to a Wikidata JSON Dump file
                            [default: <stdin>]
        --threads=<num>     If a collection of files are provided, how many
                            processor threads? [default: <cpu_count>]
        --output=<path>     Write output to a directory with one output file
                            per input path.  [default: <stdout>]
        --compress=<type>   If set, output written to the output-dir will be
                            compressed in this format. [default: bz2]
        --verbose           Print progress information to stderr.  Kind of a
                            mess when running multi-threaded.
        --debug             Print debug logs.
"""

import bz2
import json
import os
import random
import sys

import mwbase
import mwcli

from ..wikidata_preprocessor import WikidataPreprocessor


def getPropertyValue(entity):
    claims_tuples = []
    properties = list(entity.properties.keys())
    for prop in properties:
        value_found = False
        for statement in entity.properties[prop]:
            claim = statement.claim
            if claim.datatype == 'wikibase-item':
                datavalue = claim.datavalue
                if datavalue:
                    value = datavalue.id
                    value_found = True
                    claims_tuples.append((prop, value))
        if not value_found:
            claims_tuples.append((prop,))

    random.shuffle(claims_tuples)
    claims_str = ' '.join([' '.join(c) for c in claims_tuples])
    return claims_str


def isRelevantEntity(entity):
    sitelinks = [l[:-4] for l in list(entity.sitelinks.keys()) 
                 if l.endswith('wiki') and 
                 l != 'commonswiki' and l != 'specieswiki']
    return (len(sitelinks) > 0)


def preprocess_wikidata(dump):
    wikidata_preprocessor = WikidataPreprocessor()
    for item_json in dump:
        qid = item_json.get('id', None)
        if not qid:
            continue

        if verbose:
            sys.stderr.write(qid + ": ")
            sys.stderr.flush()

        entity = mwbase.Entity.from_json(item_json)
        if isRelevantEntity(entity):
            prop_val = getPropertyValue(entity)
            yield qid + ": " + prop_val
            if verbose:
                sys.stderr.write(".")
                sys.stderr.flush()
        else:
            if verbose:
                sys.stderr.write("-")
                sys.stderr.flush()
  
        if verbose:
            sys.stderr.write("\n")
            sys.stderr.flush()


streamer = mwcli.Streamer(
    __doc__,
    __name__,
    preprocess_wikidata,
    file_reader=mwcli.Streamer.read_json,
    line_writer=mwcli.Streamer.write_line
)

main = streamer.main
