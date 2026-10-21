
# -------------------------------------------------------------------------
# Research Lab: technical view of retrieval and generation.
# Only real measurements are shown. Exact search (KMP / Z-function) comes
# from exact_search.py (stage 3) and is listed when that module exists.
# -------------------------------------------------------------------------

import html

import streamlit as st

from assistant import watson
from search.approximate_search import search_approximate
from ui.widgets import watson_avatar

STORIES = ["All stories", "The Speckled Band", "The Blue Carbuncle", "The Red-Headed League"]

APPROXIMATE = "Approximate · Levenshtein + Jaccard"
EXACT_KMP = "Exact · KMP"
EXACT_Z = "Exact · Z-function"


def esc(text):
    return html.escape(str(text))


def exact_engine():
    """
        Returns exact_search(query, algorithm, top_k, story) from
        exact_search.py (stage 3), or None if the module is missing.
    """
    try:
        from search import exact_search
    except ImportError:
        return None

    return getattr(exact_search, "exact_search", None)


def format_score(score):
    if isinstance(score, int):
        return str(score)

    return f"{score:.4f}"


def matched_text(matched):
    # Exact search reports {term: frequency}; approximate search, a list.
    if isinstance(matched, dict):
        return ", ".join(f"{term} ×{count}" for term, count in matched.items())

    return ", ".join(matched)


def run_search(engine, query, collection, top_k, story, method, ngram_size):
    chunks, vocabulary, document_frequency = collection

    if engine == APPROXIMATE:
        return search_approximate(
            query, chunks, vocabulary, document_frequency,
            top_k=top_k, ngram_size=ngram_size, method=method, story=story
        )

    algorithm = "kmp" if engine == EXACT_KMP else "z"

    response = exact_engine()(query, algorithm=algorithm, top_k=top_k, story=story)

    # Same names as the approximate engine, so the view below is shared.
    response.setdefault("query_terms", response.get("keywords", []))

    return response


def draw_controls(collection):
    engines = [APPROXIMATE]

    if exact_engine() is not None:
        engines = [EXACT_KMP, EXACT_Z, APPROXIMATE]

    query = st.text_input("Query", value="What happened to the bell rope?", key="lab_query")

    left, middle, right = st.columns([1.4, 1, 1])

    engine = left.radio("Search engine", engines, key="lab_engine")
    story = middle.selectbox("Collection", STORIES, key="lab_story")
    top_k = right.slider("Results", min_value=1, max_value=10, value=5, key="lab_top_k")

    method = "combined"
    ngram_size = 3

    if engine == APPROXIMATE:
        a, b = st.columns(2)
        method = a.selectbox(
            "Scoring", ["combined", "coverage", "jaccard_words", "jaccard_ngrams"],
            key="lab_method",
            help="combined = 0.6 · coverage + 0.25 · Jaccard(words) + 0.15 · Jaccard(char n-grams)"
        )
        ngram_size = b.slider("Character n-gram size", 2, 5, 3, key="lab_ngram")

    if exact_engine() is None:
        st.caption(
            "Exact search (KMP and Z-function, stage 3) is not available: "
            "exact_search.py with exact_search(query, algorithm, top_k, story) "
            "was not found."
        )

    if st.button("Run search", type="primary", key="lab_run"):
        if len(query.strip()) == 0:
            st.warning("Write a query first.")
            return

        try:
            response = run_search(
                engine, query, collection, top_k,
                None if story == STORIES[0] else story, method, ngram_size
            )
        except Exception as error:
            st.error(f"The search failed: {type(error).__name__}: {error}")
            return

        st.session_state.lab_response = response
        st.session_state.lab_reply = None


def draw_results(response):
    results = response["results"]

    a, b, c, d = st.columns(4)
    a.metric("Algorithm", response["algorithm"])
    b.metric("Retrieval time", f"{response['retrieval_time_ms']:.2f} ms")
    c.metric("Chunks examined", response.get("chunks_examined", "—"))
    d.metric("Results", len(results))

    if "chunks_recovered" in response:
        st.caption(
            f"Fragments with at least one exact match: {response['chunks_recovered']} · "
            "candidates taken from the inverted index"
        )

    if "correction_time_ms" in response:
        st.caption(
            f"Levenshtein correction: {response['correction_time_ms']:.2f} ms · "
            f"Scoring: {response.get('scoring_time_ms', 0):.2f} ms · "
            f"Method: {response.get('method', '—')}"
        )

    if response.get("query_terms"):
        corrected = response.get("corrected_terms", response["query_terms"])
        chips = []

        for original, fixed in zip(response["query_terms"], corrected):
            if original == fixed:
                chips.append(f"<span>{esc(original)}</span>")
            else:
                chips.append(f"<span class='fix'>{esc(original)} → {esc(fixed)}</span>")

        st.markdown("**Query terms**")
        st.markdown(f"<div class='chips'>{''.join(chips)}</div>", unsafe_allow_html=True)

    st.markdown("**Retrieved fragments**")

    if len(results) == 0:
        st.info("No fragment was retrieved.")
        return

    best = max(result["score"] for result in results) or 1

    for rank, result in enumerate(results, start=1):
        width = max(2, int(100 * result["score"] / best))
        matched = result.get("matched_terms", [])
        matched_html = f" · matched: {esc(matched_text(matched))}" if matched else ""

        st.markdown(
            f"<div class='result'><div class='top'><span><span class='rank'>{rank}</span>"
            f"<span class='id'>{esc(result['chunk_id'])}</span> "
            f"<span class='story'>· {esc(result['story'])}</span></span>"
            f"<span class='score'>score {format_score(result['score'])}{matched_html}</span></div>"
            f"<div class='bar' role='img' aria-label='Relative score {width}%'><i style='width:{width}%'></i></div>"
            f"<div class='excerpt'>{esc(result['text'][:280])}…</div></div>",
            unsafe_allow_html=True
        )

    with st.expander("Full table and texts"):
        columns = ["chunk_id", "story", "score", "coverage", "jaccard_words", "jaccard_ngrams"]
        rows = [{name: result.get(name) for name in columns if name in result} for result in results]
        st.dataframe(rows, use_container_width=True, hide_index=True)

        for result in results:
            st.markdown(f"**{result['chunk_id']}**")
            st.write(result["text"])


def draw_generation(response):
    st.markdown("**Watson's answer from these fragments**")
    st.caption("Generation is measured separately and never counted in the retrieval time.")

    if st.button("Generate answer", key="lab_generate"):
        with st.spinner("Selecting context and running the language model…"):
            st.session_state.lab_reply = watson.answer_question(response["query"], response)

    reply = st.session_state.lab_reply

    if reply is None:
        return

    a, b, c = st.columns(3)
    a.metric("Status", reply["status"])
    b.metric("Generation time", f"{reply['generation_time_ms']:.0f} ms")
    c.metric("Passages sent", len(reply["context"]))

    if reply["status"] == "error":
        st.error(f"The model could not run: {reply['error']}")
    elif reply["status"] == "no_context":
        st.warning("No retrieved fragment passed the minimum score, so the model was not called.")
    else:
        st.markdown(
            f"<div class='msg'>{watson_avatar()}<div class='bubble'>"
            f"<span class='who'>{esc(reply['model'])}</span>{esc(reply['answer'])}</div></div>",
            unsafe_allow_html=True
        )

    if reply["context"]:
        st.dataframe(
            [{"chunk_id": item["chunk_id"], "story": item["story"], "score": item["score"],
              "tokens": item["tokens"]} for item in reply["context"]],
            use_container_width=True, hide_index=True
        )

    if reply["prompt"]:
        with st.expander("Prompt sent to the model"):
            st.code(reply["prompt"], language=None, wrap_lines=True)


def draw_research_lab(collection):
    st.markdown(
        "<div class='lab-head'><h1>Research Lab</h1>"
        "<p>How Watson finds his evidence: the search algorithms, their scores and times, "
        "and the answer the language model builds from them.</p></div>",
        unsafe_allow_html=True
    )

    controls, output = st.columns([1, 1.45], gap="large")

    with controls:
        draw_controls(collection)

    with output:
        response = st.session_state.lab_response

        if response is None:
            st.info("Run a search to see the retrieved fragments, their scores and the times.")
            return

        st.markdown(f"Query: **{esc(response['query'])}**")
        draw_results(response)
        st.divider()
        draw_generation(response)
