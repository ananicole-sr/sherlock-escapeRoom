
import json
import time
from pathlib import Path

from search.levenshtein import closest_word
from search.jaccard import char_ngrams, jaccard_similarity

# Shared with the exact engine. extract_query_terms is re-exported here so
# existing imports keep working.
from search.query_processing import STOPWORDS, extract_query_terms

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

CHUNKS_FILE = DATA_DIR / "processed_chunks.json"
VOCABULARY_FILE = DATA_DIR / "vocabulary.json"
INDEX_FILE = DATA_DIR / "inverted_index.json"

def load_collection():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    with open(VOCABULARY_FILE, "r", encoding="utf-8") as file:
        vocabulary = json.load(file)

    with open(INDEX_FILE, "r", encoding="utf-8") as file:
        inverted_index = json.load(file)

    document_frequency = {}

    for word in inverted_index:
        document_frequency[word] = len(inverted_index[word])

    content_vocabulary = []

    for word in vocabulary:
        if word not in STOPWORDS:
            content_vocabulary.append(word)

    for chunk in chunks:

        content_tokens = set()

        for token in chunk["tokens"]:
            if token not in STOPWORDS:
                content_tokens.add(token)

        chunk["content_tokens"] = content_tokens
        chunk["char_ngrams"] = None

    return chunks, content_vocabulary, document_frequency


def correct_query_terms(terms, vocabulary, document_frequency, max_distance=2):
    """
        Spelling correction with Levenshtein. Only the approximate strategy
        uses it; the exact engine searches the terms as they were written.
    """
    vocabulary_set = set(vocabulary)

    corrected_terms = []
    corrections = []

    for term in terms:

        if term in vocabulary_set:
            corrected_terms.append(term)
            continue

        best_word, distance = closest_word(
            term, vocabulary, max_distance, document_frequency
        )

        if best_word is None:
            corrected_terms.append(term)
        else:
            corrected_terms.append(best_word)
            corrections.append((term, best_word, distance))

    return corrected_terms, corrections


def chunk_char_ngrams(chunk, ngram_size):
    if chunk["char_ngrams"] is None:
        chunk["char_ngrams"] = char_ngrams(chunk["normalized_text"], ngram_size)

    return chunk["char_ngrams"]


def search_approximate(question, chunks, vocabulary, document_frequency,
                       top_k=5, max_distance=2, ngram_size=3,
                       weight_coverage=0.6, weight_words=0.25,
                       weight_ngrams=0.15, method="combined", story=None):

    start_time = time.perf_counter()

    terms = extract_query_terms(question)

    correction_start = time.perf_counter()

    corrected_terms, corrections = correct_query_terms(
        terms, vocabulary, document_frequency, max_distance
    )

    correction_ms = (time.perf_counter() - correction_start) * 1000

    scoring_start = time.perf_counter()

    query_words = set(corrected_terms)
    query_text = " ".join(corrected_terms)
    query_ngrams = char_ngrams(query_text, ngram_size)

    if story is None:
        searched_chunks = chunks
    else:
        searched_chunks = []
        for chunk in chunks:
            if chunk["story"] == story:
                searched_chunks.append(chunk)

    scored_chunks = []

    for chunk in searched_chunks:

        matched = query_words & chunk["content_tokens"]

        if len(query_words) == 0:
            coverage = 0.0
        else:
            coverage = len(matched) / len(query_words)

        similarity_words = jaccard_similarity(query_words, chunk["content_tokens"])

        similarity_ngrams = jaccard_similarity(
            query_ngrams, chunk_char_ngrams(chunk, ngram_size)
        )

        combined = weight_coverage * coverage
        combined = combined + weight_words * similarity_words
        combined = combined + weight_ngrams * similarity_ngrams

        if method == "jaccard_words":
            score = similarity_words
        elif method == "jaccard_ngrams":
            score = similarity_ngrams
        elif method == "coverage":
            score = coverage
        else:
            score = combined

        scored_chunks.append({
            "chunk_id": chunk["id"],
            "story": chunk["story"],
            "text": chunk["original_text"],
            "score": round(score, 6),
            "jaccard_words": round(similarity_words, 6),
            "jaccard_ngrams": round(similarity_ngrams, 6),
            "coverage": round(coverage, 6),
            "matched_terms": sorted(matched)
        })

    # Only chunks with a positive score count as found; the chunk id breaks
    # ties so the ranking is reproducible.
    found = [result for result in scored_chunks if result["score"] > 0]
    found.sort(key=lambda result: (-result["score"], result["chunk_id"]))

    with_term = sum(1 for result in scored_chunks if result["coverage"] > 0)

    results = found[:top_k]

    scoring_ms = (time.perf_counter() - scoring_start) * 1000

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    return {
        "query": question,
        "algorithm": "levenshtein+jaccard",
        "method": method,
        "retrieval_time_ms": round(elapsed_ms, 3),
        "correction_time_ms": round(correction_ms, 3),
        "scoring_time_ms": round(scoring_ms, 3),
        "query_terms": terms,
        "corrected_terms": corrected_terms,
        "corrections": corrections,
        # Metrics (same meaning in the exact engine):
        #   candidates_considered  chunks the engine could look at before
        #                          the story filter (the whole collection;
        #                          this engine uses no index)
        #   chunks_examined        chunks actually scored, after the filter
        #   chunks_matched         chunks with score > 0, before top_k
        #   results_returned       results returned, after top_k
        #   chunks_with_term_match chunks containing at least one query term
        #                          (character n-grams give almost every
        #                          chunk a small positive score)
        "candidates_considered": len(chunks),
        "chunks_examined": len(searched_chunks),
        "chunks_matched": len(found),
        "results_returned": len(results),
        "chunks_with_term_match": with_term,
        "story_filter": story,
        "results": results
    }


def main():
    print("\nSHERLOCK HOLMES - APPROXIMATE SEARCH")
    print("=" * 50)

    chunks, vocabulary, document_frequency = load_collection()

    print(f"Chunks loaded: {len(chunks)}")
    print(f"Content vocabulary size: {len(vocabulary)}")

    question = "What happened to the bel rope in the bedrom?"

    response = search_approximate(
        question, chunks, vocabulary, document_frequency, top_k=3
    )

    print(f"\nQuestion: {response['query']}")
    print(f"Extracted terms: {response['query_terms']}")
    print(f"Corrected terms: {response['corrected_terms']}")

    if response["corrections"]:
        print("\nCorrections made with Levenshtein:")
        for original, corrected, distance in response["corrections"]:
            print(f"  '{original}' -> '{corrected}'  (distance {distance})")

    print(f"\nRetrieval time: {response['retrieval_time_ms']} ms")
    print(f"Chunks examined: {response['chunks_examined']}")

    print("\nTop results:")

    for position, result in enumerate(response["results"], start=1):
        print(f"\n  {position}. {result['chunk_id']}  ({result['story']})")
        print(f"     score: {result['score']:.4f}"
              f"   coverage: {result['coverage']:.2f}"
              f"   words: {result['jaccard_words']:.4f}"
              f"   ngrams: {result['jaccard_ngrams']:.4f}")
        print(f"     matched: {result['matched_terms']}")
        print(f"     {result['text'][:150]}...")


if __name__ == "__main__":
    main()
