"""
Inspiration for test cases drawn from,

 * https://en.wikipedia.org/wiki/Help:Wikitext#Links_and_URLs
"""
from mwtext import WikitextPreprocessorMwpfh

WIKILINK_TEST_FIXTURES = {
    "basic": "[[target_title]]",
    "rename": "[[target_title|anchor_text]]",
    "kingdom": "[[kingdom (biology)]]",
    "seattle": "[[Seattle, Washington]]",
    "village": "[[Wikipedia:Village pump]]",
    "style": "[[Wikipedia:Manual of Style#Links]]",
    "kingdom|": "[[kingdom (biology)|]]",
    "seattle|": "[[Seattle, Washington|]]",
    "village|": "[[Wikipedia:Village pump|]]",
    "style|": "[[Wikipedia:Manual of Style#Links|]]",
    "#self": "[[#self]]",
}

WIKILINK_EXPECTED_TEXT = {
    "basic": "target_title",
    "rename": "anchor_text",
    "kingdom": "kingdom (biology)",
    "seattle": "Seattle, Washington",
    "village": "Village pump",
    "style": "Manual of Style",
    "kingdom|": "kingdom (biology)",
    "seattle|": "Seattle, Washington",
    "village|": "Village pump",
    "style|": "Manual of Style",
    "#self": "self",
}

WIKILINK_EXPECTED_LINKS = {
    "basic": [("target_title", "target_title", 0, 12)],
    "rename": [("target_title", "anchor_text", 0, 11)],
    "kingdom": [("kingdom (biology)", "kingdom (biology)", 0, 17)],
    "seattle": [("Seattle, Washington", "Seattle, Washington", 0, 19)],
    "village": [('Wikipedia:Village pump', 'Village pump', 0, 12)],
    "style": [('Wikipedia:Manual of Style', 'Manual of Style', 0, 15)],
    "kingdom|": [("kingdom (biology)", "kingdom (biology)", 0, 17)],
    "seattle|": [("Seattle, Washington", "Seattle, Washington", 0, 19)],
    "village|": [('Wikipedia:Village pump', 'Village pump', 0, 12)],
    "style|": [('Wikipedia:Manual of Style', 'Manual of Style', 0, 15)],
    "#self": [('#self', 'self', 0, 4)],
}


def test_wikilinks_only():
    for fixname in WIKILINK_TEST_FIXTURES:
        wtpp = WikitextPreprocessorMwpfh()
        text = WIKILINK_TEST_FIXTURES[fixname]
        parsed = wtpp.process(text)
        expected = [
            {"section_idx": 0,
             "section_name": "Introduction",
             "text": WIKILINK_EXPECTED_TEXT[fixname],
             "wikilinks": WIKILINK_EXPECTED_LINKS[fixname]}
        ]
        assert parsed == expected
