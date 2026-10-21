import json
from pathlib import Path
from search.text_cleaner import normalize_text, tokenize

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

INPUT_FILE = DATA_DIR / "chunks.json"
OUTPUT_FILE = DATA_DIR / "processed_chunks.json"


def preprocess_chunks():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    processed_chunks = []

    for chunk in chunks:

        original_text = chunk["original_text"]

        normalized_text = normalize_text(original_text)
        tokens = tokenize(original_text)

        processed_chunk = {
            "id": chunk["id"],
            "story": chunk["story"],
            "original_text": original_text,
            "normalized_text": normalized_text,
            "tokens": tokens,
            "position": chunk["position"]
        }

        processed_chunks.append(processed_chunk)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            processed_chunks,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\nSHERLOCK HOLMES - TEXT PREPROCESSING")
    print("=" * 50)

    print(f"Total chunks processed: {len(processed_chunks)}")

    total_tokens = sum(
        len(chunk["tokens"])
        for chunk in processed_chunks
    )

    unique_words = set()

    for chunk in processed_chunks:
        unique_words.update(chunk["tokens"])

    print(f"Total tokens: {total_tokens}")
    print(f"Unique words: {len(unique_words)}")
    print(f"Output saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    preprocess_chunks()
