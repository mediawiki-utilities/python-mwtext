"""
Parse the wikitext representation of a Wikipedia page into paragraph objects.

The goal of this module is to parse wikitext into plaintext in a way that preserves
information about link offsets and section information.

The actual parsing relies on the MediaWiki Parser From Hell.  Construction of the
paragraph objects is heavily inspired by Wikipedia2Vec

 * https://github.com/earwig/mwparserfromhell
 * https://github.com/wikipedia2vec/wikipedia2vec

"""
import logging
from typing import Callable, Iterable, List, Optional, Tuple
import mwparserfromhell
from mwparserfromhell.nodes import ExternalLink, Heading, Tag, Text, Wikilink


logger = logging.getLogger(__name__)


FORBIDDEN_SECTIONS = [
    "bibliography",
    "citations",
    "external links",
    "further reading",
    "other uses",
    "references",
    "see also",
    "sources",
]

FORBIDDEN_WIKILINK_PREFIXES = [
    "#",       # self links
    ":",       # used mostly for image, category, or interlanguage links
    "file:",
    "image:",
]

ALLOWED_TAGS = [
    "b",
    "i",
    "u",
]

WikilinkParser = Callable[[Wikilink], Tuple[bool, str, str]]


class WikitextPreprocessorMwpfh:

    """Wikitext Preprocessor using MediaWiki Parser From Hell

    Args:
        forbidden_wikilink_prefixes (Iterable[str]): ignore wikilinks with these
            (case insensitive) prefixes.
        forbidden_sections (Iterable[str]): skip sections with these
            (case insensitive) titles.
        allowed_tags (Iterable[str]): include the contents of these tags
        include_disallowed_tag_tokens (bool): if True, include a single
            token for tags that are not in the `allowed_tags` list.  For
            example a <table> token to represent all the markup of a table.
        canonicalize_wikilink_targets (bool): if True, uppercase the first character
            of link targets and replace spaces with underscores
        custom_wikilink_parser (Callable[[Wikilink], Tuple[bool, str, str]]):
            function that takes in a Wikilink object and returns a 3-tuple
            (keep, target, anchor) where keep determines if the link is recorded,
            target is the target page title to use and anchor is the anchor text
            to put into the text stream.  Uses _default_wikilink_parser if None.
    """
    def __init__(
        self,
        forbidden_wikilink_prefixes: Iterable[str] = FORBIDDEN_WIKILINK_PREFIXES,
        forbidden_sections: Iterable[str] = FORBIDDEN_SECTIONS,
        allowed_tags: Iterable[str] = ALLOWED_TAGS,
        include_disallowed_tag_tokens: bool = False,
        canonicalize_wikilink_targets: bool = False,
        custom_wikilink_parser: Optional[WikilinkParser] = None,
    ) -> None:
        self.forbidden_wikilink_prefixes = forbidden_wikilink_prefixes
        self.forbidden_sections = forbidden_sections
        self.allowed_tags = allowed_tags
        self.include_disallowed_tag_tokens = include_disallowed_tag_tokens
        self.canonicalize_wikilink_targets = canonicalize_wikilink_targets
        self.custom_wikilink_parser = custom_wikilink_parser
        self._reset()

    def _reset(self) -> None:
        self._section_idx = 0
        self._section_name = "Introduction"
        self._skipping_section = False
        self._current_text = ""
        self._current_wikilinks = []

    def _parse_heading_node(self, node: Heading) -> None:
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

    def _parse_tag_node(self, node: Tag) -> None:
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
            self._current_text += text

        # optionally add a single token for disallowed tags
        else:
            if self.include_disallowed_tag_tokens:
                text = "<{}>".format(node.tag.strip_code().strip())
                self._current_text += text

    def _parse_external_link_node(self, node: ExternalLink):
        """Parse external link node.

        Include the title of external links in the text stream.
        """
        if node.title is None:
            return
        text = node.title.strip_code().strip()
        self._current_text += text

    def _default_wikilink_parser(self, node: Wikilink) -> Tuple[bool, str, str]:
        """Produce (keep, target, anchor) tuple from Wikilink node.

        Take a Wikilink node and decide to keep or not.  If it's kept, produce
        a target (target page title) and anchor (anchor text).  The target will
        be recorded in the wikilinks attribute of a paragraph and the anchor
        will be added to the text stream.
        """
        target = node.title.strip_code().strip()

        if len(target) == 0:
            return (False, "", "")

        if any([
            target.lower().startswith(prefix)
            for prefix in self.forbidden_wikilink_prefixes
        ]):
            return (False, "", "")

        # remove section specific component
        target = target[:target.index("#")] if "#" in target else target

        anchor = node.text.strip_code().strip() if node.text is not None else target

        # normalize (TODO: check the format the SQL dumps use)
        if self.canonicalize_wikilink_targets:
            target = target[0].upper() + target[1:].replace(" ", "_")

        return (True, target, anchor)

    def _parse_wikilink_node(self, node: Wikilink) -> None:
        """Parse wikilink nodes.

        basic cases:,
          [[target_page]]
            node.title = "target_page", node.text = None
          [[target_page|anchor_text]]
            node.title = "target_page", node.text = "anchor_text"

        docs on link structure: https://en.wikipedia.org/wiki/Help:Link
        """

        # if there was a custom wikilink parser passed in
        if self.custom_wikilink_parser is not None:
            wikilink_parser = self.custom_wikilink_parser
        else:
            wikilink_parser = self._default_wikilink_parser

        keep, target, anchor = wikilink_parser(node)
        if keep:
            start = len(self._current_text)
            self._current_text += anchor
            end = len(self._current_text)
            self._current_wikilinks.append((target, anchor, start, end))

    def _parse_text_node(self, node: Text) -> List[dict]:
        """Parse text node.

        Create a list of paragraph objects from a text node.
        """
        paragraphs_local = []
        for (ii, text) in enumerate(node.split("\n")):
            if ii == 0:
                self._current_text += text
            else:
                if self._current_text and not self._current_text.isspace():
                    paragraphs_local.append({
                        "text": self._current_text,
                        "wikilinks": self._current_wikilinks,
                        "section_idx": self._section_idx,
                        "section_name": self._section_name})

                self._current_text = text
                self._current_wikilinks = []

        return paragraphs_local

    def process(self, text: str) -> List[dict]:
        """Process wikitext markup into a list of paragraph objects.

        TODO: Describe paragraph object format when finalized.
        """
        self._reset()
        wikicode = mwparserfromhell.parse(text)
        paragraphs = []
        do_expensive_logging = logger.isEnabledFor(logging.WARN)

        for node_idx, node in enumerate(wikicode.nodes):

            if do_expensive_logging:
                logger.warning("node=%s, %s", type(node), repr(node))

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
            paragraphs.append({
                "text": self._current_text,
                "wikilinks": self._current_wikilinks,
                "section_idx": self._section_idx,
                "section_name": self._section_name})

        return paragraphs
