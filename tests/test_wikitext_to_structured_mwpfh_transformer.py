"""
Inspiration for test cases drawn from,

 * https://en.wikipedia.org/wiki/Help:Wikitext#Links_and_URLs
"""
from mwtext import WikitextToStructuredMwpfhTransformer
from .mwpfh_wikilink_fixtures import WIKILINK_TEST_FIXTURES


def test_wikilinks_only():
    for test_name, test_data in WIKILINK_TEST_FIXTURES.items():
        wtpp = WikitextToStructuredMwpfhTransformer()
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
