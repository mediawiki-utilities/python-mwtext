"""
Parse the wikitext representation of a Wikipedia page into paragraph objects.

The goal of this module is to parse wikitext into plaintext in a way that preserves
information about link offsets and section information.

The actual parsing relies on the MediaWiki Parser From Hell.  Construction of the
paragraph objects is heavily inspired by Wikipedia2Vec

 * https://github.com/earwig/mwparserfromhell
 * https://github.com/wikipedia2vec/wikipedia2vec

"""
from typing import Callable, Iterable
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
    "#",       # self links
    ":",       # used mostly for image, category, or interlanguage links
    "file:",
    "image:",
]

DEFAULT_ALLOWED_TAGS = [
    "b",
    "i",
    "u",
]


class WikitextPreprocessorMwpfh:

    """Wikitext Preprocessor using MediaWiki Parser From Hell

    Args:
        forbidden_link_prefixes (Iterable[str]): ignore links with these
            (case insensitive) prefixes.
        forbidden_sections (Iterable[str]): skip sections with these
            (case insensitive) titles.
        allowed_tags (Iterable[str]): include the contents of these tags
        include_disallowed_tag_tokens (bool): if True, include a single
            token for tags that are not in the `allowed_tags` list.  For
            example a <table> token to represent all the markup of a table.
        preprocess_func (Callable[[str], str]): arbitary callable that will
            be called on all the test pieces included in the output.
        canonicalize_link_targets (bool): if True, uppercase the first character
            of link targets and replace spaces with underscores
    """
    def __init__(
        self,
        forbidden_link_prefixes: Iterable[str] = DEFAULT_FORBIDDEN_LINK_PREFIXES,
        forbidden_sections: Iterable[str] = DEFAULT_FORBIDDEN_SECTIONS,
        allowed_tags: Iterable[str] = DEFAULT_ALLOWED_TAGS,
        include_disallowed_tag_tokens: bool = False,
        preprocess_func: Callable[[str], str] = lambda x: x,
        canonicalize_link_targets: bool = False
    ):
        self.forbidden_link_prefixes = forbidden_link_prefixes
        self.forbidden_sections = forbidden_sections
        self.allowed_tags = allowed_tags
        self.include_disallowed_tag_tokens = include_disallowed_tag_tokens
        self.preprocess_func = preprocess_func
        self.canonicalize_link_targets = canonicalize_link_targets
        self._reset()

    def _reset(self):
        self._section_idx = 0
        self._section_name = "Introduction"
        self._skipping_section = False
        self._current_text = ""
        self._current_links = []

    def _parse_heading_node(self, node: mwparserfromhell.nodes.Heading) -> None:
        """Parse heading node.

        If this is a level 2 node (== heading ==), set the section name and decide
        if we are skipping this section.
        """
        if node.level == 2:
            self._section_name = node.title.strip_code().strip()
            if self._section_name.lower() in self.forbidden_sections:
                self._skipping_section = True
            else:
                self._section_idx += 1
                self._skipping_section = False

    def _parse_tag_node(self, node: mwparserfromhell.nodes.Tag) -> None:
        """Parse tag node.

        For allowed tags, include the contents of the tag in the text stream.
        For disallowed tags, optionally include a token to indicate the presence
        of the tag but not the contents (e.g. include a single <table> token in the
        text stream but nothing from the table markdown itself).
        """
        # never include tags with no content
        if len(node.contents) == 0:
            return

        # add the contents of allowed tags to the text stream
        if node.tag in self.allowed_tags:
            text = node.contents.strip_code().strip()
            self._current_text += self.preprocess_func(text)

        # optionally add a single token for disallowed tags
        else:
            if self.include_disallowed_tag_tokens:
                text = "<{}>".format(node.tag.strip_code().strip())
                self._current_text += self.preprocess_func(text)

    def _parse_external_link_node(self, node: mwparserfromhell.nodes.ExternalLink):
        """Parse external link node.

        Include the title of external links in the text stream.
        """
        if node.title is None:
            return
        text = node.title.strip_code().strip()
        self._current_text += self.preprocess_func(text)

    def _parse_wikilink_node(self, node: mwparserfromhell.nodes.Wikilink):
        """Parse wikilink nodes.

        basic cases:,
          [[target_page]]
            node.title = "target_page", node.text = None
          [[target_page|anchor_text]]
            node.title = "target_page", node.text = "anchor_text"

        docs on link structure: https://en.wikipedia.org/wiki/Help:Link
        """
        target = node.title.strip_code().strip()

        if len(target) == 0:
            return

        if any([
            target.lower().startswith(prefix)
            for prefix in self.forbidden_link_prefixes
        ]):
            return

        # remove section specific component
        target = target[:target.index("#")] if "#" in target else target

        # normalize (TODO: check the format the SQL dumps use)
        if self.canonicalize_link_targets:
            target = target[0].upper() + target[1:].replace(" ", "_")

        # get anchor text
        anchor = node.text.strip_code().strip() if node.text is not None else target

        # package up link
        anchor = self.preprocess_func(anchor)
        start = len(self._current_text)
        self._current_text += anchor
        end = len(self._current_text)
        self._current_links.append((target, anchor, start, end))

    def _parse_text_node(self, node: mwparserfromhell.nodes.Text):
        """Parse text node.

        Create a list of paragraph objects from a text node.
        """
        paragraphs_local = []
        for (ii, text) in enumerate(node.split("\n")):
            if ii == 0:
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

    def process(self, text: str):
        """Process wikitext markup into a list of paragraph objects.

        TODO: Describe paragraph object format when finalized.
        """
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
