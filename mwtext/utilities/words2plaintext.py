"""
``$ mwtext words2plaintext -h``
::

    Converts a "words" style transformed content revdocs into a dataset of
    plaintext and (if specified) labels for processing by fasttext,
    word2vec, and other word embedding algorithms.

    Usage:
        words2plaintext (-h|--help)
        words2plaintext [<input-file>...]
                        [--labels=<path>] [--title-lang=<l>] [--label-field=<k>]
                        [--output=<path>] [--verbose] [--debug]

  Options:
      -h --help         Print this documentation
      <input-file>      The path to a collection of revdocs containing
                        'transformed_content' in the form of "words".
      --labels=<path>   The path to a file containing label data for
                        associating with text.  If not set, no labels will
                        be included.
      --title-lang=<lang>  The lang code to use to identify the title from
                           sitelinks in the labeled dataset.
      --label-field=<k>   The field to examine within the labels file
                          [default: taxo_labels]
      --output=<path>     A path to write output to [default: <stdout>]
"""
import json
import sys
import logging

import docopt
import mwcli.files

logger = logging.getLogger(__name__)


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    logging.basicConfig(
        level=logging.INFO if not args['--debug'] else logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )
    if len(args['<input-file>']) == 0:
        input_files = [sys.stdin]
    else:
        input_files = [open(p) for p in args['<input-file>']]

    if args['--labels'] is not None:
        title_lang = args['--title-lang']
        label_field = args['--label-field']
        logger.info("Reading label file {0}...".format(args['--labels']))
        page_name2labels, label2ids = create_label_map(
            mwcli.files.reader(args['--labels']), title_lang, label_field)
        logger.debug("Label2ids: {0}".format(label2ids))
    else:
        page_name2labels = None

    if args['--output'] == "<stdout>":
        output = sys.stdout
    else:
        output = open(args['--output'], "w")

    verbose = args['--verbose']

    run(input_files, page_name2labels, output, verbose)


def run(input_files, page_name2labels, output, verbose):

    for input_file in input_files:
        for line in input_file:
            rev_doc = json.loads(line)
            page_name = rev_doc['page']['page_name']
            if page_name2labels is not None:
                if page_name not in page_name2labels:
                    logger.debug("Skipping {0} because it has no labels."
                                 .format(page_name))
                    continue
                else:
                    labels = page_name2labels[page_name]
            else:
                labels = []
            words = rev_doc['transformed_content']
            output.write(format_words_and_labels(words, labels))
            output.write("\n")


def format_words_and_labels(words, labels):
    return " ".join(words) + format_labels(labels)


def format_labels(labels):
    if len(labels) > 0:
        return " " + " ".join("__label__{0}".format(label)
                              for label in labels)
    else:
        return ""


def create_label_map(f, title_lang, label_field):
    label2ids = {}
    page_name2labels = {}
    for line in f:
        ob = json.loads(line)

        # Get title
        if title_lang == "wikidata":
            if ob['qid'] is None:
                continue
            else:
                page_name = ob['qid']
        else:
            if title_lang not in ob['sitelinks']:
                continue
            else:
                page_name = ob['sitelinks'][title_lang]

        # Get labels
        label_ids = set()
        for label in ob[label_field]:
            if label not in label2ids:
                label2ids[label] = len(label2ids)
            label_ids.add(label2ids[label])

        page_name2labels[page_name] = set(label_ids)

    return page_name2labels, label2ids
