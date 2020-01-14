r"""
``$ mwtext preprocess_text -h``
::

    Converts MediaWiki XML dumps to plaintext.  One line per text chunk with
    wiki markup and punctuation cleaned up.  This utility is designed with word
    embeddings in mind.  Generally, you can expect one line per paragraph.

    Usage:
        preprocess_text (-h|--help)
        preprocess_text [<input-file>...]
			[--namespace=<id>]... [--wiki-host=<url>]
                        [--threads=<num>] [--output=<path>]
                        [--compress=<type>] [--verbose] [--debug]

    Options:
        -h|--help           Print this documentation
        <input-file>        The path to a MediaWiki XML Dump file
                            [default: <stdin>]
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
import logging
import re
import sys

import mwapi
import mwcli

from ..wikitext_preprocessor import WikitextPreprocessor

logger = logging.getLogger(__name__)
REDIRECT_RE = re.compile("#redirect", re.I)


def preprocess_text(dump, wikitext_preprocessor, namespaces=None, verbose=False):
    for page in dump:
        if namespaces and page.namespace not in namespaces:
            continue
        if verbose:
            sys.stderr.write(page.title + ": ")
            sys.stderr.flush()

        for revision in page:
            if not is_article(revision.text):
                continue
            for line in wikitext_preprocessor.process(revision.text):
                yield " ".join(line)
                if verbose:
                    sys.stderr.write(".")
                    sys.stderr.flush()

        if verbose:
            sys.stderr.write("\n")
            sys.stderr.flush()


def process_args(args):
    session = mwapi.Session(
        args['--wiki-host'], user_agent="mwtext preprocess_text")
    if len(args['--namespace']) == 0:
        namespaces = None
    else:
        namespaces = [int(v) for v in args['--namespace']]
    return {
        'wikitext_preprocessor': WikitextPreprocessor.from_session(session),
        'namespaces': namespaces}


def is_article(text):
    return not (text is None or
                len(text) < 50 or
                REDIRECT_RE.match(text))



streamer = mwcli.Streamer(
    __doc__,
    __name__,
    preprocess_text,
    process_args=process_args,
    file_reader=mwcli.Streamer.read_xml,
    line_writer=mwcli.Streamer.write_line
)

main = streamer.main
