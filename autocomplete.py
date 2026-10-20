
# -------------------------------------------------------------------------
# AUTOCOMPLETE
#
# Builds the Trie (trie.py) from the vocabulary of the collection and gives
# the GUI the function suggest(prefix, limit). Each word is inserted with
# its document frequency (number of chunks that contain it, taken from the
# inverted index), so frequent words of the case are suggested first.
#
# The Trie is built only once, the first time it is needed. After that,
# each query costs O(p + k) instead of the O(V) of scanning the whole
# vocabulary.
# -------------------------------------------------------------------------

import json
from pathlib import Path

from trie import Trie

BASE_DIR = Path(__file__).resolve().parent
VOCABULARY_FILE = BASE_DIR / "data" / "vocabulary.json"
INVERTED_INDEX_FILE = BASE_DIR / "data" / "inverted_index.json"

MIN_PREFIX_LENGTH = 2

_vocabulary = None
_trie = None


def load_vocabulary():
    global _vocabulary

    if _vocabulary is None:
        with open(VOCABULARY_FILE, "r", encoding="utf-8") as file:
            _vocabulary = json.load(file)

    return _vocabulary


def load_document_frequency():
    if not INVERTED_INDEX_FILE.exists():
        return {}

    with open(INVERTED_INDEX_FILE, "r", encoding="utf-8") as file:
        inverted_index = json.load(file)

    document_frequency = {}

    for word in inverted_index:
        document_frequency[word] = len(inverted_index[word])

    return document_frequency


def build_trie(vocabulary, document_frequency=None):
    if document_frequency is None:
        document_frequency = {}

    trie = Trie()

    for word in vocabulary:
        trie.insert(word, document_frequency.get(word, 1))

    return trie


def get_trie():
    global _trie

    if _trie is None:
        _trie = build_trie(load_vocabulary(), load_document_frequency())

    return _trie


def suggest(prefix, limit=5):
    prefix = prefix.lower().strip()

    if len(prefix) < MIN_PREFIX_LENGTH:
        return []

    return get_trie().suggest(prefix, limit)


def last_word(text):
    text = text.strip()

    if len(text) == 0:
        return ""

    if text.endswith(" "):
        return ""

    return text.split()[-1]


def replace_last_word(text, new_word):
    parts = text.strip().split()

    if len(parts) == 0:
        return new_word + " "

    parts[-1] = new_word

    return " ".join(parts) + " "


def main():
    print("\nSHERLOCK HOLMES - AUTOCOMPLETE (Trie)")
    print("=" * 50)

    trie = get_trie()
    print(f"Words in the Trie: {len(trie)}")
    print(f"Nodes in the Trie: {trie.node_count()}")

    for prefix in ["bel", "ven", "goo", "tun", "car", "sher"]:
        print(f"  '{prefix}' -> {suggest(prefix)}")


if __name__ == "__main__":
    main()
