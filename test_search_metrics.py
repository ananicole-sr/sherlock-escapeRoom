import json
import random
from pathlib import Path

import watson
from approximate_search import load_collection, search_approximate
from exact_search import exact_search, INVERTED_INDEX, CHUNK_MAP
from kmp import kmp_search
from query_processing import extract_query_terms
from z_function import z_search

BASE_DIR = Path(__file__).resolve().parent

STORIES = [None, "The Speckled Band", "The Blue Carbuncle", "The Red-Headed League"]

QUERIES = [
    "What happened to the bell rope?",
    "Where did Peterson's wife find the blue stone?",
    "What was in Dr. Roylott’s room?",
    "Why was Jabez Wilson paid to copy the Encyclopaedia?",
    "Why did Holmes beat the pavement?",
    "Who was James Ryder?",
    "What colour was the Countess of Morcar's carriage?",
    "What was the bel roap?",
    "the of and",
    ""
]

failures = []


def check(condition, message):
    if not condition:
        failures.append(message)


def naive_positions(text, pattern):
    return [i for i in range(len(text) - len(pattern) + 1) if text[i:i + len(pattern)] == pattern]


def test_preprocessing():
    check(extract_query_terms("Where did Peterson's wife find the blue stone?")
          == ["peterson", "wife", "find", "blue", "stone"], "possessive 's")
    check(extract_query_terms("What was in Dr. Roylott’s room?") == ["dr", "roylott", "room"],
          "curly possessive ’s")
    check(extract_query_terms("Holmes' client") == ["holmes", "client"], "plural possessive '")
    check(extract_query_terms("don't bell bell rope") == ["don", "bell", "rope"],
          "single letters dropped and terms kept once")
    check(extract_query_terms("the of and") == [], "only stopwords")

    for query in QUERIES:
        terms = extract_query_terms(query)
        check("s" not in terms, f"'s' term in {query!r}")
        check(all(len(term) > 1 for term in terms), f"one-letter term in {query!r}")

    print("Preprocessing: checked")


def test_same_terms(chunks, vocabulary, document_frequency):
    for query in QUERIES:
        exact = exact_search(query, "kmp", 5)
        approx = search_approximate(query, chunks, vocabulary, document_frequency, top_k=5)
        check(exact["query_terms"] == approx["query_terms"] == extract_query_terms(query),
              f"engines extract different terms for {query!r}")

    approx = search_approximate("What was the bel roap?", chunks, vocabulary, document_frequency)
    exact = exact_search("What was the bel roap?", "kmp")
    check(len(approx["corrections"]) > 0, "approximate engine should correct 'bel roap'")
    check(exact["query_terms"] == ["bel", "roap"] and "corrections" not in exact,
          "exact engine must not correct spelling")

    print("Shared terms, correction only in the approximate engine: checked")


def test_kmp_equals_z():
    random.seed(7)
    vocabulary = json.load(open(BASE_DIR / "data" / "vocabulary.json", encoding="utf-8"))
    comparisons = 0

    for chunk in CHUNK_MAP.values():
        text = " " + chunk["normalized_text"] + " "
        for word in random.sample(vocabulary, 20) + ["holmes", "bell", "the"]:
            pattern = " " + word + " "
            expected = naive_positions(text, pattern)
            check(kmp_search(text, pattern) == expected, f"KMP positions {word!r} {chunk['id']}")
            check(z_search(text, pattern) == expected, f"Z positions {word!r} {chunk['id']}")
            comparisons += 1

    full_queries = QUERIES + [" ".join(random.sample(vocabulary, 3)) for _ in range(40)]

    for query in full_queries:
        for story in STORIES:
            a = exact_search(query, "kmp", top_k=1000, story=story)
            b = exact_search(query, "z", top_k=1000, story=story)
            same = [(r["chunk_id"], r["score"], r["matched_terms"]) for r in a["results"]] == \
                   [(r["chunk_id"], r["score"], r["matched_terms"]) for r in b["results"]]
            check(same, f"KMP and Z differ for {query!r} / {story}")
            for name in ["candidates_considered", "chunks_examined", "chunks_matched", "results_returned"]:
                check(a[name] == b[name], f"{name} differs between KMP and Z for {query!r}")
            comparisons += 1

    print(f"KMP == Z == naive search: {comparisons} comparisons")


def test_exact_metrics():
    for query in QUERIES:
        terms = extract_query_terms(query)
        candidates = set()
        for term in terms:
            candidates.update(INVERTED_INDEX.get(term, []))

        for story in STORIES:
            examined = [c for c in candidates if story is None or CHUNK_MAP[c]["story"] == story]

            # Independent count of chunks with at least one exact match.
            matched = 0
            for chunk_id in examined:
                text = " " + CHUNK_MAP[chunk_id]["normalized_text"] + " "
                if any(naive_positions(text, " " + t + " ") for t in terms):
                    matched += 1

            for top_k in [1, 5, 1000]:
                r = exact_search(query, "kmp", top_k=top_k, story=story)
                label = f"exact {query!r} story={story} top_k={top_k}"
                check(r["candidates_considered"] == len(candidates), label + " candidates")
                check(r["chunks_examined"] == len(examined), label + " examined")
                check(r["chunks_matched"] == matched, label + " matched")
                check(r["results_returned"] == min(matched, top_k) == len(r["results"]), label + " returned")
                check(r["chunks_examined"] <= r["candidates_considered"], label + " examined <= candidates")
                check(all(story is None or x["story"] == story for x in r["results"]), label + " story")

    print("Exact metrics: checked against an independent count")


def test_approximate_metrics(chunks, vocabulary, document_frequency):
    for query in QUERIES:
        for story in STORIES:
            in_story = [c for c in chunks if story is None or c["story"] == story]

            for top_k in [1, 5, 1000]:
                r = search_approximate(query, chunks, vocabulary, document_frequency,
                                       top_k=top_k, story=story)
                label = f"approx {query!r} story={story} top_k={top_k}"
                check(r["candidates_considered"] == len(chunks), label + " candidates")
                check(r["chunks_examined"] == len(in_story), label + " examined")
                check(r["results_returned"] == min(r["chunks_matched"], top_k) == len(r["results"]),
                      label + " returned")
                check(r["chunks_matched"] <= r["chunks_examined"], label + " matched <= examined")
                check(r["chunks_with_term_match"] <= r["chunks_examined"], label + " term match")
                check(all(x["score"] > 0 for x in r["results"]), label + " zero-score result")
                check(all(story is None or x["story"] == story for x in r["results"]), label + " story")

    print("Approximate metrics: checked")


def test_watson_context(chunks, vocabulary, document_frequency):
    question = "Where did Peterson's wife find the blue stone?"
    story = "The Blue Carbuncle"

    responses = {
        "kmp": exact_search(question, "kmp", 5, story),
        "z": exact_search(question, "z", 5, story),
        "approximate": search_approximate(question, chunks, vocabulary, document_frequency,
                                          top_k=5, story=story)
    }

    for name, response in responses.items():
        context = watson.select_context(question, response["results"])
        check(len(context) > 0, f"Watson got no context from {name}")
        check(sum(item["tokens"] for item in context) <= watson.input_budget(),
              f"context of {name} exceeds the budget")
        print(f"  {name:12} -> {[item['chunk_id'] for item in context]}")

    print("Watson context selection with the three engines: checked")


def main():
    chunks, vocabulary, document_frequency = load_collection()

    test_preprocessing()
    test_same_terms(chunks, vocabulary, document_frequency)
    test_kmp_equals_z()
    test_exact_metrics()
    test_approximate_metrics(chunks, vocabulary, document_frequency)
    test_watson_context(chunks, vocabulary, document_frequency)

    if failures:
        print(f"\n{len(failures)} FAILURES")
        for failure in failures[:30]:
            print("  - " + failure)
        raise SystemExit(1)

    print("\nAll search and metric checks passed.")


if __name__ == "__main__":
    main()
