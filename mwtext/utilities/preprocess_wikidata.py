r"""
``$ mwtext preprocess_wikidata -h``
::
    Converts Wikidata XML dumps to string of property/value pairs.

    Usage:
        preprocess_wikidata (-h|--help)
        preprocess_wikidata [<input-file>...]
                            [--threads=<num>] [--output=<path>]
                            [--compress=<type>] [--verbose] [--debug]

    Options:
        -h --help           Print this documentation
        <input-file>        The path to a Wikidata XML Dump file
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


def preprocess_wikidata(dump, verbose=False):
    wikidata_preprocessor = WikidataPreprocessor()
    for page in dump:
        for revision in page:
            if not is_relevant_page(page, revision):
                continue
            item_doc = json.loads(revision.text)
            qid = item_doc.get('id', None)
            entity = mwbase.Entity.from_json(item_doc)
            if not is_relevant_entity(entity, qid):
                continue

            if verbose:
                sys.stderr.write(qid + "\n")
                sys.stderr.flush()

            claims_tuples = wikidata_preprocessor.process(entity)
            random.shuffle(claims_tuples)
            claims_str = ' '.join([' '.join(claim) for claim in claims_tuples])
            yield claims_str


def is_relevant_page(page, revision):
    return (page.namespace == 0 and
            revision.model == 'wikibase-item')


def is_relevant_entity(entity, qid):
    sitelinks = [l[:-4] for l in list(entity.sitelinks.keys())
                 if l.endswith('wiki') and
                 l != 'commonswiki' and l != 'specieswiki']
    return (len(sitelinks) > 0 and qid != None)


streamer = mwcli.Streamer(
    __doc__,
    __name__,
    preprocess_wikidata,
    file_reader=mwcli.Streamer.read_xml,
    line_writer=mwcli.Streamer.write_line
)

main = streamer.main
