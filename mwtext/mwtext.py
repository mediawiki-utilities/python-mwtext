import mwcli

router = mwcli.Router(
    "mwtext",
    "This script provides access to a set of utilities for text processing",
    {'preprocess_text': "Converts an XML dump to preprocessed plaintext. " +
                        "One line per chunk."}
)

main = router.main
