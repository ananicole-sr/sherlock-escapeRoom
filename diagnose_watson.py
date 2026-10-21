import json
import time
from pathlib import Path

import watson
from approximate_search import load_collection, search_approximate
from test_watson_models import TRIAL_QUESTIONS, memory_mb
from text_cleaner import tokenize

BASE_DIR = Path(__file__).resolve().parent
OUTPUT = BASE_DIR / "data" / "watson_diagnostic_qwen.json"

# Evidence verified by hand in data/*.txt: the chunk that answers each
# question, phrases that must reach the model, and words that a correct
# answer must contain (an automatic check; the answers are also printed
# for manual review).
EVIDENCE = {
    TRIAL_QUESTIONS[0][0]: {
        "chunk_id": "speckled_band_035",
        "phrases": ["it is not even attached to a wire", "it's a dummy"],
        "answer_keys": ["dummy", "not attached", "not even attached", "attached to no", "no wire"]
    },
    TRIAL_QUESTIONS[1][0]: {
        "chunk_id": "blue_carbuncle_012",
        "phrases": ["my wife found in its crop"],
        "answer_keys": ["crop", "goose"]
    },
    TRIAL_QUESTIONS[2][0]: {
        "chunk_id": "red_headed_league_046",
        "phrases": ["out of the way for a number of hours every day"],
        "answer_keys": ["out of the way", "away from", "absence", "out of his shop", "out of the shop"]
    }
}

CROSS_STORY = (
    "Where did Peterson's wife find the blue stone?", "The Speckled Band", False,
    "Blue Carbuncle question while the filter is The Speckled Band"
)

QUESTIONS = [(q, s, a, "") for q, s, a in TRIAL_QUESTIONS] + [CROSS_STORY]

VARIANTS = {
    # The preprocessing select_context used before this change.
    "before_raw_tokens": lambda question: set(tokenize(question)),
    # The current one, shared with the search engines.
    "after_query_processing": watson.question_terms
}


def normalize(text):
    for curly, straight in [("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"')]:
        text = text.replace(curly, straight)

    return " ".join(text.lower().split())


def contains_any(text, phrases):
    text = normalize(text)

    return any(normalize(phrase) in text for phrase in phrases)


def generation_config():
    spec = watson.current_spec()

    return {
        "model": spec["repo"],
        "device": "cpu",
        "dtype": "float32",
        "context_window": spec["context_window"],
        "input_budget": watson.input_budget(),
        "max_new_tokens": spec["max_new_tokens"],
        "max_chunks": spec["max_chunks"],
        "do_sample": False,
        "repetition_penalty": 1.1,
        "system_prompt": watson.SYSTEM_PROMPT
    }


def classify(answerable, evidence, retrieved, context, reply):
    """
        retrieval  : the chunk with the evidence was not retrieved
        selection  : it was retrieved but the evidence did not reach the prompt
        generation : the evidence was in the prompt and the answer is wrong,
                     or there was no evidence and the model answered anyway
    """
    answer = reply["answer"] or ""

    if not answerable:
        if reply["status"] == "unknown":
            return "none (correctly said it does not know)"
        return "generation (answered without supporting evidence)"

    if evidence["chunk_id"] not in [item["chunk_id"] for item in retrieved]:
        return "retrieval"

    if not any(contains_any(item["excerpt"], evidence["phrases"]) for item in context):
        return "selection"

    if contains_any(answer, evidence["answer_keys"]):
        return "none (answer contains the evidence)"

    return "generation (evidence in context, wrong answer)"


def single_fragment(question, evidence, chunks_by_id):
    chunk = chunks_by_id[evidence["chunk_id"]]
    context = [{
        "chunk_id": chunk["id"],
        "story": chunk["story"],
        "score": None,
        "excerpt": chunk["original_text"],
        "tokens": watson.count_tokens(chunk["original_text"])
    }]
    prompt = watson.build_prompt(question, context)

    start = time.perf_counter()
    answer = watson.generate(prompt)
    generation_ms = round((time.perf_counter() - start) * 1000, 1)

    if answer:
        answer = answer[0].upper() + answer[1:]

    return {
        "chunk_id": chunk["id"],
        "evidence_in_context": contains_any(chunk["original_text"], evidence["phrases"]),
        "prompt": prompt,
        "prompt_tokens": watson.count_prompt_tokens(prompt),
        "answer": answer,
        "status": "unknown" if watson.is_unknown(answer) else "ok",
        "answer_contains_evidence": contains_any(answer, evidence["answer_keys"]),
        "generation_time_ms": generation_ms
    }


def main():
    watson.select_model("qwen")
    watson.load_model()

    chunks, vocabulary, document_frequency = load_collection()
    chunks_by_id = {chunk["id"]: chunk for chunk in chunks}
    original_terms = watson.question_terms

    records = []

    for question, story, answerable, note in QUESTIONS:
        evidence = EVIDENCE.get(question) if answerable else None

        response = search_approximate(
            question, chunks, vocabulary, document_frequency, top_k=5, story=story
        )

        retrieved = [{
            "rank": rank,
            "chunk_id": result["chunk_id"],
            "story": result["story"],
            "score": result["score"],
            "contains_evidence": bool(evidence) and result["chunk_id"] == evidence["chunk_id"]
        } for rank, result in enumerate(response["results"], start=1)]

        print(f"\nQ: {question}  [filter: {story}] {note}")
        print(f"   retrieved: {[r['chunk_id'] for r in retrieved]}"
              f"   ({response['retrieval_time_ms']:.1f} ms)")

        record = {
            "question": question,
            "story_filter": story,
            "answerable_from_filtered_documents": answerable,
            "note": note,
            "evidence": evidence,
            "search": {
                "engine": response["algorithm"],
                "query_terms": response["query_terms"],
                "corrected_terms": response["corrected_terms"],
                "retrieval_time_ms": response["retrieval_time_ms"],
                "candidates_considered": response["candidates_considered"],
                "chunks_examined": response["chunks_examined"],
                "chunks_matched": response["chunks_matched"],
                "results_returned": response["results_returned"],
                "retrieved": retrieved
            },
            "variants": {}
        }

        for name, terms_function in VARIANTS.items():
            watson.question_terms = terms_function

            reply = watson.answer_question(question, response)
            context = reply["context"]

            evidence_in_context = bool(evidence) and any(
                contains_any(item["excerpt"], evidence["phrases"]) for item in context
            )

            failure = classify(answerable, evidence, retrieved, context, reply)

            record["variants"][name] = {
                "question_terms_used": sorted(terms_function(question)),
                "context": context,
                "evidence_in_context": evidence_in_context,
                "prompt": reply["prompt"],
                "prompt_tokens": watson.count_prompt_tokens(reply["prompt"]) if reply["prompt"] else 0,
                "status": reply["status"],
                "answer": reply["answer"],
                "generation_time_ms": reply["generation_time_ms"],
                "error": reply["error"],
                "failure_stage": failure
            }

            print(f"   [{name}] context {[c['chunk_id'] for c in context]}"
                  f" evidence_in_context={evidence_in_context}")
            print(f"      A ({reply['generation_time_ms']:.0f} ms, {reply['status']}): {reply['answer']}")
            print(f"      -> failure stage: {failure}")

        watson.question_terms = original_terms

        before = record["variants"]["before_raw_tokens"]
        after = record["variants"]["after_query_processing"]
        record["before_after_same_prompt"] = before["prompt"] == after["prompt"]

        if answerable:
            single = single_fragment(question, evidence, chunks_by_id)
            record["single_fragment_test"] = single
            print(f"   [single fragment {single['chunk_id']}] "
                  f"({single['generation_time_ms']:.0f} ms, {single['status']}): {single['answer']}")

        records.append(record)

    rss, peak = memory_mb()

    output = OUTPUT
    if output.exists():
        output = output.with_name(f"{output.stem}_{time.strftime('%Y%m%d_%H%M%S')}.json")

    with open(output, "w", encoding="utf-8") as file:
        json.dump({
            "purpose": "Diagnostic of Watson (not the 20-question evaluation)",
            "retrieval": "approximate search with the case story filter, top_k=5 (same path as the game)",
            "generation_config": generation_config(),
            "memory_rss_mb": rss,
            "memory_peak_mb": peak,
            "results": records
        }, file, ensure_ascii=False, indent=2)

    print(f"\nSaved to: {output}")


FOLLOWUP_OUTPUT = BASE_DIR / "data" / "watson_diagnostic_qwen_followup.json"


def followup():
    """
        Repeats only what changed after sending whole fragments and fixing
        ligatures (æ -> ae). A prompt identical to one already generated in
        the first diagnostic reuses that answer (greedy decoding gives the
        same output for the same prompt); any other prompt is generated.
    """
    with open(OUTPUT, "r", encoding="utf-8") as file:
        previous = json.load(file)

    watson.select_model("qwen")
    watson.load_model()

    chunks, vocabulary, document_frequency = load_collection()
    records = []

    for old in previous["results"]:
        question, story = old["question"], old["story_filter"]
        answerable = old["answerable_from_filtered_documents"]
        evidence = old["evidence"]

        response = search_approximate(
            question, chunks, vocabulary, document_frequency, top_k=5, story=story
        )

        retrieved = [{
            "rank": rank,
            "chunk_id": result["chunk_id"],
            "score": result["score"],
            "contains_evidence": bool(evidence) and result["chunk_id"] == evidence["chunk_id"]
        } for rank, result in enumerate(response["results"], start=1)]

        context = watson.select_context(question, response["results"])
        prompt = watson.build_prompt(question, context)

        reused_from = None
        for name, variant in old["variants"].items():
            if variant["prompt"] == prompt:
                reused_from = name

        if reused_from:
            done = old["variants"][reused_from]
            reply = {"status": done["status"], "answer": done["answer"], "context": context,
                     "generation_time_ms": done["generation_time_ms"], "prompt": prompt, "error": None}
        else:
            reply = watson.answer_question(question, response)

        failure = classify(answerable, evidence, retrieved, reply["context"], reply)

        record = {
            "question": question,
            "story_filter": story,
            "answerable_from_filtered_documents": answerable,
            "retrieved": retrieved,
            "retrieved_changed": [r["chunk_id"] for r in retrieved]
                                 != [r["chunk_id"] for r in old["search"]["retrieved"]],
            "context": reply["context"],
            "trimmed_passages": sum(1 for item in reply["context"] if item.get("trimmed")),
            "evidence_in_context": bool(evidence) and any(
                contains_any(item["excerpt"], evidence["phrases"]) for item in reply["context"]),
            "prompt": reply["prompt"],
            "prompt_tokens": watson.count_prompt_tokens(reply["prompt"]) if reply["prompt"] else 0,
            "input_budget": watson.input_budget(),
            "generated_again": reused_from is None,
            "reused_answer_from": reused_from,
            "status": reply["status"],
            "answer": reply["answer"],
            "generation_time_ms": reply["generation_time_ms"],
            "retrieval_time_ms": response["retrieval_time_ms"],
            "failure_stage": failure,
            "previous_answer_after_query_processing": old["variants"]["after_query_processing"]["answer"],
            "single_fragment_test": "unchanged: same prompt as in the first diagnostic"
                                    if answerable else None
        }
        records.append(record)

        print(f"\nQ: {question}  [filter: {story}]")
        print(f"   retrieved: {[r['chunk_id'] for r in retrieved]}  changed={record['retrieved_changed']}")
        print(f"   prompt {record['prompt_tokens']} tokens (budget {record['input_budget']}), "
              f"trimmed passages {record['trimmed_passages']}, evidence_in_context={record['evidence_in_context']}")
        print(f"   {'generated' if reused_from is None else 'reused from ' + reused_from}"
              f" ({reply['generation_time_ms']:.0f} ms, {reply['status']}): {reply['answer']}")
        print(f"   -> failure stage: {failure}")

    output = FOLLOWUP_OUTPUT
    if output.exists():
        output = output.with_name(f"{output.stem}_{time.strftime('%Y%m%d_%H%M%S')}.json")

    with open(output, "w", encoding="utf-8") as file:
        json.dump({
            "purpose": "Follow-up of the Watson diagnostic after: whole fragments when they fit, "
                       "and ligature normalization (ae, oe) with regenerated index and vocabulary",
            "generation_config": generation_config(),
            "results": records
        }, file, ensure_ascii=False, indent=2)

    print(f"\nSaved to: {output}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "followup":
        followup()
    else:
        main()
