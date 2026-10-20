
import json
import time
from pathlib import Path

from approximate_search import load_collection, search_approximate

BASE_DIR = Path(__file__).resolve().parent
RESULTS_FILE = BASE_DIR / "data" / "approximate_results.json"

TEST_QUERIES = [
    "What happened to the bell rope?",
    "Who was Dr Roylott and what did he keep in his room?",
    "What was the speckled band?",
    "Why did Helen hear a whistle at night?",
    "Where was the ventilator in the bedroom?",
    "Who found the blue carbuncle in the goose?",
    "What happened to the hat that Peterson found?",
    "Who was arrested for stealing the jewel?",
    "What was the Red-Headed League about?",
    "Why did Jabez Wilson copy the encyclopedia?",
    "What did Holmes find under the pavement?",
    "Who was the assistant Vincent Spaulding really?"
]

MISSPELLED_QUERIES = [
    "What happened to the bel roap?",
    "What was the spekled band?",
    "Who stole the blu carbunkle?",
    "What was the Red Heded Leage about?",
    "Where was the ventilater in the bedrom?"
]


def print_table_header():
    print(f"{'#':>3} {'query':<48} {'time(ms)':>9} {'top chunk':<22} {'score':>8}")
    print("-" * 95)


def run_queries(queries, chunks, vocabulary, document_frequency, label):
    print(f"\n{label}")
    print("=" * 95)
    print_table_header()

    records = []
    total_time = 0.0

    for position, question in enumerate(queries, start=1):

        response = search_approximate(
            question, chunks, vocabulary, document_frequency, top_k=3
        )

        total_time = total_time + response["retrieval_time_ms"]

        if len(response["results"]) > 0:
            top = response["results"][0]
            top_id = top["chunk_id"]
            top_score = top["score"]
        else:
            top_id = "none"
            top_score = 0.0

        short_query = question[:46]

        print(f"{position:>3} {short_query:<48} "
              f"{response['retrieval_time_ms']:>9.2f} {top_id:<22} {top_score:>8.4f}")

        records.append(response)

    average_time = total_time / len(queries)

    print("-" * 95)
    print(f"Average retrieval time: {average_time:.2f} ms over {len(queries)} queries")

    return records, average_time


def compare_methods(chunks, vocabulary, document_frequency):
    print("\nCOMPARISON OF SCORING METHODS")
    print("=" * 95)

    question = "What happened to the bell rope in the bedroom?"
    methods = ["coverage", "jaccard_words", "jaccard_ngrams", "combined"]

    print(f"Query: {question}\n")
    print(f"{'method':<16} {'time(ms)':>9}  top 3 chunks")
    print("-" * 95)

    for method in methods:

        response = search_approximate(
            question, chunks, vocabulary, document_frequency,
            top_k=3, method=method
        )

        top_ids = []

        for result in response["results"]:
            top_ids.append(f"{result['chunk_id']}({result['score']:.3f})")

        print(f"{method:<16} {response['retrieval_time_ms']:>9.2f}  {', '.join(top_ids)}")


def measure_collection_growth(chunks, vocabulary, document_frequency):
    print("\nEFFECT OF COLLECTION SIZE")
    print("=" * 95)

    question = "What happened to the bell rope in the bedroom?"
    sizes = [25, 50, 75, 100, 147]

    print(f"{'chunks':>8} {'time(ms)':>10} {'ms per chunk':>14}")
    print("-" * 35)

    for size in sizes:

        subset = chunks[:size]

        total = 0.0
        repetitions = 5

        for _ in range(repetitions):
            response = search_approximate(
                question, subset, vocabulary, document_frequency, top_k=3
            )
            total = total + response["retrieval_time_ms"]

        average = total / repetitions

        print(f"{size:>8} {average:>10.2f} {average / size:>14.4f}")


def measure_correction_cost(chunks, vocabulary, document_frequency):
    print("\nCOST OF THE LEVENSHTEIN CORRECTION")
    print("=" * 95)

    pairs = [
        ("no typos", "What happened to the bell rope in the bedroom?"),
        ("one typo", "What happened to the bel rope in the bedroom?"),
        ("three typos", "What happend to the bel roap in the bedrom?")
    ]

    print(f"{'case':<14} {'correction(ms)':>16} {'scoring(ms)':>13} {'total(ms)':>11}")
    print("-" * 60)

    for label, question in pairs:

        response = search_approximate(
            question, chunks, vocabulary, document_frequency, top_k=3
        )

        print(f"{label:<14} {response['correction_time_ms']:>16.2f} "
              f"{response['scoring_time_ms']:>13.2f} "
              f"{response['retrieval_time_ms']:>11.2f}")


def main():
    print("\nSHERLOCK HOLMES - APPROXIMATE SEARCH EVALUATION")
    print("=" * 95)

    load_start = time.perf_counter()
    chunks, vocabulary, document_frequency = load_collection()
    load_ms = (time.perf_counter() - load_start) * 1000

    print(f"Chunks: {len(chunks)}")
    print(f"Content vocabulary: {len(vocabulary)} words")
    print(f"Collection loaded in {load_ms:.1f} ms")

    clean_records, clean_average = run_queries(
        TEST_QUERIES, chunks, vocabulary, document_frequency,
        "QUERIES WITHOUT TYPOS"
    )

    typo_records, typo_average = run_queries(
        MISSPELLED_QUERIES, chunks, vocabulary, document_frequency,
        "QUERIES WITH TYPOS (Levenshtein correction)"
    )

    print("\nCorrections applied in the misspelled queries:")
    print("-" * 60)

    for response in typo_records:
        if len(response["corrections"]) > 0:
            for original, corrected, distance in response["corrections"]:
                print(f"  '{original}' -> '{corrected}'  (distance {distance})")

    compare_methods(chunks, vocabulary, document_frequency)
    measure_collection_growth(chunks, vocabulary, document_frequency)
    measure_correction_cost(chunks, vocabulary, document_frequency)

    print("\nSUMMARY")
    print("=" * 95)
    print(f"Average time without typos: {clean_average:.2f} ms")
    print(f"Average time with typos:    {typo_average:.2f} ms")

    all_records = clean_records + typo_records

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(all_records, file, ensure_ascii=False, indent=2)

    print(f"\nResults saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
