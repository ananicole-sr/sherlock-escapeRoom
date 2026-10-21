
import json
import time
from pathlib import Path

from text_cleaner import tokenize
from kmp import kmp_search
from z_function import z_search


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

with open(DATA_DIR / "processed_chunks.json", "r", encoding="utf-8") as file:
    CHUNKS = json.load(file)

with open(DATA_DIR / "inverted_index.json", "r", encoding="utf-8") as file:
    INVERTED_INDEX = json.load(file)

CHUNK_MAP = {chunk["id"]: chunk for chunk in CHUNKS}

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were",
    "what", "who", "where", "when", "why", "how",
    "about", "to", "of", "in", "on", "at", "for",
    "and", "or", "it", "this", "that", "did",
    "does", "do", "with", "from", "there"
}


def extract_keywords(query):
    tokens = tokenize(query)

    keywords = []
    seen = set()

    for token in tokens:
        if token not in STOPWORDS and token not in seen:
            keywords.append(token)
            seen.add(token)

    return keywords


def exact_search(query, algorithm="kmp", top_k=5, story=None):
    if algorithm == "kmp":
        search_function = kmp_search
    elif algorithm == "z":
        search_function = z_search
    else:
        raise ValueError("Algorithm must be 'kmp' or 'z'")

    start_time = time.perf_counter()

    keywords = extract_keywords(query)

    candidate_ids = set()

    for keyword in keywords:
        candidate_ids.update(INVERTED_INDEX.get(keyword, []))

    results = []

    for chunk_id in candidate_ids:
        chunk = CHUNK_MAP[chunk_id]

        if story is not None and chunk["story"] != story:
            continue

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

    return {
        "query": query,
        "algorithm": algorithm,
        "keywords": keywords,
        "retrieval_time_ms": round(retrieval_time_ms, 4),
        "chunks_examined": len(candidate_ids),
        "chunks_recovered": len(results),
        "results": results[:top_k]
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
        print(f"Chunks examined: {output['chunks_examined']}")
        print(f"Chunks recovered: {output['chunks_recovered']}")

        print("\nTOP 5 RESULTS:")

        for i, result in enumerate(output["results"], start=1):

            print(f"\n{i}. Chunk: {result['chunk_id']}")
            print(f"   Story: {result['story']}")
            print(f"   Score: {result['score']}")
            print(f"   Matched terms: {result['matched_terms']}")
            print(f"   Text: {result['text'][:250]}...")
