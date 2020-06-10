import mwcli

router = mwcli.Router(
    "mwtext",
    "This script provides access to a set of utilities for text processing",
    {'transform_content': "Transforms an XML dump using a transformer",
     'words2plaintext': "Converts a 'words' type transformation into " +
                        "plaintext -- optionally with labels",
     'learn_vectors':   "Learn a set of word vectors from preprocessed " +
                        "plaintext",
     'word2vec2gensim': "Converts word2vec format to gensim KeyedVector " +
                        "binaries"}
)

main = router.main
