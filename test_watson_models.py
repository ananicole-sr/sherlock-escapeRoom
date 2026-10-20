import json
import sys
import time
from pathlib import Path

import watson
from approximate_search import load_collection, search_approximate

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "data"

# One question per story, searched inside that story as the game does, and
# one question the documents cannot answer.
TRIAL_QUESTIONS = [
    ("What did Holmes discover about the bell rope?", "The Speckled Band", True),
    ("Where did Peterson's wife find the blue stone?", "The Blue Carbuncle", True),
    ("Why was Jabez Wilson paid to copy the Encyclopaedia?", "The Red-Headed League", True),
    ("What colour was the Countess of Morcar's carriage?", "The Blue Carbuncle", False)
]


def memory_mb():
    """
        Current (VmRSS) and peak (VmHWM) resident memory of this process.
    """
    values = {}

    with open("/proc/self/status", "r") as file:
        for line in file:
            if line.startswith("VmRSS:") or line.startswith("VmHWM:"):
                name, amount = line.split(":")
                values[name] = round(int(amount.split()[0]) / 1024, 1)

    return values.get("VmRSS"), values.get("VmHWM")


def main():
    alias = sys.argv[1] if len(sys.argv) > 1 else watson.DEFAULT_MODEL
    watson.select_model(alias)

    chunks, vocabulary, document_frequency = load_collection()

    rss_before, _ = memory_mb()

    start = time.perf_counter()
    watson.load_model()
    load_ms = (time.perf_counter() - start) * 1000

    rss_loaded, _ = memory_mb()

    print(f"\nWATSON TRIAL - {watson.model_name()}")
    print("=" * 78)
    print(f"Model load: {load_ms / 1000:.1f} s   memory: {rss_before} MB -> {rss_loaded} MB")

    records = []

    for question, story, answerable in TRIAL_QUESTIONS:
        response = search_approximate(
            question, chunks, vocabulary, document_frequency, top_k=5, story=story
        )

        reply = watson.answer_question(question, response)
        prompt_tokens = watson.count_prompt_tokens(reply["prompt"]) if reply["prompt"] else 0
        rss_now, rss_peak = memory_mb()

        print(f"\nQ: {question}  [{story}]")
        print(f"   retrieval {response['retrieval_time_ms']:.1f} ms · generation "
              f"{reply['generation_time_ms']:.0f} ms · prompt {prompt_tokens} tokens "
              f"(budget {watson.input_budget()}) · status {reply['status']}")
        print(f"   A: {reply['answer']}")

        for item in reply["context"]:
            print(f"   - {item['chunk_id']}  score {item['score']:.3f}  {item['tokens']} tokens")

        if reply["error"]:
            print(f"   ERROR: {reply['error']}")

        records.append({
            "question": question,
            "story_filter": story,
            "answerable_from_documents": answerable,
            "model": reply["model"],
            "status": reply["status"],
            "answer": reply["answer"],
            "retrieval_time_ms": response["retrieval_time_ms"],
            "generation_time_ms": reply["generation_time_ms"],
            "prompt_tokens": prompt_tokens,
            "input_budget_tokens": watson.input_budget(),
            "context": reply["context"],
            "prompt": reply["prompt"],
            "error": reply["error"],
            "memory_rss_mb": rss_now,
            "memory_peak_mb": rss_peak
        })

    _, rss_peak = memory_mb()
    print(f"\nPeak memory of the process: {rss_peak} MB")

    output = RESULTS_DIR / f"watson_trial_{watson.resolve_model(alias)}.json"

    with open(output, "w", encoding="utf-8") as file:
        json.dump({
            "model": watson.model_name(),
            "device": "cpu",
            "model_load_ms": round(load_ms, 1),
            "memory_before_load_mb": rss_before,
            "memory_after_load_mb": rss_loaded,
            "memory_peak_mb": rss_peak,
            "results": records
        }, file, ensure_ascii=False, indent=2)

    print(f"Results saved to: {output}")


if __name__ == "__main__":
    main()
