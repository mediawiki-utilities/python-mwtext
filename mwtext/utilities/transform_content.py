r"""
``$ mwtext transform_content -h``
::

    Transforms content from MediaWiki XML dumps.  Outputs `revdocs` but
    replaces text field with a transformed_content field.

    Usage:
        transform_content (-h|--help)
        transform_content <content-transformer> [<input-file>...]
                          [--include=<func>]
                          [--param=<kv>]...
                          [--include-redirects]
                          [--namespace=<id>]...
                          [--content-model=<mdl>]...
                          [--min-content-length=<chrs>]
                          [--siteinfo=<path>]
                          [--wiki-host=<url>]
                          [--threads=<num>] [--output=<path>]
                          [--compress=<type>] [--verbose] [--debug]

    Options:
        -h --help           Print this documentation
        <content-transformer>  Path to a content transformer to construct and
                               execute.
        <input-file>        The path to a MediaWiki XML Dump file
                            [default: <stdin>]
        -p --param=<kv>     A parameter to pass to the <content-transformer>.
                            <kv> takes the form of "<key>=<value>" where <key>
                            is a legal python argument name and <value> is JSON
                            encoded data.
        --include=<func>    Classpath for a module containing an "include"
                            to run against each revision to determine if it
                            should be processed. If set, only revisions for
                            which the function returns true will be included.
        --include-redirects  If set, include redirects
        --namespace=<id>    Limit processing to this namespace.  Can be
                            repeated to select for multiple namespaces.
        --content-model=<mdl>  Limit to this content model.  Can be repeated to
                               match multiple different content types.
        --min-content-length=<chrs>  Limit to pages with at least <len>
                                     characters of content.
        --siteinfo=<path>   The path to a file containing a relevant siteinfo
                            document JSON encoded.
        --wiki-host=<url>   The hostname of the MediaWiki install to query for
                            siteinfo.  Note that this argument is ignored when
                            '--siteinfo' is specified.
        --threads=<num>     If a collection of files are provided, how many
                            processor threads?  Note that this actually uses
                            subprocesses and will parallelize over CPU
                            [default: <cpu_count>]
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
import yamlconf

from ..filter_functions import all_pages_and_revisions
from .util import get_siteinfo, is_relevant_page

logger = logging.getLogger(__name__)
REDIRECT_RE = re.compile("#redirect", re.I)


def transform_content(
        dump, transformer, include_criteria=None, allowed_namespaces=None,
        allowed_content_models=None, include_redirects=False,
        min_content_length=None, verbose=False):

    namespace_id_map = {ns.id: ns.name for ns in dump.site_info.namespaces}

    for page in dump:
        if verbose:
            sys.stderr.write(page.title + ": ")
            sys.stderr.flush()

        for revision in page:
            relevant = is_relevant_page(
                page, revision, include_criteria=include_criteria,
                allowed_namespaces=allowed_namespaces,
                allowed_content_models=allowed_content_models,
                include_redirects=include_redirects,
                min_content_length=min_content_length)
            if not relevant:
                continue

            transformed_doc = transformer.transform(revision.text)
            rev_doc = revision.to_json()
            rev_doc['page'] = page.to_json()
            rev_doc['page']['page_name'] = \
                format_page_name(page, namespace_id_map)
            del rev_doc['text']
            rev_doc['transformed_content'] = transformed_doc
            yield rev_doc

            if verbose:
                sys.stderr.write(".")
                sys.stderr.flush()

        if verbose:
            sys.stderr.write("\n")
            sys.stderr.flush()


def format_page_name(page, namespace_id_map):
    if page.namespace == 0:
        return page.title
    else:
        return namespace_id_map[page.namespace] + ":" + page.title


def process_args(args):
    try:
        Transformer = yamlconf.import_path(args['<content-transformer>'])
    except ImportError:
        Transformer = yamlconf.import_path(
            "mwtext.content_transformers." + args['<content-transformer>'])
    if args['--siteinfo'] is not None:
        siteinfo = json.load(open(args['--siteinfo']))['query']
    else:
        logger.info("Gathering siteinfo from {0}".format(args['--wiki-host']))
        session = mwapi.Session(
            args['--wiki-host'], user_agent="mwtext transform_content")
        siteinfo = get_siteinfo(session)

    kwarg_params = {}
    for kv in args['--param']:
        key, value = process_param(kv)
        kwarg_params[key] = value

    transformer = Transformer.from_siteinfo(siteinfo, **kwarg_params)

    if args['--include']:
        try:
            include_criteria = yamlconf.import_path(args['--include'])
        except ImportError:
            include_criteria = yamlconf.import_path(
                "mwtext.filter_functions." + args['--include'])
    else:
        include_criteria = all_pages_and_revisions

    include_redirects = bool(args['--include-redirects'])

    if len(args['--namespace']) == 0:
        allowed_namespaces = None
    else:
        allowed_namespaces = set(int(v) for v in args['--namespace'])

    if len(args['--content-model']) == 0:
        allowed_content_models = None
    else:
        allowed_content_models = set(cm for cm in args['--content-model'])

    min_content_length = int(args['--min-content-length'])

    return {
        'transformer': transformer,
        'include_criteria': include_criteria,
        'include_redirects': include_redirects,
        'allowed_namespaces': allowed_namespaces,
        'allowed_content_models': allowed_content_models,
        'min_content_length': min_content_length
    }


def process_param(kv):
    key, value_str = kv.split("=", 1)
    return key, json.loads(value_str)


streamer = mwcli.Streamer(
    __doc__,
    __name__,
    transform_content,
    process_args=process_args,
    file_reader=mwcli.Streamer.read_xml,
    line_writer=mwcli.Streamer.write_json
)

main = streamer.main
