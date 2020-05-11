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
        "links": [],
    },
    "style": {
        "wikitext": "[[Wikipedia:Manual of Style#Links]]",
        "text": "Manual of Style",
        "links": [],
    },
    "style2": {
        "wikitext": "[[Wikipedia:Manual of Style#Italics|Italics]]",
        "text": "Italics",
        "links": [],
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
        "links": [],
    },
    "style|": {
        "wikitext": "[[Wikipedia:Manual of Style#Links|]]",
        "text": "Manual of Style",
        "links": [],
    },
    "#self": {
        "wikitext": "[[#Links and URLs]]",
        "text": "Links and URLs",
        "links": [],
    },
    "#self|s": {
        "wikitext": "[[#Links and URLs|Links and URLs]]",
        "text": "Links and URLs",
        "links": [],
    },
    "micro-": {
        "wikitext": "[[micro-]]second",
        "text": "micro-second",
        "links": [('micro-', 'micro-', 0, 6)],
    },
    "micro-nowiki": {
        "wikitext": "[[micro-]]<nowiki />second",
        "text": "micro-second",
        "links": [('micro-', 'micro-', 0, 6)],
    },
    "category": {
        "wikitext": "a [[Category:Vowel letters]]",
        "text": "a ",
        "links": [],
    },
    ":category": {
        "wikitext": "a [[:Category:Vowel letters]]",
        "text": "a Vowel letters",
        "links": [],
    },
    ":category|": {
        "wikitext": "a [[:Category:Vowel letters|]]",
        "text": "a Vowel letters",
        "links": [],
    },
    "nested_file": {
        "wikitext": "a [[File:Albedo-e hg.svg|thumb|upright=1.3|The percentage of [[diffuse reflection|diffusely reflected]] [[sunlight]] relative to various surface conditions]]",
        "text": "a ",
        "links": [],
    },
}
