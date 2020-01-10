r"""
``$ mwtext preprocess_text -h``
::

    Converts MediaWiki XML dumps to plaintext.  One line per text chunk with
    wiki markup and punctuation cleaned up.  This utility is designed with word
    embeddings in mind.  Generally, you can expect one line per paragraph.

    Usage:
        preprocess_text (-h|--help)
        preprocess_text [<input-file>...] [--language=<lang>]
                        [--threads=<num>] [--output=<path>]
                        [--compress=<type>] [--verbose] [--debug]

    Options:
        -h|--help           Print this documentation
        <input-file>        The path to a MediaWiki XML Dump file
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
import logging
import sys

import mwapi
import mwcli

from ..wikitext_preprocessor import WikitextPreprocessor

logger = logging.getLogger(__name__)


def preprocess_text(dump, wikitext_preprocessor, verbose=False):
    for page in dump:
        if verbose:
            sys.stderr.write(page.title + ": ")
            sys.stderr.flush()

        for revision in page:
            for line in wikitext_preprocessor.process(revision.text):
                yield line
                if verbose:
                    sys.stderr.write(".")
                    sys.stderr.flush()

        if verbose:
            sys.stderr.write("\n")
            sys.stderr.flush()


def process_args(args):
    session = mwapi.Session(
        args['--wiki-host'], user_agent="mwtext preprocess_text")
    return {
        'wikitext_preprocessor': WikitextPreprocessor.from_session(session)}


streamer = mwcli.Streamer(
    __doc__,
    __name__,
    preprocess_text,
    process_args=process_args,
    file_reader=mwcli.Streamer.read_xml,
    file_writer=mwcli.Streamer.write_plain
)

main = streamer.main
