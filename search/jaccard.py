
def word_ngrams(tokens, n=1):
    if n <= 1:
        return set(tokens)

    ngrams = set()

    for i in range(len(tokens) - n + 1):
        ngram = " ".join(tokens[i:i + n])
        ngrams.add(ngram)

    return ngrams


def char_ngrams(text, n=3):
    text = text.replace(" ", "")

    ngrams = set()

    for i in range(len(text) - n + 1):
        ngrams.add(text[i:i + n])

    return ngrams


def jaccard_similarity(set_a, set_b):
    if len(set_a) == 0 and len(set_b) == 0:
        return 0.0

    intersection = set_a & set_b
    union = set_a | set_b

    return len(intersection) / len(union)


def main():
    print("\nSHERLOCK HOLMES - JACCARD SIMILARITY")
    print("=" * 50)

    question_tokens = ["bell", "rope", "bedroom"]
    chunk_tokens = ["holmes", "inspected", "the", "bell",
                    "rope", "inside", "the", "bedroom"]

    question_words = word_ngrams(question_tokens, 1)
    chunk_words = word_ngrams(chunk_tokens, 1)

    print("\nExample with words:")
    print(f"  question words: {sorted(question_words)}")
    print(f"  chunk words:    {sorted(chunk_words)}")
    print(f"  intersection:   {sorted(question_words & chunk_words)}")
    print(f"  union size:     {len(question_words | chunk_words)}")
    print(f"  similarity:     {jaccard_similarity(question_words, chunk_words):.4f}")

    print("\nExample with word bigrams:")

    question_bigrams = word_ngrams(question_tokens, 2)
    chunk_bigrams = word_ngrams(chunk_tokens, 2)

    print(f"  question bigrams: {sorted(question_bigrams)}")
    print(f"  similarity:       {jaccard_similarity(question_bigrams, chunk_bigrams):.4f}")

    print("\nExample with character trigrams (tolerates typos):")

    correct = char_ngrams("bell rope", 3)
    misspelled = char_ngrams("bel roap", 3)

    print(f"  'bell rope' trigrams: {sorted(correct)}")
    print(f"  'bel roap'  trigrams: {sorted(misspelled)}")
    print(f"  similarity:           {jaccard_similarity(correct, misspelled):.4f}")


if __name__ == "__main__":
    main()
