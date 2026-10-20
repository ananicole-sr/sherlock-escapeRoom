import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHUNK_SIZE = 200

STORIES = {
    "speckled_band.txt": "The Speckled Band",
    "blue_carbuncle.txt": "The Blue Carbuncle",
    "red_headed_league.txt": "The Red-Headed League"
}


def read_document(file_path):
    with open(file_path, "r", encoding="utf-8-sig") as file:
        return file.read()


def split_into_chunks(text, chunk_size=200):
    text = re.sub(r"\s+", " ", text).strip()

    sentences = re.split(r"(?<=[.!?])\s+(?=[\"'“‘A-Z])", text)

    chunks = []
    current_chunk = []
    current_word_count = 0

    for sentence in sentences:
        words = sentence.split()
        word_count = len(words)

        if current_chunk and current_word_count + word_count > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_word_count = 0

        if word_count > chunk_size:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_word_count = 0

            for i in range(0, word_count, chunk_size):
                chunks.append(" ".join(words[i:i + chunk_size]))

            continue

        current_chunk.append(sentence)
        current_word_count += word_count

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def process_documents():
    all_chunks = []

    print("\nSHERLOCK HOLMES - DOCUMENT PROCESSING")
    print("=" * 50)

    for filename, story_name in STORIES.items():
        file_path = DATA_DIR / filename

        if not file_path.exists():
            print(f"ERROR: File not found: {file_path}")
            continue

        text = read_document(file_path)

        word_count = len(text.split())
        character_count = len(text)

        chunks = split_into_chunks(text, CHUNK_SIZE)

        story_id = Path(filename).stem

        for position, chunk in enumerate(chunks, start=1):
            all_chunks.append({
                "id": f"{story_id}_{position:03d}",
                "story": story_name,
                "original_text": chunk,
                "position": position
            })

        print(f"\nStory: {story_name}")
        print(f"Words: {word_count}")
        print(f"Characters: {character_count}")
        print(f"Chunks generated: {len(chunks)}")

    output_path = DATA_DIR / "chunks.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(all_chunks, file, ensure_ascii=False, indent=4)

    print("\n" + "=" * 50)
    print(f"Total chunks generated: {len(all_chunks)}")
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    process_documents()
