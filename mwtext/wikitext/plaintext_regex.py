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
    r"<ref[^<]*<\/ref>",  # No references
    r"<[^>]*>",  # No tags
    r"\[" + URL_RE + r"\]",  # No external links without display text
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


class WikitextToPlaintextRegexTransformer:
    FORBIDDEN_NAMESPACE_IDS = (6, 14)

    def __init__(self, forbidden_link_prefixes):
        forbidden_link_re = \
            r"\[\[(" + \
            "|".join(forbidden_link_prefixes).lower() + \
            r"):[^\]]+\]\]"
        self.strip_regex = re.compile(
            "|".join(STRIP_WIKITEXT_REs + [forbidden_link_re]))
        self.replace_regexs = [(re.compile(p), r) for p, r in REPLACE_REs]
        self.token_regex = re.compile(WORD_OR_CJK_RE)

    def process(self, text):
        stripped_text = re.sub(self.strip_regex, "", text.lower())
        for replace_regex, replacement in self.replace_regexs:
            stripped_text = re.sub(replace_regex, replacement, stripped_text)

        for paragraph in re.split(PARAGRAPH_SPLIT_RE, stripped_text):
            paragraph_tokens = [
                match.group(0)
                for match in re.finditer(self.token_regex, paragraph)]
            if len(paragraph_tokens) > 0:
                yield paragraph_tokens
