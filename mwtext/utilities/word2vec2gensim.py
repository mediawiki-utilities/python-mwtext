r"""
``$ mwtext word2vec2gensim -h``
::

    Converts a word2vec formatted file to a gensim-compatible binary
    containing the same vectors.

    Usage:
        word2vec2gensim (-h|--help)
        word2vec2gensim <input> <output>
                        [--limit=<num>]
                        [--verbose] [--debug]

    Options:
        -h|--help           Print this documentation
        <input>             The path to a word2vec formatted file (can
                            be bz2 or gz compressed)
        <output>            The name of the main output file to write.
                            A second output file will be written with
                            ".vectors.numpy" added to the filename provided.
        --limit=<num>       Set a limit on the number of words that should be
                            loaded from the word2vec formatted file.  Unlimited
                            if not specified.
        --verbose           Print progress information to stderr.  Kind of a
                            mess when running multi-threaded.
        --debug             Print debug logs.
"""
import logging

import docopt
from gensim.models import KeyedVectors

logger = logging.getLogger(__name__)


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    logging.basicConfig(
        level=logging.INFO if not args['--debug'] else logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )

    input_path = args['<input>']
    output_path = args['<output>']
    limit = int(args['--limit']) if args['--limit'] is not None else None
    verbose = args['--verbose']

    word2vec2gensim(input_path, limit, output_path, verbose)


def word2vec2gensim(input_path, limit, output_path, verbose):
    model = KeyedVectors.load_word2vec_format(input_path, limit=limit)
    model.save(output_path)
