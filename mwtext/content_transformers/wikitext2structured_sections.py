"""
Parse the wikitext representation of a Wikipedia page into paragraph objects.

The goal of this module is to parse wikitext into plaintext in a way that preserves
information about link offsets and section information.  The default settings are
geared towards extracting the offsets for every internal link (i.e. links that lead
to other main space pages in the same wiki).

The actual parsing relies on the MediaWiki Parser From Hell.  Construction of the
paragraph objects is heavily inspired by the approach taken in Wikipedia2Vec

 * https://github.com/earwig/mwparserfromhell
 * https://github.com/wikipedia2vec/wikipedia2vec


known issues:

 * links inside tags are put into text stream but not link list
   e.g. ''[[Photometria]]''


"""
import logging
from typing import Callable, Iterable, List, Optional, Tuple
from .content_transformer import ContentTransformer
import mwparserfromhell
from mwparserfromhell.nodes import ExternalLink, Heading, Tag, Text, Wikilink
from mwparserfromhell.wikicode import Wikicode


logger = logging.getLogger(__name__)


FORBIDDEN_WIKILINK_PREFIXES = [
    "file:",
    "image:",
    "category:",
]

ALLOWED_TAGS = [
    "b",
    "i",
    "u",
]

WikilinkParser = Callable[[Wikilink], Tuple[bool, bool, str, str]]


class Wikitext2StructuredSections(ContentTransformer):

    """Wikitext -> Structured Sections using MediaWiki Parser From Hell

    Args:
        forbidden_wikilink_prefixes (Iterable[str]): ignore wikilinks with
            these (case insensitive) prefixes.
        allowed_tags (Iterable[str]): include the contents of these tags
        include_disallowed_tag_tokens (bool): if True, include a single
            token for tags that are not in the `allowed_tags` list.  For
            example a <table> token to represent all the markup of a table.
        custom_wikilink_parser (Callable[[Wikilink], Tuple[bool, bool, str,
                str]]):
            function that takes in a Wikilink object and returns a 4-tuple
            (add_link, add_text, target, anchor) where,
              * add_link: determines if link is added to link list
              * add_text: determines if anchor is added to text stream
              * target: target page title to use
              * anchor: anchor text to use
            Uses _default_wikilink_parser if None.
    """
    def __init__(
        self,
        forbidden_wikilink_prefixes: Iterable[str] = FORBIDDEN_WIKILINK_PREFIXES,
        allowed_tags: Iterable[str] = ALLOWED_TAGS,
        include_disallowed_tag_tokens: bool = False,
        custom_wikilink_parser: Optional[WikilinkParser] = None,
        include_external_link_anchors: bool = True,
    ) -> None:
        self.forbidden_wikilink_prefixes = forbidden_wikilink_prefixes
        self.allowed_tags = allowed_tags
        self.include_disallowed_tag_tokens = include_disallowed_tag_tokens
        self.custom_wikilink_parser = custom_wikilink_parser
        self.include_external_link_anchors = include_external_link_anchors

    def transform(self, wikitext: str) -> dict:
        """Process wikitext into structured data.

        This transformer takes in wikitext and produces structured data.
        It is designed under the assumption that the input is a full Wikipedia
        page of wikitext markup.  However, you can still pass in snippets of
        wikitext and get mostly sensible results.

        Args:
            wikitext (str): wikitext markup

        Returns:
            structured (dict): structured page data

        """
        parse_state = {
            "section_idx": 0,
            "section_name": "Introduction",
            "current_text": "",
            "current_wikilinks": [],
        }

        wikicode = mwparserfromhell.parse(wikitext)
        paragraphs = []
        do_expensive_logging = logger.isEnabledFor(logging.DEBUG)

        for node_idx, node in enumerate(wikicode.nodes):

            if do_expensive_logging:
                logger.debug("node=%s, %s", type(node), repr(node))

            if isinstance(node, Text):
                paragraphs_local = self._parse_text_node(node, parse_state)
                paragraphs.extend(paragraphs_local)
            elif isinstance(node, Wikilink):
                self._parse_wikilink_node(node, parse_state)
            elif isinstance(node, ExternalLink):
                self._parse_external_link_node(node, parse_state)
            elif isinstance(node, Tag):
                self._parse_tag_node(node, parse_state)
            elif isinstance(node, Heading):
                self._parse_heading_node(node, parse_state)

        if parse_state["current_text"] and not parse_state["current_text"].isspace():
            paragraphs.append({
                "plaintext": parse_state["current_text"].rstrip(),
                "wikilinks": parse_state["current_wikilinks"],
                "section_idx": parse_state["section_idx"],
                "section_name": parse_state["section_name"]})

        has_disambigution_template = self._has_disambiguation_template(wikitext)
        return {
            "paragraphs": paragraphs,
            "categories": self._default_filter_categories(wikicode),
            "has_disambiguation_template": has_disambigution_template,
        }

    def _parse_heading_node(self, node: Heading, parse_state) -> None:
        """Parse heading node.

        If this is a level 2 node (== heading ==), update section information.
        """
        if node.level == 2:
            parse_state["section_name"] = node.title.strip_code().strip()
            parse_state["section_idx"] += 1

    def _parse_tag_node(self, node: Tag, parse_state) -> None:
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
            parse_state["current_text"] += text

        # optionally add a single token for disallowed tags
        else:
            if self.include_disallowed_tag_tokens:
                text = "<{}>".format(node.tag.strip_code().strip())
                parse_state["current_text"] += text

    def _parse_external_link_node(self, node: ExternalLink, parse_state):
        """Parse external link node.

        Include the title of external links in the text stream.
        """
        if not self.include_external_link_anchors:
            return
        if not node.title:
            return
        text = node.title.strip_code().strip()
        parse_state["current_text"] += text

    def _default_wikilink_parser(
            self,
            node: Wikilink
    ) -> Tuple[bool, bool, str, str]:
        """Produce (add_text, add_link, target, anchor) tuple from Wikilink node.

        The tuple entries mean the following,
          * add_text: add the anchor text to the text stream?
          * add_link: add the target page title and anchor text to the link list?
          * target: target page title
          * anchor: link anchor text
        """
        target = node.title.strip_code().strip()

        if len(target) == 0:
            return (False, False, "", "")

        if any([
            target.lower().startswith(prefix)
            for prefix in self.forbidden_wikilink_prefixes
        ]):
            return (False, False, "", "")

        # [[#Links and URLs]]  (link to section in current page)
        if target.startswith("#"):
            anchor = target[1:]
            return (True, False, target, anchor)

        # remove section specific component
        target = target[:target.index("#")] if "#" in target else target

        # cover node.text = None and node.text = ""
        anchor = node.text.strip_code().strip() if node.text else target

        # remove namespace from anchor
        anchor = anchor[anchor.rindex(":") + 1:] if ":" in anchor else anchor

        # format page titles to match SQL dump format
        target = target[0].upper() + target[1:].replace(" ", "_")

        add_text = True
        add_link = ":" not in target
        return (add_text, add_link, target, anchor)

    def _parse_wikilink_node(self, node: Wikilink, parse_state) -> None:
        """Parse wikilink nodes.

        basic cases:,
          [[target_page]]
            node.title = "target_page", node.text = None
          [[target_page|anchor_text]]
            node.title = "target_page", node.text = "anchor_text"

        funny cases:
          [[target_page|]]
            node.title = "target_page", node.text = ""

        docs on link structure: https://en.wikipedia.org/wiki/Help:Link
        """

        # if there was a custom wikilink parser passed in
        if self.custom_wikilink_parser is not None:
            wikilink_parser = self.custom_wikilink_parser
        else:
            wikilink_parser = self._default_wikilink_parser

        add_text, add_link, target, anchor = wikilink_parser(node)

        if add_text:
            start = len(parse_state["current_text"])
            parse_state["current_text"] += anchor
            end = len(parse_state["current_text"])
        if add_link:
            parse_state["current_wikilinks"].append((target, anchor, start, end))

    def _parse_text_node(self, node: Text, parse_state) -> List[dict]:
        """Parse text node.

        Create a list of paragraph objects from a text node.
        """
        paragraphs_local = []
        for (ii, text) in enumerate(node.split("\n")):
            if ii == 0:
                parse_state["current_text"] += text
            else:
                if parse_state["current_text"] and not parse_state["current_text"].isspace():
                    paragraphs_local.append({
                        "text": parse_state["current_text"],
                        "wikilinks": parse_state["current_wikilinks"],
                        "section_idx": parse_state["section_idx"],
                        "section_name": parse_state["section_name"]})

                parse_state["current_text"] = text
                parse_state["current_wikilinks"] = []

        return paragraphs_local

    def _default_filter_categories(self, wikicode: Wikicode) -> List[str]:
        """Return a list of categories from wikicode."""
        wikilinks = wikicode.filter_wikilinks()
        ii = len("Category:")
        category_links = [
            el for el in wikilinks
            if el.title.lower().startswith("category:")]
        category_titles = [
            el.title.rstrip()[ii:]
            for el in category_links
            if len(el.title.rstrip()[ii:]) > 0]
        category_titles = [
            title[0].upper() + title[1:].replace(" ", "_")
            for title in category_titles
        ]

        return category_titles

    def _has_disambiguation_template(self, wikitext: str) -> bool:
        """Check for templates indicating disambiguation page status.

        Disambiguation templates come in several varieties
        e.g. {{disambiguation}}, {{disambiguation|geo}}, ...
        Also, links inside a page can be marked with a
        {{disambiguation needed|date=...}}
        without marking the page as a disambigution page so we do a quick
        and dirty check for the opening part of a disambiguation template.

        Another way to check for disambiguation page status (and other non natural
        text pages) is to use wikidata to see if the page is associated with a
        wikidata item that is an instance of https://www.wikidata.org/wiki/Q17442446
        or any of its subclasses.
        """
        template_bool = (
            "{{disambiguation|" in wikitext or
            "{{disambiguation}}" in wikitext)
        return template_bool
