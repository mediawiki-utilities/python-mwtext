"""
Parse the wikitext representation of a Wikipedia page into paragraph objects.

The goal of this module is to parse wikitext into plaintext in a way that preserves
information about link offsets and section information.

The actual parsing relies on the MediaWiki Parser From Hell.  Construction of the
paragraph objects is heavily inspired by Wikipedia2Vec

 * https://github.com/earwig/mwparserfromhell
 * https://github.com/wikipedia2vec/wikipedia2vec

"""
import mwparserfromhell


DEFAULT_FORBIDDEN_SECTIONS = [
    "bibliography",
    "citations",
    "external links",
    "further reading",
    "other uses",
    "references",
    "see also",
    "sources",
]

DEFAULT_FORBIDDEN_LINK_PREFIXES = [
    "file:",
    "image:",
]


class WikitextPreprocessorMwpfh:

    def __init__(
        self,
        forbidden_link_prefixes=DEFAULT_FORBIDDEN_LINK_PREFIXES,
        forbidden_sections=DEFAULT_FORBIDDEN_SECTIONS,
        include_tag_tokens=False,
        preprocess_func=lambda x: x,
    ):
        self.forbidden_link_prefixes = forbidden_link_prefixes
        self.forbidden_sections = forbidden_sections
        self.include_tag_tokens = include_tag_tokens
        self.preprocess_func = preprocess_func
        self._reset()

    def _reset(self):
        self._section_idx = 0
        self._section_name = "Introduction"
        self._skipping_section = False
        self._current_text = ""
        self._current_links = []

    def _parse_heading_node(self, node):
        if node.level == 2:
            self._section_name = node.title.strip_code().strip()
            if self._section_name.lower() in self.forbidden_sections:
                self._skipping_section = True
            else:
                self._section_idx += 1
                self._skipping_section = False

    def _parse_tag_node(self, node):

        if not node.contents:
            return

        if node.tag in ('b', 'i', 'u'):
            text = node.contents.strip_code()
            self._current_text += self.preprocess_func(text)
        else:
            if self.include_tag_tokens:
                text = "<{}>".format(node.tag.strip_code().strip())
                self._current_text += self.preprocess_func(text)

    def _parse_external_link_node(self, node):
        if not node.title:
            return
        text = node.title.strip_code()
        self._current_text += self.preprocess_func(text)

    def _parse_wikilink_node(self, node):
        """docs on link structure: https://en.wikipedia.org/wiki/Help:Link"""
        title = node.title.strip_code().strip()

        # skip self links
        if title.startswith("#"):
            return

        if title.startswith(':'):
            title = title[1:]

        if not title:
            return

        # normalize
        title = title[0].upper() + title[1:].replace(' ', '_')

        # remove links to page sections
        title = title[:title.index("#")] if "#" in title else title

        if node.text:
            text = node.text.strip_code()
            # e.g. https://en.wikipedia.org/wiki/Wikipedia:Extended_image_syntax
            if any([
                title.lower().startswith(prefix)
                for prefix in self.forbidden_link_prefixes
            ]):
                return
        else:
            text = node.title.strip_code()

        text = self.preprocess_func(text)
        start = len(self._current_text)
        self._current_text += text
        end = len(self._current_text)
        self._current_links.append((title, text, start, end))

    def _parse_text_node(self, node):

        paragraphs_local = []
        for (n, text) in enumerate(node.split('\n')):
            if n == 0:
                self._current_text += self.preprocess_func(text)
            else:
                if self._current_text and not self._current_text.isspace():
                    paragraphs_local.append([
                        self._current_text,
                        self._current_links,
                        self._section_idx,
                        self._section_name])

                self._current_text = self.preprocess_func(text)
                self._current_links = []

        return paragraphs_local

    def process(self, text):

        self._reset()
        wikicode = mwparserfromhell.parse(text)
        paragraphs = []

        for node_idx, node in enumerate(wikicode.nodes):

            if not self._skipping_section:
                if isinstance(node, mwparserfromhell.nodes.Text):
                    paragraphs_local = self._parse_text_node(node)
                    paragraphs.extend(paragraphs_local)
                elif isinstance(node, mwparserfromhell.nodes.Wikilink):
                    self._parse_wikilink_node(node)
                elif isinstance(node, mwparserfromhell.nodes.ExternalLink):
                    self._parse_external_link_node(node)
                elif isinstance(node, mwparserfromhell.nodes.Tag):
                    self._parse_tag_node(node)

            if isinstance(node, mwparserfromhell.nodes.Heading):
                # this is the only place that can change _skipping_section
                self._parse_heading_node(node)

        if self._current_text and not self._current_text.isspace():
            paragraphs.append([
                self._current_text,
                self._current_links,
                self._section_idx,
                self._section_name])

        return paragraphs
