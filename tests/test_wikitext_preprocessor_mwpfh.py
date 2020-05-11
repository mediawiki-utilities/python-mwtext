"""
Inspiration for test cases drawn from,

 * https://en.wikipedia.org/wiki/Help:Wikitext#Links_and_URLs
"""
from mwtext import WikitextPreprocessorMwpfh

WIKILINK_TEST_FIXTURES = {
    "basic": {
        "wikitext": "[[target_title]]",
        "text": "target_title",
        "links": [("target_title", "target_title", 0, 12)],
    },
    "rename": {
        "wikitext": "[[target_title|anchor_text]]",
        "text": "anchor_text",
        "links": [("target_title", "anchor_text", 0, 11)],
    },
    "kingdom": {
        "wikitext": "[[kingdom (biology)]]",
        "text": "kingdom (biology)",
        "links": [("kingdom (biology)", "kingdom (biology)", 0, 17)],
    },
    "seattle": {
        "wikitext": "[[Seattle, Washington]]",
        "text": "Seattle, Washington",
        "links": [("Seattle, Washington", "Seattle, Washington", 0, 19)],
    },
    "village": {
        "wikitext": "[[Wikipedia:Village pump]]",
        "text": "Village pump",
        "links": [('Wikipedia:Village pump', 'Village pump', 0, 12)],
    },
    "style": {
        "wikitext": "[[Wikipedia:Manual of Style#Links]]",
        "text": "Manual of Style",
        "links": [('Wikipedia:Manual of Style', 'Manual of Style', 0, 15)],
    },
    "kingdom|": {
        "wikitext": "[[kingdom (biology)|]]",
        "text": "kingdom (biology)",
        "links": [("kingdom (biology)", "kingdom (biology)", 0, 17)],
    },
    "seattle|": {
        "wikitext": "[[Seattle, Washington|]]",
        "text": "Seattle, Washington",
        "links": [("Seattle, Washington", "Seattle, Washington", 0, 19)],
    },
    "village|": {
        "wikitext": "[[Wikipedia:Village pump|]]",
        "text": "Village pump",
        "links": [('Wikipedia:Village pump', 'Village pump', 0, 12)],
    },
    "style|": {
        "wikitext": "[[Wikipedia:Manual of Style#Links|]]",
        "text": "Manual of Style",
        "links": [('Wikipedia:Manual of Style', 'Manual of Style', 0, 15)],
    },
    "#self": {
        "wikitext": "[[#self]]",
        "text": "self",
        "links": [('#self', 'self', 0, 4)],
    },
}



def test_wikilinks_only():
    for test_name, test_data in WIKILINK_TEST_FIXTURES.items():
        wtpp = WikitextPreprocessorMwpfh()
        parsed = wtpp.process(test_data["wikitext"])
        expected = [
            {
                "section_idx": 0,
                "section_name": "Introduction",
                "text": test_data["text"],
                "wikilinks": test_data["links"]
            },
        ]
        assert parsed == expected
