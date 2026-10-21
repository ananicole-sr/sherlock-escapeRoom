
# -------------------------------------------------------------------------
# WATSON (stage 5): retrieval-augmented answers with a Hugging Face model.
#
# 1. The search engine (exact or approximate) returns ranked chunks.
# 2. select_context() keeps the best ones that bring new information,
#    trims each one to its most relevant sentences and makes sure the whole
#    prompt (instructions + passages + question) plus the space reserved for
#    the answer fits in the token window of the model.
# 3. build_prompt() asks the model to answer in English ONLY from those
#    passages and to say "I do not know" when they are not enough.
# 4. generate() runs the model on CPU. Its time is measured apart from
#    retrieval.
#
# Models (only one is loaded per process, never both):
#   "qwen"     Qwen/Qwen2.5-0.5B-Instruct, causal LM with a chat template
#              (default)
#   "flan-t5"  google/flan-t5-base, sequence-to-sequence
#
# Choose with the WATSON_MODEL environment variable (alias or repository
# id). There is no automatic fallback: if the selected model fails, Watson
# reports the error. A Hugging Face token, only needed for private models,
# is read from HF_TOKEN, so no credentials live in the code.
# -------------------------------------------------------------------------

import gc
import os
import re
import threading
import time

from query_processing import extract_query_terms
from text_cleaner import tokenize

MODELS = {
    "qwen": {
        "repo": "Qwen/Qwen2.5-0.5B-Instruct",
        "kind": "causal",
        # Qwen accepts far more, but on CPU the cost grows with the prompt.
        "context_window": 2048,
        "max_new_tokens": 160,
        "max_chunks": 4
    },
    "flan-t5": {
        "repo": "google/flan-t5-base",
        "kind": "seq2seq",
        # Encoder input limit; the answer is produced by the decoder apart.
        "context_window": 512,
        "max_new_tokens": 96,
        "max_chunks": 3
    }
}

DEFAULT_MODEL = "qwen"

MIN_CONTEXT_CHUNKS = 3
MIN_SCORE = 0.05                # below this, a chunk is not considered evidence
MAX_OVERLAP = 0.6               # chunks more similar than this are duplicates
SAFETY_TOKENS = 16              # margin for rounding in the token counts
UNKNOWN_ANSWER = "I do not know"

SYSTEM_PROMPT = (
    "You are Dr. Watson, helping to investigate a case from the Sherlock "
    "Holmes stories. Always answer in English. Use only the numbered "
    "passages given by the user: do not use outside knowledge and do not "
    "invent names, events or details. Answer in one or two sentences. "
    "If the passages do not contain enough information to answer, reply "
    f"exactly: {UNKNOWN_ANSWER}."
)

# FLAN-T5 has no chat template, so the same rules go in a plain header.
PROMPT_HEADER = (
    "Read the passages from the Sherlock Holmes stories and answer the "
    "question in English in one complete sentence. Use only the passages. "
    f"If they do not contain the answer, reply exactly: {UNKNOWN_ANSWER}."
)


def resolve_model(name):
    """
        Accepts an alias ("qwen", "flan-t5") or a repository id from MODELS.
        Anything else is an error, never a silent fallback.
    """
    key = (name or DEFAULT_MODEL).strip()

    if key.lower() in MODELS:
        return key.lower()

    for alias, spec in MODELS.items():
        if spec["repo"].lower() == key.lower():
            return alias

    raise ValueError(
        f"Unknown WATSON_MODEL '{name}'. Use one of: "
        + ", ".join(f"{alias} ({spec['repo']})" for alias, spec in MODELS.items())
    )


_selected = os.environ.get("WATSON_MODEL", DEFAULT_MODEL)
_model = None
_tokenizer = None
_loaded_alias = None
_load_lock = threading.Lock()


def current_spec():
    return MODELS[resolve_model(_selected)]


def model_name():
    try:
        return current_spec()["repo"]
    except ValueError:
        return str(_selected)


def unload_model():
    global _model, _tokenizer, _loaded_alias

    with _load_lock:
        _model = None
        _tokenizer = None
        _loaded_alias = None
        gc.collect()


def select_model(name):
    """
        Changes the model used by Watson. The previous one is released first,
        so two models are never in memory at the same time.
    """
    global _selected

    alias = resolve_model(name)

    if alias != _loaded_alias:
        unload_model()

    _selected = alias


# -------------------------------------------------------------------------
# Model loading
# -------------------------------------------------------------------------

def load_model():
    """
        Loads the selected tokenizer and model only once per process, on CPU.
        Raises the original exception if transformers is missing or the
        download fails, so the interface can show the error and offer a retry.
    """
    global _model, _tokenizer, _loaded_alias

    alias = resolve_model(_selected)

    with _load_lock:
        if _model is None or _loaded_alias != alias:
            import torch
            from transformers import AutoTokenizer

            spec = MODELS[alias]
            token = os.environ.get("HF_TOKEN")

            _model = None
            _tokenizer = None
            gc.collect()

            if spec["kind"] == "causal":
                from transformers import AutoModelForCausalLM as ModelClass
            else:
                from transformers import AutoModelForSeq2SeqLM as ModelClass

            tokenizer = AutoTokenizer.from_pretrained(spec["repo"], token=token)

            # float32: this CPU has no native bfloat16, which would be slower.
            model = ModelClass.from_pretrained(
                spec["repo"], token=token, dtype=torch.float32
            )
            model.to("cpu")
            model.eval()

            _tokenizer = tokenizer
            _model = model
            _loaded_alias = alias

    return _tokenizer, _model


def model_is_loaded():
    try:
        return _model is not None and _loaded_alias == resolve_model(_selected)
    except ValueError:
        return False


def count_tokens(text):
    if _tokenizer is not None:
        return len(_tokenizer.encode(text, add_special_tokens=False))

    # Rough estimate used before the model is loaded.
    return int(len(text.split()) * 1.4) + 1


# -------------------------------------------------------------------------
# Context selection
# -------------------------------------------------------------------------

def split_sentences(text):
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())

    return [sentence for sentence in sentences if len(sentence) > 0]


def best_window(text, terms, token_budget):
    """
        Returns the run of consecutive sentences of the chunk that contains
        the most query terms and fits in token_budget.
    """
    sentences = split_sentences(text)

    if len(sentences) == 0:
        return ""

    hits = []

    for sentence in sentences:
        words = set(tokenize(sentence))
        hits.append(len(words & terms))

    best_start = 0
    best_end = 0
    best_hits = -1

    for start in range(len(sentences)):
        total_tokens = 0
        total_hits = 0

        for end in range(start, len(sentences)):
            total_tokens = total_tokens + count_tokens(sentences[end])

            if total_tokens > token_budget and end > start:
                break

            total_hits = total_hits + hits[end]

            if total_hits > best_hits:
                best_hits = total_hits
                best_start = start
                best_end = end

    return " ".join(sentences[best_start:best_end + 1])


def overlap(words_a, words_b):
    if len(words_a) == 0 or len(words_b) == 0:
        return 0.0

    return len(words_a & words_b) / len(words_a | words_b)


def input_budget():
    """
        Tokens the prompt may use. A causal model writes its answer in the
        same window, so the answer space is reserved; FLAN-T5's decoder has
        its own space, so only the encoder limit applies.
    """
    spec = current_spec()

    if spec["kind"] == "causal":
        return spec["context_window"] - spec["max_new_tokens"]

    return spec["context_window"]


def passage_line(position, story, excerpt):
    return f"[{position}] ({story}) {excerpt}"


def question_terms(question):
    """
        Terms of the question used to pick fragments and sentences. Same
        preprocessing as the search engines (query_processing): before, the
        raw tokens were used, so stopwords such as "what", "did" or "the"
        and the "s" of possessives counted as matches.
    """
    return set(extract_query_terms(question))


def select_context(question, results, max_chunks=None):
    """
        Chooses the fragments that will be sent to the model.

        Priority: higher score first, fragments must contain at least one
        query term, near-duplicates are skipped, and the passages are trimmed
        so that instructions + question + passages + answer space fit in the
        token window of the selected model.
    """
    if max_chunks is None:
        max_chunks = current_spec()["max_chunks"]

    terms = question_terms(question)

    candidates = []

    for result in results:
        if result["score"] < MIN_SCORE:
            continue

        matched = set(result.get("matched_terms", []))

        if len(matched) == 0:
            matched = terms & set(tokenize(result["text"]))

        if len(matched) == 0:
            continue

        candidates.append((result, matched | terms))

    chosen = []
    chosen_words = []

    for result, chunk_terms in candidates:
        words = set(tokenize(result["text"]))

        is_duplicate = False

        for previous in chosen_words:
            if overlap(words, previous) > MAX_OVERLAP:
                is_duplicate = True

        if is_duplicate:
            continue

        chosen.append((result, chunk_terms))
        chosen_words.append(words)

        if len(chosen) >= max_chunks:
            break

    if len(chosen) == 0:
        return []

    # Everything that is not a passage: instructions, question, chat
    # template markers. Measured on the real prompt with no passages.
    fixed_tokens = count_prompt_tokens(build_prompt(question, []))
    available = input_budget() - fixed_tokens - SAFETY_TOKENS

    how_many = min(len(chosen), MIN_CONTEXT_CHUNKS)
    per_chunk = max(60, available // how_many)

    context = []
    used = 0

    for position, (result, chunk_terms) in enumerate(chosen, start=1):
        label_tokens = count_tokens(passage_line(position, result["story"], "")) + 1
        budget = min(per_chunk, available - used) - label_tokens

        if budget < 40:
            break

        # The whole fragment is sent when it fits; it is trimmed to its most
        # relevant sentences only when it does not.
        excerpt = result["text"]
        tokens = count_tokens(excerpt)
        trimmed = False

        if tokens > budget:
            excerpt = best_window(result["text"], chunk_terms, budget)
            tokens = count_tokens(excerpt)
            trimmed = True

        if used + tokens + label_tokens > available:
            break

        used = used + tokens + label_tokens

        context.append({
            "chunk_id": result["chunk_id"],
            "story": result["story"],
            "score": result["score"],
            "excerpt": excerpt,
            "tokens": tokens,
            "trimmed": trimmed
        })

    # Final check on the real prompt (instructions + passages + question):
    # if rounding left it over the budget, drop passages from the end.
    while len(context) > 0 and count_prompt_tokens(build_prompt(question, context)) > input_budget():
        context.pop()

    return context


# -------------------------------------------------------------------------
# Prompt and generation
# -------------------------------------------------------------------------

def build_messages(question, context):
    passages = []

    for position, item in enumerate(context, start=1):
        passages.append(passage_line(position, item["story"], item["excerpt"]))

    if len(passages) == 0:
        passages.append("(no passages)")

    user = "Passages:\n" + "\n\n".join(passages) + f"\n\nQuestion: {question}"

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user}
    ]


def build_prompt(question, context):
    """
        Returns the exact text the model receives: the chat template applied
        to the messages for Qwen, a plain prompt for FLAN-T5.
    """
    if current_spec()["kind"] == "causal" and _tokenizer is not None:
        return _tokenizer.apply_chat_template(
            build_messages(question, context),
            tokenize=False,
            add_generation_prompt=True
        )

    if current_spec()["kind"] == "causal":
        # Before the tokenizer exists: same content, used only to estimate.
        messages = build_messages(question, context)
        return messages[0]["content"] + "\n\n" + messages[1]["content"]

    passages = []

    for position, item in enumerate(context, start=1):
        passages.append(passage_line(position, item["story"], item["excerpt"]))

    return (
        PROMPT_HEADER
        + "\n\nPassages:\n"
        + "\n".join(passages)
        + f"\n\nQuestion: {question}\nAnswer:"
    )


def count_prompt_tokens(prompt):
    if _tokenizer is not None:
        # The chat template already contains the special tokens.
        return len(_tokenizer(prompt, add_special_tokens=False)["input_ids"]) + 2

    return count_tokens(prompt) + 24


def generate(prompt):
    tokenizer, model = load_model()
    spec = current_spec()

    import torch

    if spec["kind"] == "causal":
        inputs = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
        prompt_length = inputs["input_ids"].shape[1]

        if prompt_length + spec["max_new_tokens"] > spec["context_window"]:
            raise ValueError(
                f"Prompt of {prompt_length} tokens does not leave room for the "
                f"answer in a window of {spec['context_window']}."
            )

        with torch.no_grad():
            output = model.generate(
                **inputs,
                max_new_tokens=spec["max_new_tokens"],
                do_sample=False,
                temperature=None,
                top_p=None,
                top_k=None,
                repetition_penalty=1.1,
                pad_token_id=tokenizer.eos_token_id
            )

        new_tokens = output[0][prompt_length:]

        return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()

    inputs = tokenizer(
        prompt, return_tensors="pt", truncation=True, max_length=spec["context_window"]
    )

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=spec["max_new_tokens"],
            num_beams=3,
            no_repeat_ngram_size=3,
            early_stopping=True
        )

    return tokenizer.decode(output[0], skip_special_tokens=True).strip()


def is_unknown(answer):
    cleaned = answer.lower().strip(" .!\"'")

    return len(cleaned) == 0 or cleaned.startswith(UNKNOWN_ANSWER.lower())


def answer_question(question, search_response):
    """
        Answers a question with the chunks returned by any search engine.

        Returns a dictionary with:
            status      "ok", "unknown" (model found no answer in the
                        passages), "no_context" (no chunk was relevant) or
                        "error" (the model could not run)
            answer      text of the model, or None
            passages    excerpts sent to the model
            sources     chunk_id, story and score of each excerpt
            context     full context records (with token counts)
            prompt      the exact prompt sent to the model (after the
                        chat template, for Qwen)
            model       name of the model
            generation_time_ms
            error       error message when status is "error"
    """
    try:
        resolve_model(_selected)
    except ValueError as error:
        return {
            "status": "error", "answer": None, "passages": [], "sources": [],
            "context": [], "prompt": None, "model": model_name(),
            "generation_time_ms": 0.0, "error": f"ValueError: {error}"
        }

    context = select_context(question, search_response["results"])

    reply = {
        "status": "ok",
        "answer": None,
        "passages": [item["excerpt"] for item in context],
        "sources": [
            {"chunk_id": item["chunk_id"], "story": item["story"], "score": item["score"]}
            for item in context
        ],
        "context": context,
        "prompt": None,
        "model": model_name(),
        "generation_time_ms": 0.0,
        "error": None
    }

    if len(context) == 0:
        reply["status"] = "no_context"
        return reply

    try:
        load_model()

        # The token counts are exact once the tokenizer is available.
        context = select_context(question, search_response["results"])
        reply["context"] = context
        reply["passages"] = [item["excerpt"] for item in context]
        reply["sources"] = [
            {"chunk_id": item["chunk_id"], "story": item["story"], "score": item["score"]}
            for item in context
        ]

        prompt = build_prompt(question, context)
        reply["prompt"] = prompt

        start = time.perf_counter()
        answer = generate(prompt)
        reply["generation_time_ms"] = round((time.perf_counter() - start) * 1000, 1)

    except Exception as error:
        reply["status"] = "error"
        reply["error"] = f"{type(error).__name__}: {error}"
        return reply

    if len(answer) > 0:
        answer = answer[0].upper() + answer[1:]

    reply["answer"] = answer

    if is_unknown(answer):
        reply["status"] = "unknown"

    return reply


def main():
    from approximate_search import load_collection, search_approximate

    chunks, vocabulary, document_frequency = load_collection()

    for question in ["What happened to the bell rope?",
                     "Who found the blue carbuncle?",
                     "Why did Holmes beat the pavement?"]:

        response = search_approximate(question, chunks, vocabulary, document_frequency, top_k=5)
        reply = answer_question(question, response)

        print(f"\nQ: {question}")
        print(f"   status: {reply['status']}   generation: {reply['generation_time_ms']} ms")
        print(f"   A: {reply['answer']}")

        for item in reply["context"]:
            print(f"   - {item['chunk_id']} ({item['tokens']} tokens)")


if __name__ == "__main__":
    main()
