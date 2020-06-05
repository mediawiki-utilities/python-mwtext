r"""
``$ mwtext transform_content -h``
::

    Transforms content from MediaWiki XML dumps.  Outputs `revdocs` but
    replaces content fields with transformed content.

    Usage:
        transform_content (-h|--help)
        transform_content <content-transformer> [<input-file>...]
                          [--parameter=<kv>]...
                          [--namespace=<id>]...
                          [--labels=<path>] [--label-field=<k>]
                          [--threads=<num>] [--output=<path>]
                          [--compress=<type>] [--verbose] [--debug]

    Options:
        -h|--help           Print this documentation
        <content-transformer>  Path to a content transformer to construct and
                               execute.
        <input-file>        The path to a MediaWiki XML Dump file
                            [default: <stdin>]
        --parameter=<kv>    A parameter to pass to the <content-transformer>
        --namespace=<id>    Limit processing to this namespace.  Can be
                            repeated to select for multiple namespaces.
        --wiki-host=<url>   The hostname of the MediaWiki install to query
                            for metadata from.
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
import json
import logging
import re
import sys

import mwapi
import mwcli
import mwcli.files

from ..wikitext_preprocessor import WikitextPreprocessor

logger = logging.getLogger(__name__)
REDIRECT_RE = re.compile("#redirect", re.I)


def preprocess_text(dump, forbidden_namespaces, title2labels=None,
                    namespaces=None, min_line=10, verbose=False):
    wikitext_preprocessor = WikitextPreprocessor(forbidden_namespaces)
    for page in dump:
        if namespaces and page.namespace not in namespaces:
            continue
        if title2labels is not None:
            if page.title not in title2labels:
                continue
            else:
                labels = title2labels[page.title]
        else:
            labels = []
        if verbose:
            sys.stderr.write(page.title + ": ")
            sys.stderr.flush()

        for revision in page:
            if not is_article(revision.text):
                continue
            for line in wikitext_preprocessor.process(revision.text):
                if len(line) >= min_line:
                    yield format_labels(labels) + " ".join(line)
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


def format_labels(label_ids):
    if len(label_ids) > 0:
        return " ".join("__label__{0}".format(id) for id in label_ids) + " "
    else:
        return ""


def process_args(args):
    session = mwapi.Session(
        args['--wiki-host'], user_agent="mwtext preprocess_text")
    lang, forbidden_namespaces = get_wiki_info(session)
    logger.info(
        "Gathered details from site_info: lang={0}, forbidden_namespaces={1}"
        .format(lang, forbidden_namespaces))
    if args['--labels'] is not None:
        label_field = args['--label-field']
        logger.info("Reading label file {0}...".format(args['--labels']))
        title2labels, label2ids = create_label_map(
            mwcli.files.reader(args['--labels']), lang, label_field)
        logger.info("Label2ids: {0}".format(label2ids))
    else:
        title2labels = None

    if len(args['--namespace']) == 0:
        namespaces = None
    else:
        namespaces = [int(v) for v in args['--namespace']]
    min_line = int(args['--min-line'])
    return {
        'forbidden_namespaces': forbidden_namespaces,
        'title2labels': title2labels,
        'namespaces': namespaces,
        'min_line': min_line}


def create_label_map(f, lang, label_field):
    label2ids = {}
    title2labels = {}
    for line in f:
        ob = json.loads(line)

        # Get title
        if lang not in ob['sitelinks']:
            continue
        else:
            title = ob['sitelinks'][lang]

        # Get labels
        label_ids = set()
        for label in ob[label_field]:
            if label not in label2ids:
                label2ids[label] = len(label2ids)
            label_ids.add(label2ids[label])

        title2labels[title] = set(label_ids)

    return title2labels, label2ids


def get_siteinfo(session):
    doc = session.get(action="query", meta="siteinfo",
                      siprop=["namespaces", "namespacealiases", "general"],
                      formatversion=2)
    forbidden_namespaces = set()
    for namespace in doc['query']['namespaces'].values():
        if namespace['id'] in WikitextPreprocessor.FORBIDDEN_NAMESPACE_IDS:
            forbidden_namespaces.add(namespace['name'].lower())
            forbidden_namespaces.add(namespace['canonical'].lower())
    for namespace in doc['query']['namespacealiases']:
        if namespace['id'] in WikitextPreprocessor.FORBIDDEN_NAMESPACE_IDS:
            forbidden_namespaces.add(namespace['alias'].lower())

    return doc['query']['general']['lang'], forbidden_namespaces


streamer = mwcli.Streamer(
    __doc__,
    __name__,
    preprocess_text,
    process_args=process_args,
    file_reader=mwcli.Streamer.read_xml,
    line_writer=mwcli.Streamer.write_line
)

main = streamer.main
