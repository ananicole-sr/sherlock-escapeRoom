import csv
import json
import re
import time
from pathlib import Path

from assistant import watson
from search.approximate_search import load_collection, search_approximate
from search.exact_search import exact_search
from evaluation.watson_trial import memory_mb
from search.text_cleaner import normalize_text

BASE_DIR = Path(__file__).resolve().parent.parent
QUESTIONS_FILE = BASE_DIR / "reports" / "results" / "evaluation_questions.json"
RESULTS_FILE = BASE_DIR / "reports" / "results" / "evaluation_results.json"
REVIEW_FILE = BASE_DIR / "reports" / "results" / "evaluation_review.csv"

TOP_K = 5
WARMUP_RUNS = 1
TIMED_RUNS = 5
ENGINES = ["kmp", "z", "approximate"]
APPROXIMATE_SETTINGS = {"method": "combined", "ngram_size": 3, "max_distance": 2}


def search(engine, question, collection, story):
    chunks, vocabulary, document_frequency = collection

    if engine == "approximate":
        return search_approximate(
            question, chunks, vocabulary, document_frequency, top_k=TOP_K, story=story,
            **APPROXIMATE_SETTINGS
        )

    return exact_search(question, algorithm=engine, top_k=TOP_K, story=story)


def timed_search(engine, question, collection, story):
    """
        One warm-up run, then TIMED_RUNS measured runs. Keeps every time:
        the one reported by the engine and the wall time around the call.
    """
    for _ in range(WARMUP_RUNS):
        search(engine, question, collection, story)

    engine_times = []
    wall_times = []
    rankings = []
    response = None

    for _ in range(TIMED_RUNS):
        start = time.perf_counter()
        response = search(engine, question, collection, story)
        wall_times.append(round((time.perf_counter() - start) * 1000, 4))
        engine_times.append(response["retrieval_time_ms"])
        rankings.append([(r["chunk_id"], r["score"]) for r in response["results"]])

    timing = {
        "warmup_runs": WARMUP_RUNS,
        "timed_runs": TIMED_RUNS,
        "engine_reported_ms": engine_times,
        "engine_reported_mean_ms": round(sum(engine_times) / len(engine_times), 4),
        "wall_ms": wall_times,
        "wall_mean_ms": round(sum(wall_times) / len(wall_times), 4),
        "same_results_in_all_runs": all(r == rankings[0] for r in rankings)
    }

    return response, timing


def normalize_quote(text):
    for curly, straight in [("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"')]:
        text = text.replace(curly, straight)

    return " ".join(text.lower().split())


def contains_keyword(answer, keywords):
    text = " " + normalize_text(answer or "") + " "

    for keyword in keywords:
        pattern = r"\b" + re.escape(normalize_text(keyword)) + r"\b"
        if re.search(pattern, text):
            return True

    return False


def preliminary_check(item, reply):
    """
        Automatic first pass, NOT a human evaluation:
          answerable    the answer contains one of the expected keywords
          unanswerable  the model abstained ("I do not know")
    """
    if reply["status"] == "error":
        return "error"

    if item["type"] == "unanswerable":
        return "abstained" if reply["status"] in ("unknown", "no_context") else "answered_anyway"

    if reply["status"] in ("unknown", "no_context"):
        return "abstained"

    return "keyword_found" if contains_keyword(reply["answer"], item["answer_keywords"]) else "keyword_missing"


def run_one(item, engine, collection):
    evidence_ids = sorted({chunk_id for chunk_id, quote in item["evidence"]})

    record = {
        "id": item["id"],
        "story": item["story"],
        "type": item["type"],
        "question": item["question"],
        "original_question": item.get("original_question"),
        "expected_answer": item["expected_answer"],
        "evidence_chunk_ids": evidence_ids,
        "algorithm": engine,
        "story_filter": item["story"],
        "error": None
    }

    try:
        response, timing = timed_search(engine, item["question"], collection, item["story"])
    except Exception as error:
        record["error"] = f"search failed: {type(error).__name__}: {error}"
        record["status"] = "error"
        return record

    retrieved = []

    for rank, result in enumerate(response["results"], start=1):
        retrieved.append({
            "rank": rank,
            "chunk_id": result["chunk_id"],
            "story": result["story"],
            "score": result["score"],
            "matched_terms": result.get("matched_terms"),
            "is_evidence": result["chunk_id"] in evidence_ids
        })

    evidence_ranks = [r["rank"] for r in retrieved if r["is_evidence"]]

    record.update({
        "query_terms": response.get("query_terms"),
        "corrected_terms": response.get("corrected_terms"),
        "corrections": response.get("corrections"),
        "metrics": {
            "candidates_considered": response["candidates_considered"],
            "chunks_examined": response["chunks_examined"],
            "chunks_matched": response["chunks_matched"],
            "results_returned": response["results_returned"],
            "chunks_with_term_match": response.get("chunks_with_term_match")
        },
        "retrieval_timing": timing,
        "retrieved": retrieved,
        "evidence_retrieved": len(evidence_ranks) > 0,
        "best_evidence_rank": min(evidence_ranks) if evidence_ranks else None
    })

    reply = watson.answer_question(item["question"], response)

    evidence_quotes = [quote for chunk_id, quote in item["evidence"]]
    evidence_in_context = any(
        normalize_quote(quote) in normalize_quote(passage["excerpt"])
        for passage in reply["context"] for quote in evidence_quotes
    )

    record.update({
        "context": reply["context"],
        "evidence_in_context": evidence_in_context,
        "prompt": reply["prompt"],
        "prompt_tokens": watson.count_prompt_tokens(reply["prompt"]) if reply["prompt"] else 0,
        "status": reply["status"],
        "answer": reply["answer"],
        "generation_time_ms": reply["generation_time_ms"],
        "error": reply["error"],
        "preliminary_check": preliminary_check(item, reply)
    })

    return record


def configuration():
    spec = watson.current_spec()

    return {
        "questions_file": str(QUESTIONS_FILE.relative_to(BASE_DIR)),
        "engines": ENGINES,
        "top_k": TOP_K,
        "story_filter": "story of each question",
        "approximate_settings": APPROXIMATE_SETTINGS,
        "retrieval_timing": {"warmup_runs": WARMUP_RUNS, "timed_runs": TIMED_RUNS,
                             "excludes_generation": True},
        "model": spec["repo"],
        "device": "cpu",
        "dtype": "float32",
        "context_window": spec["context_window"],
        "input_budget": watson.input_budget(),
        "max_new_tokens": spec["max_new_tokens"],
        "max_chunks": spec["max_chunks"],
        "min_score": watson.MIN_SCORE,
        "do_sample": False,
        "repetition_penalty": 1.1,
        "system_prompt": watson.SYSTEM_PROMPT,
        "one_new_generation_per_question_and_engine": True,
        "preliminary_check": "automatic keyword / abstention check; NOT a human evaluation"
    }


def save(records, started, model_load_ms, finished=False):
    rss, peak = memory_mb()

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump({
            "finished": finished,
            "started_at": started,
            "model_load_ms": model_load_ms,
            "configuration": configuration(),
            "memory_rss_mb": rss,
            "memory_peak_mb": peak,
            "runs": len(records),
            "results": records
        }, file, ensure_ascii=False, indent=2)


def export_review(records):
    columns = [
        "id", "story", "type", "algorithm", "question", "original_question", "expected_answer",
        "model_answer", "status", "evidence_retrieved", "best_evidence_rank", "evidence_in_context",
        "retrieval_mean_ms", "generation_ms", "preliminary_check (automatic, not human)",
        "context_usefulness", "correctness", "answer_support", "comment"
    ]

    with open(REVIEW_FILE, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(columns)

        for r in records:
            writer.writerow([
                r["id"], r["story"], r["type"], r["algorithm"], r["question"],
                r.get("original_question") or "", r.get("expected_answer") or "(no answer in the collection)",
                r.get("answer") or "", r.get("status"), r.get("evidence_retrieved"),
                r.get("best_evidence_rank") or "", r.get("evidence_in_context"),
                r.get("retrieval_timing", {}).get("engine_reported_mean_ms", ""),
                r.get("generation_time_ms", ""), r.get("preliminary_check", "error"),
                "", "", "", ""
            ])


def main():
    if RESULTS_FILE.exists():
        raise SystemExit(f"{RESULTS_FILE} already exists; move it before running again.")

    with open(QUESTIONS_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)["questions"]

    started = time.strftime("%Y-%m-%d %H:%M:%S")

    watson.select_model("qwen")
    start = time.perf_counter()
    watson.load_model()
    model_load_ms = round((time.perf_counter() - start) * 1000, 1)
    print(f"Model loaded in {model_load_ms / 1000:.1f} s")

    collection = load_collection()
    records = []

    for item in questions:
        for engine in ENGINES:
            try:
                record = run_one(item, engine, collection)
            except Exception as error:
                record = {"id": item["id"], "story": item["story"], "type": item["type"],
                          "question": item["question"], "algorithm": engine, "status": "error",
                          "error": f"{type(error).__name__}: {error}"}

            records.append(record)
            print(f"{record['id']} {engine:11} status={record.get('status')} "
                  f"evidence_retrieved={record.get('evidence_retrieved')} "
                  f"in_context={record.get('evidence_in_context')} "
                  f"search={record.get('retrieval_timing', {}).get('engine_reported_mean_ms')} ms "
                  f"gen={record.get('generation_time_ms')} ms "
                  f"check={record.get('preliminary_check')} | {record.get('answer') or record.get('error')}",
                  flush=True)

        save(records, started, model_load_ms)

    save(records, started, model_load_ms, finished=True)
    export_review(records)
    print(f"\nSaved {len(records)} runs to {RESULTS_FILE} and {REVIEW_FILE}")


if __name__ == "__main__":
    main()
