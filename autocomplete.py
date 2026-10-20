
# -------------------------------------------------------------------------
# TEMPORARY MODULE
#
# This is a provisional autocomplete so the interface can be developed and
# tested before the Trie is ready. It scans the vocabulary directly, which
# is O(V) per query instead of the O(p) that a Trie gives.
#
# When Lepe delivers the Trie, this file should be replaced by a version
# that calls it. The GUI only uses the function suggest(prefix, limit),
# so nothing else in the interface has to change.
# -------------------------------------------------------------------------

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VOCABULARY_FILE = BASE_DIR / "data" / "vocabulary.json"

_vocabulary = None


def load_vocabulary():
    global _vocabulary

    if _vocabulary is None:
        with open(VOCABULARY_FILE, "r", encoding="utf-8") as file:
            _vocabulary = json.load(file)

    return _vocabulary


def suggest(prefix, limit=5):
    prefix = prefix.lower().strip()

    if len(prefix) < 2:
        return []

    vocabulary = load_vocabulary()

    matches = []

    for word in vocabulary:
        if word.startswith(prefix) and word != prefix:
            matches.append(word)

        if len(matches) >= limit:
            break

    return matches


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
    print("\nSHERLOCK HOLMES - AUTOCOMPLETE (provisional)")
    print("=" * 50)

    vocabulary = load_vocabulary()
    print(f"Vocabulary size: {len(vocabulary)}")

    for prefix in ["bel", "ven", "goo", "tun", "car", "sher"]:
        print(f"  '{prefix}' -> {suggest(prefix)}")


if __name__ == "__main__":
    main()
