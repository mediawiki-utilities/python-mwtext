from mwtext import WikitextPreprocessorMwpfh


def test_wikilink_1():
    wtpp = WikitextPreprocessorMwpfh()
    text = """[[target]]"""
    parsed = wtpp.process(text)
    expected = [
        {'section_idx': 0,
         'section_name': 'Introduction',
         'text': 'target',
         'wikilinks': [('target', 'target', 0, 6)]}
    ]
    assert parsed == expected


def test_wikilink_2():
    wtpp = WikitextPreprocessorMwpfh()
    text = """[[target|anchor]]"""
    parsed = wtpp.process(text)
    expected = [
        {'section_idx': 0,
         'section_name': 'Introduction',
         'text': 'anchor',
         'wikilinks': [('target', 'anchor', 0, 6)]}
    ]
    assert parsed == expected
