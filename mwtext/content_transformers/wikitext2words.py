from .content_transformer import ContentTransformer
from . import util
import re
from deltas.tokenizers import lexicon

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

replace_res = [
    # Replace headers with a paragraph break
    (re.compile(r"(^|\n)==+[^=]+==+"), "\n\n"),
    # External links with display text
    (re.compile(r"\[" + lexicon.url + r"( ([^\]]+))?\]"), r"\5"),
    #  Wiki links without display text
    (re.compile(r"\[\[([^\]\|]+)\]\]"), r"\1"),
    # Wiki links with display text
    (re.compile(r"\[\[([^\]\|]+)\|([^\]]+)\]\]"), r"\2"),
    # Replace numbers with 'anumber'
    (re.compile(lexicon.number), "anumber")
]

word_or_cjk = re.compile(lexicon.word + "|" + lexicon.cjk_word)


class Wikitext2Words(ContentTransformer):

    def __init__(self, hidden_link_namespace_names):
        forbidden_link_re = \
            r"\[\[(" + \
            "|".join(hidden_link_namespace_names).lower() + \
            r"):[^\]]+\]\]"
        self.strip_regex = re.compile(
            "|".join(strip_wikitext + [forbidden_link_re]))
        self.replace_regexs = [(re.compile(p), r) for p, r in replace_res]

    def transform(self, content):
        """
        Converts wikitext into a cleaned up list of words.
        """
        return list(self._extract_words(content))

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

        for match in re.finditer(word_or_cjk, stripped_text):
            yield match.group(0)
