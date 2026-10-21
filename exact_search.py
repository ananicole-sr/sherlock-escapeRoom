
import json
import time
from pathlib import Path

from kmp import kmp_search
from z_function import z_search

# Same preprocessing as the approximate engine, without spelling correction:
# exact search looks for the terms exactly as they were written.
from query_processing import extract_query_terms


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

with open(DATA_DIR / "processed_chunks.json", "r", encoding="utf-8") as file:
    CHUNKS = json.load(file)

with open(DATA_DIR / "inverted_index.json", "r", encoding="utf-8") as file:
    INVERTED_INDEX = json.load(file)

CHUNK_MAP = {chunk["id"]: chunk for chunk in CHUNKS}

def extract_keywords(query):
    return extract_query_terms(query)


def exact_search(query, algorithm="kmp", top_k=5, story=None):
    if algorithm == "kmp":
        search_function = kmp_search
    elif algorithm == "z":
        search_function = z_search
    else:
        raise ValueError("Algorithm must be 'kmp' or 'z'")

    start_time = time.perf_counter()

    keywords = extract_keywords(query)

    # Candidates: chunks that contain at least one keyword according to the
    # inverted index (hashing), in any story.
    candidate_ids = set()

    for keyword in keywords:
        candidate_ids.update(INVERTED_INDEX.get(keyword, []))

    # Examined: the candidates that pass the story filter. Only these are
    # scanned with KMP or the Z-function.
    examined_ids = sorted(
        chunk_id for chunk_id in candidate_ids
        if story is None or CHUNK_MAP[chunk_id]["story"] == story
    )

    results = []

    for chunk_id in examined_ids:
        chunk = CHUNK_MAP[chunk_id]

        text = chunk["normalized_text"]

        score = 0
        matched_terms = {}

        for keyword in keywords:
            pattern = f" {keyword} "
            searchable_text = f" {text} "

            positions = search_function(searchable_text, pattern)

            if positions:
                frequency = len(positions)
                score += 5 + frequency

                matched_terms[keyword] = frequency

        if score > 0:
            results.append({
                "chunk_id": chunk["id"],
                "story": chunk["story"],
                "text": chunk["original_text"],
                "score": score,
                "matched_terms": matched_terms
            })

    results.sort(
        key=lambda result: (-result["score"], result["chunk_id"])
    )

    retrieval_time_ms = (time.perf_counter() - start_time) * 1000

    returned = results[:top_k]

    return {
        "query": query,
        "algorithm": algorithm,
        "keywords": keywords,
        "query_terms": keywords,
        "story_filter": story,
        "retrieval_time_ms": round(retrieval_time_ms, 4),
        # Metrics (same meaning in the approximate engine):
        #   candidates_considered  chunks proposed by the inverted index,
        #                          before the story filter
        #   chunks_examined        chunks scanned with KMP / Z, after it
        #   chunks_matched         chunks with at least one exact match,
        #                          before top_k
        #   results_returned       results returned, after top_k
        "candidates_considered": len(candidate_ids),
        "chunks_examined": len(examined_ids),
        "chunks_matched": len(results),
        "results_returned": len(returned),
        "chunks_recovered": len(results),   # older name of chunks_matched
        "results": returned
    }


if __name__ == "__main__":

    question = "What was unusual about the bell rope?"

    for algorithm in ["kmp", "z"]:

        output = exact_search(
            query=question,
            algorithm=algorithm,
            top_k=5,
            story="The Speckled Band"
        )

        print("\n" + "=" * 60)
        print(f"ALGORITHM: {algorithm.upper()}")
        print("=" * 60)

        print(f"Question: {output['query']}")
        print(f"Keywords: {output['keywords']}")
        print(f"Retrieval time: {output['retrieval_time_ms']} ms")
        print(f"Candidates considered: {output['candidates_considered']}")
        print(f"Chunks examined: {output['chunks_examined']}")
        print(f"Chunks matched: {output['chunks_matched']}")
        print(f"Results returned: {output['results_returned']}")

        print("\nTOP 5 RESULTS:")

        for i, result in enumerate(output["results"], start=1):

            print(f"\n{i}. Chunk: {result['chunk_id']}")
            print(f"   Story: {result['story']}")
            print(f"   Score: {result['score']}")
            print(f"   Matched terms: {result['matched_terms']}")
            print(f"   Text: {result['text'][:250]}...")
