import mwcli

router = mwcli.Router(
    "mwtext",
    "This script provides access to a set of utilities for text processing",
    {'preprocess_text': "Converts an XML dump to preprocessed plaintext. " +
                        "One line per chunk.",
     'learn_vectors':   "Learn a set of word vectors from preprocessed " +
                        "plaintext"}
)

main = router.main
