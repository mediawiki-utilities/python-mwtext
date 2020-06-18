from .content_transformer import ContentTransformer
from . import util
import re

PLAIN_PROTO = [r'bitcoin', r'geo', r'magnet', r'mailto', r'news', r'sips?',
               r'tel', r'urn']
SLASHED_PROTO = [r'', r'ftp', r'ftps', r'git', r'gopher', r'https?', r'ircs?',
                 r'mms', r'nntp', r'redis', r'sftp', r'ssh', r'svn', r'telnet',
                 r'worldwind', r'xmpp']
ADDRESS = r'[^\s/$.?#].[^\s]*'

URL_RE = (
    r'(' +  # noqa
        r'(' + '|'.join(PLAIN_PROTO) + r')\:|' +  # noqa
        r'((' + '|'.join(SLASHED_PROTO) + r')\:)?\/\/' +
    r')' + ADDRESS
)

STRIP_WIKITEXT_REs = [
    r"<!--.*?-->",  # no commented out text
    r"{{.*?}}",  # no templates
    r"&[a-z]+;",  # No entities
    r"<ref[^<>]*>[^<]*<\/ref>",  # No reference content or ref tags
    r"<[^>]*>",  # No tags, but leave the content
    r"\[" + URL_RE + r"\]",  # No external links without display text
    URL_RE,  # No bare external links either
    r"\{\{[^\}]+\}\}",  # No templates
    r"\{\|[^\}\|]+\|\}",  # No tables
    r"(^|\n);+[^\n]+",  # Definition lists terms
    r"\n\s*\|[^\n]+",  # No template arguments
    r"'''?"  # No bold or italics
]

# Matches 10, 10.2, 3.123e10, 100,000,000, etc.
NUMBER_RE = r"\b[0-9][0-9\.\,]*(e[0-9]+)?s?\b"

REPLACE_REs = [
    # Replace headers with a paragraph break
    (re.compile(r"(^|\n)==+[^=]+==+"), "\n\n"),
    # External links with display text
    (re.compile(r"\[" + URL_RE + r"( ([^\]]+))?\]"), r"\5"),
    #  Wiki links without display text
    (re.compile(r"\[\[([^\]\|]+)\]\]"), r"\1"),
    # Wiki links with display text
    (re.compile(r"\[\[([^\]\|]+)\|([^\]]+)\]\]"), r"\2"),
    # Replace numbers with 'anumber'
    (re.compile(NUMBER_RE), "anumber")
]

PARAGRAPH_SPLIT_RE = r'(\n|\n\r|\r\n)\s*(\n|\n\r|\r\n)+'

devangari_word = r'\u0901-\u0963'
arabic_word = r'\u0601-\u061A' + \
              r'\u061C-\u0669' + \
              r'\u06D5-\u06EF'
bengali_word = r'\u0980-\u09FF'
combined_word = devangari_word + arabic_word + bengali_word

WORD_RE = r'([^\W\d]|[' + combined_word + r'])' + \
          r'[\w' + combined_word + r']*' + \
          r'([\'’]([\w' + combined_word + r']+|(?=($|\s))))*'

# Matches Chinese, Japanese and Korean characters.
CJK_RE = (
    r'[' +
        r'\u4E00-\u62FF' +  # noqa Unified Ideographs
        r'\u6300-\u77FF' +
        r'\u7800-\u8CFF' +
        r'\u8D00-\u9FCC' +
        r'\u3400-\u4DFF' +  # Unified Ideographs Ext A
        r'\U00020000-\U000215FF' +  # Unified Ideographs Ext. B
        r'\U00021600-\U000230FF' +
        r'\U00023100-\U000245FF' +
        r'\U00024600-\U000260FF' +
        r'\U00026100-\U000275FF' +
        r'\U00027600-\U000290FF' +
        r'\U00029100-\U0002A6DF' +
        r'\uF900-\uFAFF' +  # Compatibility Ideographs
        r'\U0002F800-\U0002FA1F' +  # Compatibility Ideographs Suppl.
        r'\u3041-\u3096' +  # Hiragana
        r'\u30A0-\u30FF' +  # Katakana
        r'\u3400-\u4DB5' +  # Kanji
        r'\u4E00-\u9FCB' +
        r'\uF900-\uFA6A' +
        r'\u2E80-\u2FD5' +  # Kanji radicals
        r'\uFF5F-\uFF9F' +  # Katakana and Punctuation (Half Width)
        r'\u31F0-\u31FF' +  # Miscellaneous Japanese Symbols and Characters
        r'\u3220-\u3243' +
        r'\u3280-\u337F'
    r']'
)
WORD_OR_CJK_RE = re.compile(WORD_RE + "|" + CJK_RE)

PARAGRAPH_SPLIT_RE = r'(\n|\n\r|\r\n)\s*(\n|\n\r|\r\n)+'

HIDDEN_LINK_NAMESPACES = ['Category', 'Image']


class Wikitext2Words(ContentTransformer):

    def __init__(self, hidden_link_namespace_names):
        forbidden_link_re = \
            r"\[\[(" + \
            "|".join(hidden_link_namespace_names).lower() + \
            r"):[^\]]+\]\]"
        self.strip_regex = re.compile(
            "|".join(STRIP_WIKITEXT_REs + [forbidden_link_re]))
        self.replace_regexs = [(re.compile(p), r) for p, r in REPLACE_REs]

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

        for match in re.finditer(WORD_OR_CJK_RE, stripped_text):
            yield match.group(0)
