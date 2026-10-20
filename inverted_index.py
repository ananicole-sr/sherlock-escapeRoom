
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "processed_chunks.json"
OUTPUT_FILE = DATA_DIR / "inverted_index.json"
VOCABULARY_FILE = DATA_DIR / "vocabulary.json"


def build_inverted_index(chunks):
    inverted_index = {}

    for chunk in chunks:
        chunk_id = chunk["id"]

        unique_tokens = set(chunk["tokens"])

        for word in unique_tokens:
            if word not in inverted_index:
                inverted_index[word] = []

            inverted_index[word].append(chunk_id)

    return inverted_index


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    inverted_index = build_inverted_index(chunks)

    inverted_index = {
        word: sorted(inverted_index[word])
        for word in sorted(inverted_index)
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(inverted_index, file, ensure_ascii=False, indent=4)

    vocabulary = list(inverted_index.keys())

    with open(VOCABULARY_FILE, "w", encoding="utf-8") as file:
        json.dump(vocabulary, file, ensure_ascii=False, indent=4)

    print("\nSHERLOCK HOLMES - INVERTED INDEX")
    print("=" * 50)
    print(f"Total chunks indexed: {len(chunks)}")
    print(f"Unique indexed words: {len(inverted_index)}")
    print(f"Inverted index saved to: {OUTPUT_FILE}")
    print(f"Vocabulary saved to: {VOCABULARY_FILE}")

    example_word = "holmes"
    matches = inverted_index.get(example_word, [])

    print(f"\nExample search: '{example_word}'")
    print(f"Found in {len(matches)} chunks")
    print(f"First matches: {matches[:5]}")


if __name__ == "__main__":
    main()
