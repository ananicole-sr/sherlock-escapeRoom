
# -------------------------------------------------------------------------
# TEMPORARY MODULE
#
# Watson's answers are generated here by simply quoting the fragments that
# the search engine recovered. There is no language model involved yet.
#
# Lepe is in charge of stage 5 (Hugging Face). When his module is ready,
# the function answer_question() should call it instead, keeping the same
# inputs and the same return value, so the interface does not change.
# -------------------------------------------------------------------------

MAX_CONTEXT_CHUNKS = 2
MAX_SENTENCES = 2
MAX_CHARACTERS = 320


def select_context(results, max_chunks=MAX_CONTEXT_CHUNKS):
    context = []

    for result in results[:max_chunks]:
        context.append(result)

    return context


def first_sentences(text, how_many=MAX_SENTENCES):
    sentences = []
    current = ""

    for character in text:
        current = current + character

        if character in ".!?":
            sentences.append(current.strip())
            current = ""

            if len(sentences) >= how_many:
                break

    if len(sentences) == 0:
        return text[:MAX_CHARACTERS]

    joined = " ".join(sentences)

    if len(joined) > MAX_CHARACTERS:
        joined = joined[:MAX_CHARACTERS].rsplit(" ", 1)[0] + "..."

    return joined


def answer_question(question, search_response):
    results = search_response["results"]

    if len(results) == 0:
        return {
            "answer": "I am afraid I found nothing in the files that speaks to "
                      "that. Try asking it another way.",
            "passages": [],
            "sources": []
        }

    best = results[0]

    if best["score"] < 0.05:
        return {
            "answer": "I searched the papers but found nothing solid enough to be "
                      "worth repeating. Holmes would tell us not to theorise ahead "
                      "of our data. Try naming an object or a person from the case.",
            "passages": [],
            "sources": []
        }

    context = select_context(results)

    passages = []
    sources = []

    for result in context:
        passages.append(first_sentences(result["text"]))
        sources.append({
            "chunk_id": result["chunk_id"],
            "story": result["story"],
            "score": result["score"]
        })

    answer = f"The files of {context[0]['story']} mention this:"

    return {
        "answer": answer,
        "passages": passages,
        "sources": sources
    }
