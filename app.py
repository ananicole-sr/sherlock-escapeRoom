
import json
from pathlib import Path

import streamlit as st

from approximate_search import load_collection, search_approximate
from autocomplete import suggest, last_word, replace_last_word
from watson import answer_question

BASE_DIR = Path(__file__).resolve().parent
CASES_FILE = BASE_DIR / "data" / "cases.json"

st.set_page_config(
    page_title="Sherlock Holmes - The Final Case",
    page_icon="🔍",
    layout="wide"
)

CUSTOM_STYLE = """
<style>

/* =====================================================================
   Apple Human Interface Guidelines
   - Typography: SF Pro type scale (Large Title 34 / Title 1 28 /
     Title 2 22 / Headline 17 semibold / Body 17 / Footnote 13)
   - Layout: 8 pt spacing grid, 44 pt minimum hit targets
   - Color: dark mode semantic system colors
   - Motion: 0.25 s ease-out, subtle
   ===================================================================== */

:root {
    /* Backgrounds (dark mode) */
    --system-background: #000000;
    --secondary-background: #1C1C1E;
    --tertiary-background: #2C2C2E;
    --grouped-background: #1C1C1E;

    /* Labels */
    --label: rgba(255, 255, 255, 1.00);
    --secondary-label: rgba(235, 235, 245, 0.60);
    --tertiary-label: rgba(235, 235, 245, 0.30);

    /* Separators */
    --separator: rgba(84, 84, 88, 0.65);
    --opaque-separator: #38383A;

    /* Accent and system colors */
    --accent: #FF9F0A;          /* systemOrange, dark */
    --accent-pressed: #FFB340;
    --system-blue: #0A84FF;
    --system-green: #30D158;
    --system-red: #FF453A;
    --system-brown: #AC8E68;

    /* Shape */
    --radius-large: 16px;
    --radius-medium: 12px;
    --radius-small: 10px;

    /* Spacing: 8 pt grid */
    --space-1: 8px;
    --space-2: 16px;
    --space-3: 24px;
    --space-4: 32px;
}

/* ---------- typography ---------- */

html, body, [class*="css"], .stApp {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
                 "Helvetica Neue", "Segoe UI", Roboto, sans-serif;
    -webkit-font-smoothing: antialiased;
    font-size: 17px;
    line-height: 1.47;
    letter-spacing: -0.022em;
}

.stApp {
    background-color: var(--system-background);
    color: var(--label);
}

/* Large Title */
h1 {
    font-size: 34px !important;
    line-height: 41px !important;
    font-weight: 700 !important;
    letter-spacing: 0.374px !important;
    color: var(--label) !important;
    margin-bottom: var(--space-1) !important;
    padding-bottom: 0 !important;
    border: none !important;
}

/* Title 2 */
h2 {
    font-size: 22px !important;
    line-height: 28px !important;
    font-weight: 700 !important;
    letter-spacing: 0.35px !important;
    color: var(--label) !important;
}

/* Title 3 */
h3 {
    font-size: 20px !important;
    line-height: 25px !important;
    font-weight: 600 !important;
    letter-spacing: 0.38px !important;
    color: var(--label) !important;
    margin-top: var(--space-3) !important;
    margin-bottom: var(--space-2) !important;
}

header[data-testid="stHeader"] {
    background: transparent;
}

/* ---------- sidebar ---------- */

section[data-testid="stSidebar"] {
    background-color: var(--secondary-background);
    border-right: 0.5px solid var(--separator);
}

section[data-testid="stSidebar"] h1 {
    font-size: 22px !important;
    line-height: 28px !important;
}

/* Footnote, as used for iOS grouped-list section headers */
section[data-testid="stSidebar"] h3 {
    font-size: 13px !important;
    line-height: 18px !important;
    font-weight: 600 !important;
    letter-spacing: -0.08px !important;
    text-transform: uppercase;
    color: var(--secondary-label) !important;
    margin-top: var(--space-3) !important;
    margin-bottom: var(--space-1) !important;
}

section[data-testid="stSidebar"] p {
    font-size: 15px;
    color: var(--secondary-label);
}

section[data-testid="stSidebar"] hr {
    border-color: var(--separator);
    margin: var(--space-2) 0;
}

/* ---------- controls: 44 pt minimum hit target ---------- */

.stTextInput input {
    background-color: var(--tertiary-background) !important;
    color: var(--label) !important;
    border: none !important;
    border-radius: var(--radius-small) !important;
    min-height: 44px;
    padding: 11px 16px !important;
    font-size: 17px !important;
    letter-spacing: -0.022em;
    transition: box-shadow 0.25s ease-out;
}

.stTextInput input::placeholder {
    color: var(--tertiary-label) !important;
}

.stTextInput input:focus {
    box-shadow: 0 0 0 4px rgba(255, 159, 10, 0.35) !important;
    outline: none !important;
}

.stButton button {
    background-color: var(--tertiary-background);
    color: var(--accent) !important;
    border: none;
    border-radius: var(--radius-small);
    min-height: 44px;
    padding: 11px 20px;
    font-size: 17px;
    font-weight: 600;
    letter-spacing: -0.022em;
    transition: background-color 0.25s ease-out, transform 0.1s ease-out;
}

.stButton button:hover {
    background-color: #3A3A3C;
    color: var(--accent-pressed) !important;
}

.stButton button:active {
    transform: scale(0.97);
}

.stButton button:focus-visible {
    box-shadow: 0 0 0 4px rgba(255, 159, 10, 0.35);
}

/* ---------- tabs: segmented control ---------- */

[role="tablist"] {
    background-color: var(--secondary-background);
    border-radius: var(--radius-small);
    padding: 2px;
    gap: 2px;
    width: fit-content;
    border: none !important;
}

[data-testid="stTab"] {
    background-color: transparent;
    border-radius: 8px;
    padding: 6px 16px;
    min-height: 36px;
    display: flex;
    align-items: center;
    transition: background-color 0.25s ease-out;
    border: none !important;
}

[data-testid="stTab"] p {
    font-size: 15px !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
    color: var(--secondary-label) !important;
    margin: 0 !important;
}

[data-testid="stTab"]:hover {
    background-color: rgba(120, 120, 128, 0.20);
}

[data-testid="stTab"][aria-selected="true"] {
    background-color: #48484A;
}

[data-testid="stTab"][aria-selected="true"] p {
    color: var(--label) !important;
}

.react-aria-SelectionIndicator {
    display: none !important;
    background: transparent !important;
    height: 0 !important;
}

.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ---------- grouped content cards ---------- */

.case-card {
    background-color: var(--grouped-background);
    border-radius: var(--radius-large);
    padding: var(--space-3);
    margin-bottom: var(--space-2);
    font-size: 17px;
    line-height: 1.47;
    color: var(--label);
}

.objective-card {
    background-color: rgba(10, 132, 255, 0.14);
    border-radius: var(--radius-medium);
    padding: var(--space-2);
    margin-bottom: var(--space-3);
    font-size: 15px;
    line-height: 20px;
    color: #9CCAFF;
}

.clue-card {
    background-color: var(--grouped-background);
    border-left: 3px solid var(--accent);
    border-radius: var(--radius-medium);
    padding: var(--space-2);
    margin-bottom: var(--space-1);
    font-size: 15px;
    line-height: 21px;
    color: var(--label);
}

.player-card {
    background-color: var(--accent);
    color: #1C1C1E;
    border-radius: 18px 18px 4px 18px;
    padding: 10px 16px;
    margin: 0 0 var(--space-1) 25%;
    font-size: 16px;
    line-height: 21px;
    font-weight: 500;
}

.watson-card {
    background-color: var(--tertiary-background);
    border-radius: 18px 18px 18px 4px;
    padding: 10px 16px;
    margin: 0 25% var(--space-1) 0;
    font-size: 16px;
    line-height: 21px;
    color: var(--label);
}

.quote-card {
    background-color: var(--secondary-background);
    border-left: 2px solid var(--separator);
    border-radius: 4px var(--radius-small) var(--radius-small) 4px;
    padding: 12px 16px;
    margin: 0 20% var(--space-1) var(--space-2);
    font-family: ui-serif, "New York", Georgia, serif;
    font-size: 15px;
    line-height: 22px;
    color: var(--secondary-label);
}

.riddle-card {
    background-color: var(--grouped-background);
    border-radius: var(--radius-large);
    padding: var(--space-4);
    font-family: ui-serif, "New York", Georgia, serif;
    font-size: 20px;
    line-height: 32px;
    color: var(--label);
    white-space: pre-wrap;
    text-align: center;
}

.case-subtitle {
    font-size: 15px;
    line-height: 20px;
    color: var(--secondary-label);
    margin-top: -4px;
    margin-bottom: var(--space-3);
}

.locked-note {
    font-size: 15px;
    color: var(--tertiary-label);
}

/* ---------- captions as Footnote ---------- */

[data-testid="stCaptionContainer"] p {
    font-size: 13px !important;
    line-height: 18px !important;
    color: rgba(235, 235, 245, 0.55) !important;
    letter-spacing: -0.08px;
}

/* ---------- alerts ---------- */

[data-testid="stAlert"] {
    border-radius: var(--radius-medium);
    border: none;
    font-size: 15px;
}

/* ---------- dividers ---------- */

hr {
    border-color: var(--separator);
    margin: var(--space-3) 0;
}

</style>
"""

st.markdown(CUSTOM_STYLE, unsafe_allow_html=True)


@st.cache_resource
def get_collection():
    return load_collection()


@st.cache_resource
def get_cases():
    with open(CASES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def start_session():
    if "current_case" not in st.session_state:
        st.session_state.current_case = 0

    if "unlocked" not in st.session_state:
        st.session_state.unlocked = 1

    if "solved" not in st.session_state:
        st.session_state.solved = []

    if "discovered_clues" not in st.session_state:
        st.session_state.discovered_clues = {}

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}

    if "pending_question" not in st.session_state:
        st.session_state.pending_question = ""

    if "question_version" not in st.session_state:
        st.session_state.question_version = 0

    if "feedback" not in st.session_state:
        st.session_state.feedback = ""


def clues_found(case_id):
    return st.session_state.discovered_clues.get(case_id, 0)


def history_for(case_id):
    return st.session_state.chat_history.get(case_id, [])


def normalize_answer(text):
    text = text.lower().strip()

    cleaned = ""

    for character in text:
        if character.isalnum() or character == " ":
            cleaned = cleaned + character

    return " ".join(cleaned.split())


def check_answer(case, typed_answer):
    typed = normalize_answer(typed_answer)

    if len(typed) == 0:
        return False

    for accepted in case["accepted_answers"]:
        if typed == normalize_answer(accepted):
            return True

    return False


def draw_sidebar(cases):
    st.sidebar.title("The Final Case")
    st.sidebar.markdown("Sherlock Holmes has disappeared.")
    st.sidebar.markdown("---")

    st.sidebar.subheader("Case files")

    for position, case in enumerate(cases):

        if position < st.session_state.unlocked:

            if case["id"] in st.session_state.solved:
                label = f"{position + 1}. {case['title']}  [solved]"
            else:
                label = f"{position + 1}. {case['title']}"

            if st.sidebar.button(label, key=f"nav_{case['id']}"):
                st.session_state.current_case = position
                st.session_state.feedback = ""
                st.rerun()

        else:
            st.sidebar.markdown(
                f"<span class='locked-note'>{position + 1}. Locked</span>",
                unsafe_allow_html=True
            )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"Cases solved: **{len(st.session_state.solved)} / {len(cases)}**"
    )


def draw_clues(case):
    st.subheader("Evidence")

    found = clues_found(case["id"])

    if found == 0:
        st.markdown(
            "<span class='locked-note'>No evidence collected yet. "
            "Ask Watson about the case to uncover it.</span>",
            unsafe_allow_html=True
        )

    for position in range(found):
        st.markdown(
            f"<div class='clue-card'>{case['clues'][position]}</div>",
            unsafe_allow_html=True
        )

    if found < len(case["clues"]):
        if st.button("Examine the scene for more evidence", key=f"clue_{case['id']}"):
            st.session_state.discovered_clues[case["id"]] = found + 1
            st.rerun()


def draw_watson(case, chunks, vocabulary, document_frequency):
    st.subheader("Dr. Watson")

    for entry in history_for(case["id"]):

        st.markdown(
            f"<div class='player-card'><b>You:</b> {entry['question']}</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<div class='watson-card'><b>Watson:</b> {entry['answer']}</div>",
            unsafe_allow_html=True
        )

        for passage in entry.get("passages", []):
            st.markdown(
                f"<div class='quote-card'>{passage}</div>",
                unsafe_allow_html=True
            )

        if len(entry["sources"]) > 0:
            source_labels = []

            for source in entry["sources"]:
                source_labels.append(f"{source['chunk_id']} ({source['score']:.3f})")

            st.caption("Fragments used: " + ", ".join(source_labels))

    st.markdown("**Ask Watson about the case**")

    question_key = f"question_{st.session_state.question_version}"

    question = st.text_input(
        "Your question",
        value=st.session_state.pending_question,
        key=question_key,
        label_visibility="collapsed"
    )

    prefix = last_word(question)
    suggestions = suggest(prefix, limit=5)

    if len(suggestions) > 0:
        st.caption("Suggestions from the vocabulary (Trie autocomplete)")

        columns = st.columns(len(suggestions))

        for position, word in enumerate(suggestions):
            if columns[position].button(word, key=f"sug_{case['id']}_{word}"):
                st.session_state.pending_question = replace_last_word(question, word)
                st.session_state.question_version = st.session_state.question_version + 1
                st.rerun()

    left, right = st.columns([1, 3])

    if left.button("Ask", key=f"ask_{case['id']}"):

        if len(question.strip()) > 0:

            response = search_approximate(
                question, chunks, vocabulary, document_frequency,
                top_k=5, story=case["story"]
            )

            watson_reply = answer_question(question, response)

            history = history_for(case["id"])

            history.append({
                "question": question,
                "answer": watson_reply["answer"],
                "passages": watson_reply["passages"],
                "sources": watson_reply["sources"],
                "retrieval_time_ms": response["retrieval_time_ms"],
                "corrections": response["corrections"]
            })

            st.session_state.chat_history[case["id"]] = history

            st.session_state.pending_question = ""
            st.session_state.question_version = st.session_state.question_version + 1

            st.rerun()

    right.caption("Suggested: " + "  |  ".join(case["suggested_questions"][:2]))


def draw_riddle(case, cases):
    st.subheader("The riddle")

    st.markdown(
        f"<div class='riddle-card'>{case['riddle']}</div>",
        unsafe_allow_html=True
    )

    answer = st.text_input("Your answer", key=f"answer_{case['id']}")

    if st.button("Submit answer", key=f"submit_{case['id']}"):

        if check_answer(case, answer):

            if case["id"] not in st.session_state.solved:
                st.session_state.solved.append(case["id"])

            position = cases.index(case)

            if position + 1 >= st.session_state.unlocked:
                st.session_state.unlocked = min(position + 2, len(cases))

            st.session_state.feedback = "correct"

        else:
            st.session_state.feedback = "wrong"

        st.rerun()

    if st.session_state.feedback == "correct" or case["id"] in st.session_state.solved:
        st.success("Correct. " + case["solution_note"])

        position = cases.index(case)

        if position + 1 < len(cases):
            if st.button("Open the next case file", key=f"next_{case['id']}"):
                st.session_state.current_case = position + 1
                st.session_state.feedback = ""
                st.rerun()
        else:
            st.balloons()
            st.markdown("### All three cases are solved. Holmes can be found.")

    elif st.session_state.feedback == "wrong":
        st.error("That is not what the evidence says. Read the files again.")


def draw_escape_room(cases, chunks, vocabulary, document_frequency):
    case = cases[st.session_state.current_case]

    st.title(case["title"])
    st.markdown(
        f"<div class='case-subtitle'>Based on {case['story']}</div>",
        unsafe_allow_html=True
    )

    image_path = BASE_DIR / case["image"]

    if image_path.exists():
        st.image(str(image_path), use_container_width=True)

    st.markdown(
        f"<div class='case-card'>{case['intro']}</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<div class='objective-card'><b>Objective:</b> {case['objective']}</div>",
        unsafe_allow_html=True
    )

    left_column, right_column = st.columns([1, 1])

    with left_column:
        draw_clues(case)

    with right_column:
        draw_watson(case, chunks, vocabulary, document_frequency)

    st.markdown("---")

    draw_riddle(case, cases)


def draw_research_lab(chunks, vocabulary, document_frequency):
    st.title("Research Lab")
    st.caption(
        "Technical view of the retrieval system. "
        "The exact search (KMP and Z-function) and the language model "
        "will be connected here by the rest of the team."
    )

    query = st.text_input("Query", value="What happened to the bell rope?")

    left, middle, right = st.columns(3)

    method = left.selectbox(
        "Scoring method",
        ["combined", "coverage", "jaccard_words", "jaccard_ngrams"]
    )

    top_k = middle.slider("Results", min_value=1, max_value=10, value=5)
    ngram_size = right.slider("Character n-gram size", min_value=2, max_value=5, value=3)

    if st.button("Run approximate search"):

        response = search_approximate(
            query, chunks, vocabulary, document_frequency,
            top_k=top_k, ngram_size=ngram_size, method=method
        )

        column_a, column_b, column_c = st.columns(3)

        column_a.metric("Retrieval time", f"{response['retrieval_time_ms']} ms")
        column_b.metric("Correction time", f"{response['correction_time_ms']} ms")
        column_c.metric("Chunks examined", response["chunks_examined"])

        st.markdown("**Query processing**")

        st.markdown(
            "Extracted terms: `" + "`  `".join(response["query_terms"]) + "`"
        )

        st.markdown(
            "Corrected terms: `" + "`  `".join(response["corrected_terms"]) + "`"
        )

        if len(response["corrections"]) > 0:
            st.markdown("**Levenshtein corrections**")

            correction_rows = []

            for original, corrected, distance in response["corrections"]:
                correction_rows.append({
                    "typed": original,
                    "corrected to": corrected,
                    "edit distance": distance
                })

            st.table(correction_rows)

        st.markdown("**Retrieved fragments**")

        result_rows = []

        for result in response["results"]:
            result_rows.append({
                "chunk_id": result["chunk_id"],
                "story": result["story"],
                "score": result["score"],
                "coverage": result["coverage"],
                "jaccard_words": result["jaccard_words"],
                "jaccard_ngrams": result["jaccard_ngrams"],
                "matched terms": ", ".join(result["matched_terms"])
            })

        st.dataframe(result_rows, use_container_width=True)

        for result in response["results"]:
            with st.expander(f"{result['chunk_id']} - score {result['score']:.4f}"):
                st.write(result["text"])


def main():
    start_session()

    cases = get_cases()
    chunks, vocabulary, document_frequency = get_collection()

    draw_sidebar(cases)

    escape_tab, lab_tab = st.tabs(["Escape Room", "Research Lab"])

    with escape_tab:
        draw_escape_room(cases, chunks, vocabulary, document_frequency)

    with lab_tab:
        draw_research_lab(chunks, vocabulary, document_frequency)


if __name__ == "__main__":
    main()
