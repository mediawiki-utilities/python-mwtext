from .content_transformer import ContentTransformer
from . import util
import re
import itertools
from deltas.tokenizers import lexicon
from deltas.tokenizers import cjk_tokenization

strip_wikitext = [
    r"<!--.*?-->",  # no commented out text
    r"{{.*?}}",  # no templates
    r"&[a-z]+;",  # No entities
    r"<ref[^<>]*>[^<]*<\/ref>",  # No reference content or ref tags
    r"<[^>]*>",  # No tags, but leave the content
    r"\[" + lexicon.url + r"\]",  # No external links without display text
    lexicon.url,  # No bare external links either
    r"\{\{[^\}]+\}\}",  # No templates
    r"\{\|[^\}\|]+\|\}",  # No tables
    r"(^|\n);+[^\n]+",  # Definition lists terms
    r"\n\s*\|[^\n]+",  # No template arguments
    r"'''?"  # No bold or italics
]

# this is already take care of by removing external link in strip_wikitext
# see line lexicon.url, and is also giving an error :
# "error: invalid group reference 5 at position 1"
# then [https://mediawiki.org MediaWiki] becomes [MediaWiki]
#
# https://www.mediawiki.org/wiki/Help:Links
# External links with display text
# (re.compile(r"\[" + lexicon.url + r"( ([^\]]+))?\]"), r"\5"),

replace_res = [
    # Replace headers with a paragraph break
    (re.compile(r"(^|\n)==+[^=]+==+"), "\n\n"),
    # Wiki links without display text
    (re.compile(r"\[\[([^\]\|]+)\]\]"), r"\1"),
    # Wiki links with display text
    (re.compile(r"\[\[([^\]\|]+)\|([^\]]+)\]\]"), r"\2"),
    # Replace numbers with 'anumber'
    (re.compile(lexicon.number), "anumber")
]

# added "anumber" + "|" as in korean test the numbers were not extracted
# eg. [[1944년]] became 'anumber년' (previously it was only '년')
# now : 'anumber', '년'
word_or_cjk = re.compile(lexicon.word + "|" + lexicon.cjk_word)


class Wikitext2Words(ContentTransformer):

    def __init__(self, hidden_link_namespace_names, CJK=False):
        forbidden_link_re = \
            r"\[\[(" + \
            "|".join(hidden_link_namespace_names).lower() + \
            r"):[^\]]+\]\]"
        self.strip_regex = re.compile(
            "|".join(strip_wikitext + [forbidden_link_re]))
        self.replace_regexs = replace_res
        self.CJK = CJK

    def transform(self, content):
        """
        Converts wikitext into a cleaned up list of words.
        """
        return self._extract_words(content)

    @classmethod
    def from_siteinfo(cls, siteinfo, *args, **kwargs):
        hidden_link_namespace_names = \
            util.generate_non_link_namespace_names(siteinfo)
        return cls(hidden_link_namespace_names, *args, **kwargs)

    def _extract_words(self, text):
        # Strip non-content content
        stripped_text = re.sub(self.strip_regex, "", text.lower())

        # Process links and stuff.
        for replace_regex, replacement in self.replace_regexs:
            stripped_text = re.sub(replace_regex, replacement, stripped_text)

        extracted_words = []
        for match in re.finditer(word_or_cjk, stripped_text):
            extracted_words.append(match.group(0))

        # this must be done othwerwise '三之丸は比高6メートルほどの' ->
        # '三之丸は比高anumberメートルほどの' and not
        # ['三之丸は比高', 'anumber', 'メートルほどの']
        # filter function is used as 'anumberメートルほどの'
        # becomes ['', 'anumber', 'メートルほどの']
        # https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-list-of-lists
        # https://stackoverflow.com/questions/30933216/split-by-regex-without-resulting-empty-strings-in-python
        extracted_words = [re.split('(anumber)', word) for word in extracted_words] # noqa
        extracted_words = list(itertools.chain.from_iterable(extracted_words))
        extracted_words = list(filter(None, extracted_words))

        if self.CJK is True:
            joined_text = "".join(extracted_words)
            language = cjk_tokenization.lng_decision(
                joined_text, lexicon.CJK_LEXICON, lng_frac_par=0.25)

            if language != 'other':
                for i in range(len(extracted_words))[::-1]:
                    processed_word = cjk_tokenization.CJK_tokenization(
                                            extracted_words[i], language)
                    extracted_words[i:i+1] = [word for word in processed_word]

        return extracted_words
