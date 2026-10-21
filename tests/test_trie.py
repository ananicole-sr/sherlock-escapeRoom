import json
import time
from pathlib import Path

from search.trie import Trie
from search.autocomplete import load_vocabulary, load_document_frequency, build_trie

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_FILE = BASE_DIR / "reports" / "results" / "trie_results.json"

TEST_PREFIXES = ["bel", "ven", "goo", "tun", "car", "sher", "ro", "sp", "wh", "zzz"]
REPETITIONS = 200


def test_basic_operations():
    trie = Trie()

    for word in ["loca", "locacion", "lapiz", "poca", "pozo", "puerco", "puerta", "taco"]:
        trie.insert(word)

    assert trie.search("loca")
    assert trie.search("poca")
    assert not trie.search("lap")
    assert not trie.search("poco")
    assert not trie.search("puerc")

    assert trie.starts_with("lap")
    assert trie.starts_with("loca")
    assert trie.starts_with("puerc")
    assert not trie.starts_with("poco")

    assert len(trie) == 8

    trie.insert("loca")
    assert len(trie) == 8

    print("Basic operations: OK")


def test_suggestions():
    trie = Trie()
    trie.insert("bell", 10)
    trie.insert("belong", 3)
    trie.insert("belief", 3)
    trie.insert("bed", 7)
    trie.insert("be", 20)

    assert trie.suggest("bel") == ["bell", "belief", "belong"]
    assert trie.suggest("be", limit=2) == ["bell", "bed"]
    assert trie.suggest("x") == []
    assert trie.suggest("bell") == []

    print("Suggestions: OK")


def test_against_vocabulary(trie, vocabulary):
    for prefix in TEST_PREFIXES:
        expected = sorted(word for word in vocabulary
                          if word.startswith(prefix) and word != prefix)
        found = sorted(trie.suggest(prefix, limit=len(vocabulary)))

        assert found == expected, prefix

    for word in vocabulary:
        assert trie.search(word), word

    print("Trie agrees with a linear scan of the vocabulary: OK")


def linear_suggest(vocabulary, document_frequency, prefix, limit):
    candidates = []

    for word in vocabulary:
        if word.startswith(prefix) and word != prefix:
            candidates.append((word, document_frequency.get(word, 1)))

    candidates.sort(key=lambda item: (-item[1], item[0]))

    return [word for word, weight in candidates[:limit]]


def average_time_ms(function, repetitions=REPETITIONS):
    start = time.perf_counter()

    for _ in range(repetitions):
        function()

    return (time.perf_counter() - start) * 1000 / repetitions


def measure(trie, vocabulary, document_frequency):
    print("\nTRIE VS LINEAR SCAN")
    print("=" * 75)
    print(f"{'prefix':<8} {'matches':>8} {'trie (ms)':>11} {'linear (ms)':>12}  suggestions")
    print("-" * 75)

    records = []

    for prefix in TEST_PREFIXES:
        matches = len(trie.words_with_prefix(prefix))

        trie_time = average_time_ms(lambda: trie.suggest(prefix, 5))
        linear_time = average_time_ms(
            lambda: linear_suggest(vocabulary, document_frequency, prefix, 5)
        )

        suggestions = trie.suggest(prefix, 5)

        print(f"{prefix:<8} {matches:>8} {trie_time:>11.4f} {linear_time:>12.4f}  {suggestions}")

        records.append({
            "prefix": prefix,
            "matches": matches,
            "trie_time_ms": trie_time,
            "linear_time_ms": linear_time,
            "suggestions": suggestions
        })

    return records


def measure_construction(vocabulary, document_frequency):
    print("\nCONSTRUCTION")
    print("=" * 75)

    total_characters = sum(len(word) for word in vocabulary)

    start = time.perf_counter()
    trie = build_trie(vocabulary, document_frequency)
    build_time = (time.perf_counter() - start) * 1000

    print(f"Words:              {len(trie)}")
    print(f"Total characters:   {total_characters}")
    print(f"Nodes:              {trie.node_count()}")
    print(f"Nodes saved by shared prefixes: "
          f"{100 * (1 - trie.node_count() / (total_characters + 1)):.1f}%")
    print(f"Build time:         {build_time:.2f} ms")

    return {
        "words": len(trie),
        "total_characters": total_characters,
        "nodes": trie.node_count(),
        "build_time_ms": build_time
    }


def main():
    test_basic_operations()
    test_suggestions()

    vocabulary = load_vocabulary()
    document_frequency = load_document_frequency()

    construction = measure_construction(vocabulary, document_frequency)

    trie = build_trie(vocabulary, document_frequency)
    test_against_vocabulary(trie, vocabulary)

    records = measure(trie, vocabulary, document_frequency)

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump({"construction": construction, "queries": records},
                  file, ensure_ascii=False, indent=2)

    print(f"\nResults saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
