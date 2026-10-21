
# -------------------------------------------------------------------------
# Stage 6 - retrieval time versus collection size.
#
# Real sub-collections of one, two and three stories are built in memory
# from data/processed_chunks.json: each one gets its own inverted index,
# vocabulary, document frequencies and approximate-search structures. The
# production files are only read, never written.
#
# Three growth orders, so each question's source story is present from the
# one-story collection and every story is the base once:
#   A  Speckled Band  -> + Blue Carbuncle    -> + Red-Headed League  (SB01-SB07)
#   B  Blue Carbuncle -> + Red-Headed League -> + Speckled Band      (BC01-BC07)
#   C  Red-Headed     -> + Speckled Band     -> + Blue Carbuncle     (RH01-RH06)
#
# No story filter is used. Qwen is not called.
#
# The exact engine (exact_search.py) reads the index and the chunks from
# module-level variables; they are swapped for the sub-collection's while
# it is measured and restored afterwards. The algorithm is unchanged.
# -------------------------------------------------------------------------

import copy
import csv
import gc
import json
import platform
import time
from pathlib import Path

from search import exact_search
from search.approximate_search import STOPWORDS, search_approximate
from search.inverted_index import build_inverted_index
from search.jaccard import char_ngrams

BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_FILE = BASE_DIR / "data" / "processed_chunks.json"
QUESTIONS_FILE = BASE_DIR / "reports" / "results" / "evaluation_questions.json"
RESULTS_FILE = BASE_DIR / "reports" / "results" / "scaling_results.json"
SUMMARY_FILE = BASE_DIR / "reports" / "results" / "scaling_summary.csv"

SB = "The Speckled Band"
BC = "The Blue Carbuncle"
RH = "The Red-Headed League"

ORDERS = {
    "A": [SB, BC, RH],
    "B": [BC, RH, SB],
    "C": [RH, SB, BC]
}

ENGINES = ["kmp", "z", "approximate"]
TOP_K = 5
WARMUP_RUNS = 1
TIMED_RUNS = 5
NGRAM_SIZE = 3
APPROXIMATE_SETTINGS = {"method": "combined", "ngram_size": NGRAM_SIZE, "max_distance": 2}

DEFINITIONS = {
    "candidates_considered": "Exact: chunks proposed by the inverted index (at least one query term). "
                             "Approximate: every chunk of the collection (no index is used).",
    "chunks_examined": "Chunks actually scanned (exact: with KMP or Z) or scored (approximate). "
                       "No story filter is used here, so it equals the candidates.",
    "chunks_matched": "Exact: chunks with at least one exact match. Approximate: chunks with a "
                      "score > 0 (character n-grams give almost every chunk a small score). Before top_k.",
    "results_returned": "Results returned after top_k (= min(chunks_matched, top_k)).",
    "engine_reported_ms": "retrieval_time_ms reported by the engine itself, from the start of the "
                          "query processing to the ranked list.",
    "wall_ms": "Time measured around the call by this script.",
    "collection_characters": "Characters of original_text in the collection.",
    "normalized_characters": "Characters of normalized_text (what KMP and Z scan)."
}


def prepare_collection(all_chunks, stories):
    """
        Builds every structure the engines need for this sub-collection and
        times each step separately from the searches.
    """
    timings = {}

    start = time.perf_counter()
    chunks = [copy.deepcopy(chunk) for chunk in all_chunks if chunk["story"] in stories]
    timings["select_chunks_ms"] = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    index = build_inverted_index(chunks)
    index = {word: sorted(index[word]) for word in sorted(index)}
    vocabulary = list(index.keys())
    document_frequency = {word: len(ids) for word, ids in index.items()}
    timings["inverted_index_and_vocabulary_ms"] = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    content_vocabulary = [word for word in vocabulary if word not in STOPWORDS]
    for chunk in chunks:
        chunk["content_tokens"] = {token for token in chunk["tokens"] if token not in STOPWORDS}
    timings["approximate_tokens_ms"] = (time.perf_counter() - start) * 1000

    # Character n-grams are cached on each chunk by the approximate engine;
    # they are built here so no search pays for them.
    start = time.perf_counter()
    for chunk in chunks:
        chunk["char_ngrams"] = char_ngrams(chunk["normalized_text"], NGRAM_SIZE)
    timings["approximate_char_ngrams_ms"] = (time.perf_counter() - start) * 1000

    timings = {name: round(value, 3) for name, value in timings.items()}
    timings["total_ms"] = round(sum(timings.values()), 3)

    return {
        "chunks": chunks,
        "index": index,
        "chunk_map": {chunk["id"]: chunk for chunk in chunks},
        "vocabulary": content_vocabulary,
        "document_frequency": document_frequency,
        "size": {
            "stories": len(stories),
            "story_names": stories,
            "chunks": len(chunks),
            "collection_characters": sum(len(c["original_text"]) for c in chunks),
            "normalized_characters": sum(len(c["normalized_text"]) for c in chunks),
            "tokens": sum(len(c["tokens"]) for c in chunks),
            "index_terms": len(index),
            "content_vocabulary": len(content_vocabulary)
        },
        "preparation": timings
    }


def search(engine, question, collection):
    if engine == "approximate":
        return search_approximate(
            question, collection["chunks"], collection["vocabulary"],
            collection["document_frequency"], top_k=TOP_K, **APPROXIMATE_SETTINGS
        )

    return exact_search.exact_search(question, algorithm=engine, top_k=TOP_K)


def measure(engine, question, collection):
    for _ in range(WARMUP_RUNS):
        search(engine, question, collection)

    engine_ms = []
    wall_ms = []
    rankings = []
    response = None

    for _ in range(TIMED_RUNS):
        start = time.perf_counter()
        response = search(engine, question, collection)
        wall_ms.append(round((time.perf_counter() - start) * 1000, 4))
        engine_ms.append(response["retrieval_time_ms"])
        rankings.append([(r["chunk_id"], r["score"]) for r in response["results"]])

    return response, {
        "engine_reported_ms": engine_ms,
        "engine_reported_mean_ms": round(sum(engine_ms) / len(engine_ms), 4),
        "engine_reported_min_ms": min(engine_ms),
        "engine_reported_max_ms": max(engine_ms),
        "wall_ms": wall_ms,
        "wall_mean_ms": round(sum(wall_ms) / len(wall_ms), 4),
        "same_results_in_all_runs": all(r == rankings[0] for r in rankings)
    }


def main():
    if RESULTS_FILE.exists():
        raise SystemExit(f"{RESULTS_FILE} already exists; move it before running again.")

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        all_chunks = json.load(file)

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)["questions"]

    production_index = exact_search.INVERTED_INDEX
    production_map = exact_search.CHUNK_MAP

    collections = []
    runs = []

    try:
        for order, stories in ORDERS.items():
            base = stories[0]
            order_questions = [q for q in questions if q["story"] == base]

            for size in range(1, len(stories) + 1):
                included = stories[:size]
                collection = prepare_collection(all_chunks, included)

                collections.append({
                    "order": order,
                    "base_story": base,
                    "size": collection["size"],
                    "preparation_ms": collection["preparation"]
                })

                exact_search.INVERTED_INDEX = collection["index"]
                exact_search.CHUNK_MAP = collection["chunk_map"]

                for item in order_questions:
                    evidence_ids = {chunk_id for chunk_id, quote in item["evidence"]}

                    for engine in ENGINES:
                        response, timing = measure(engine, item["question"], collection)
                        ranked = [r["chunk_id"] for r in response["results"]]
                        ranks = [rank for rank, chunk_id in enumerate(ranked, start=1)
                                 if chunk_id in evidence_ids]

                        runs.append({
                            "order": order,
                            "base_story": base,
                            "stories": collection["size"]["stories"],
                            "chunks": collection["size"]["chunks"],
                            "collection_characters": collection["size"]["collection_characters"],
                            "normalized_characters": collection["size"]["normalized_characters"],
                            "engine": engine,
                            "question_id": item["id"],
                            "question_type": item["type"],
                            "question": item["question"],
                            "query_terms": response.get("query_terms"),
                            "corrected_terms": response.get("corrected_terms"),
                            "timing": timing,
                            "candidates_considered": response["candidates_considered"],
                            "chunks_examined": response["chunks_examined"],
                            "chunks_matched": response["chunks_matched"],
                            "results_returned": response["results_returned"],
                            "returned_chunk_ids": ranked,
                            "returned_stories": [r["story"] for r in response["results"]],
                            "answerable": item["type"] != "unanswerable",
                            "evidence_rank_in_top_k": min(ranks) if ranks else None
                        })

                print(f"{order} {collection['size']['stories']} stories "
                      f"({collection['size']['chunks']} chunks): {len(order_questions)} questions "
                      f"x {len(ENGINES)} engines, preparation {collection['preparation']['total_ms']:.1f} ms",
                      flush=True)
                gc.collect()
    finally:
        exact_search.INVERTED_INDEX = production_index
        exact_search.CHUNK_MAP = production_map

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump({
            "description": "Retrieval time versus real collection size (stage 6). Qwen not used.",
            "configuration": {
                "orders": ORDERS,
                "questions": "the 20 questions of reports/results/evaluation_questions.json; each order uses "
                             "the questions of its base story",
                "engines": ENGINES,
                "top_k": TOP_K,
                "story_filter": None,
                "approximate_settings": APPROXIMATE_SETTINGS,
                "warmup_runs_per_question_and_engine": WARMUP_RUNS,
                "timed_runs_per_question_and_engine": TIMED_RUNS,
                "cache": "no caches in the exact engine; approximate character n-grams are "
                         "precomputed during preparation (outside the timed searches); "
                         "Levenshtein has no cache and runs inside the timed search",
                "structures": "each sub-collection has its own inverted index, vocabulary, "
                              "document frequencies, content tokens and character n-grams",
                "exact_engine_note": "exact_search.INVERTED_INDEX and CHUNK_MAP are swapped for the "
                                     "sub-collection during its measurements and restored afterwards",
                "python": platform.python_version(),
                "machine": platform.processor() or platform.machine()
            },
            "definitions": DEFINITIONS,
            "collections": collections,
            "runs": runs
        }, file, ensure_ascii=False, indent=2)

    columns = ["order", "base_story", "stories", "chunks", "collection_characters",
               "normalized_characters", "engine", "question_id", "question_type",
               "engine_reported_mean_ms", "engine_reported_min_ms", "engine_reported_max_ms",
               "wall_mean_ms", "candidates_considered", "chunks_examined", "chunks_matched",
               "results_returned", "evidence_rank_in_top_k"]

    with open(SUMMARY_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        for run in runs:
            writer.writerow([
                run["order"], run["base_story"], run["stories"], run["chunks"],
                run["collection_characters"], run["normalized_characters"], run["engine"],
                run["question_id"], run["question_type"],
                run["timing"]["engine_reported_mean_ms"], run["timing"]["engine_reported_min_ms"],
                run["timing"]["engine_reported_max_ms"], run["timing"]["wall_mean_ms"],
                run["candidates_considered"], run["chunks_examined"], run["chunks_matched"],
                run["results_returned"],
                "" if run["evidence_rank_in_top_k"] is None else run["evidence_rank_in_top_k"]
            ])

    print(f"\nSaved {len(runs)} measurements to {RESULTS_FILE} and {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
