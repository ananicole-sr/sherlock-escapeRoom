
# -------------------------------------------------------------------------
# Investigation screen: case header, progress between case files, the
# interactive scene, Watson, the evidence notebook and the deduction.
# -------------------------------------------------------------------------

import html

import streamlit as st

import watson
from approximate_search import search_approximate
from autocomplete import suggest, last_word
from ui import state
from ui.state import ROMAN
from ui.widgets import scene_view, ask_box, watson_avatar

CHAT_LOG_KEY = "chat_log"
STARTER_LIMIT = 3


def esc(text):
    return html.escape(str(text))


# -------------------------------------------------------------------------
# Header and progress
# -------------------------------------------------------------------------

def draw_case_header(case, cases):
    position = cases.index(case)

    head, tracker = st.columns([1.25, 1], vertical_alignment="bottom", gap="large")

    with head:
        st.markdown(
            f"<div class='case-head'>"
            f"<div class='kicker'>Case file {ROMAN[position]} of {ROMAN[len(cases) - 1]}"
            f" &middot; {esc(case['story'])}</div>"
            f"<h1>{esc(case['title'])}</h1>"
            f"<p class='objective'><b>Objective:</b> {esc(case['objective'])}</p>"
            f"</div>",
            unsafe_allow_html=True
        )

    with tracker:
        draw_tracker(case, cases)


def draw_tracker(case, cases):
    with st.container(key="tracker"):
        columns = st.columns(len(cases) + (1 if state.all_solved(cases) else 0))

        for position, other in enumerate(cases):
            unlocked = state.is_unlocked(position)
            solved = state.is_solved(other)

            if not unlocked:
                label = f"{ROMAN[position]} · Locked"
                help_text = "Solve the previous case file to unlock it."
            elif solved:
                label = f"✓ {ROMAN[position]} · {other['title']}"
                help_text = "Solved. You can reopen it at any time."
            else:
                label = f"{ROMAN[position]} · {other['title']}"
                help_text = "Open case file."

            clicked = columns[position].button(
                label,
                key=f"track_{other['id']}",
                type="primary" if other["id"] == case["id"] else "secondary",
                disabled=not unlocked,
                help=help_text,
                use_container_width=True
            )

            if clicked and other["id"] != case["id"]:
                state.open_case(position)
                st.rerun()

        if state.all_solved(cases):
            if columns[-1].button("✦ Conclusion", key="track_finale", use_container_width=True):
                st.session_state.view = "finale"
                st.rerun()


# -------------------------------------------------------------------------
# Scene
# -------------------------------------------------------------------------

def handle_scene_event(case, key):
    event = state.take_event(key)

    if event is None:
        return

    valid_ids = [hotspot["id"] for hotspot in case["hotspots"]]

    if event.get("id") not in valid_ids:
        return

    if event["type"] == "inspect":
        state.mark_inspected(case["id"], event["id"])

    elif event["type"] == "record":
        hotspot = next(h for h in case["hotspots"] if h["id"] == event["id"])

        if hotspot["note"]:
            state.record(case["id"], event["id"])


def draw_scene(case, cases):
    key = f"scene_{case['id']}"

    handle_scene_event(case, key)

    position = cases.index(case)

    scene_view(
        case,
        label=f"Case {ROMAN[position]}",
        inspected=state.inspected_in(case["id"]),
        recorded=state.recorded_in(case["id"]),
        key=key
    )


def draw_deduction_bar(case, cases):
    with st.container(key="deduce"):
        recorded = len(state.recorded_in(case["id"]))

        if state.is_solved(case):
            title = "Case closed"
            body = "You presented the right deduction. Review it or move on."
            label = "Review deduction"
        else:
            title = "Present your deduction"
            body = (f"{recorded} observation{'s' if recorded != 1 else ''} in your notebook. "
                    "When the evidence points one way, name it.")
            label = "Present your deduction"

        st.markdown(
            f"<div class='deduce-copy'><div class='title'>{title}</div>"
            f"<div class='body'>{body}</div></div>",
            unsafe_allow_html=True
        )

        if st.button(label, key=f"deduce_{case['id']}", type="primary",
                     use_container_width=True):
            deduction_dialog(case, cases)


@st.dialog("Present your deduction", width="large")
def deduction_dialog(case, cases):
    st.markdown(
        f"<div class='parchment'><span class='kicker'>{esc(case['title'])} &middot; "
        f"the riddle</span>{esc(case['riddle']).replace(chr(10), '<br>')}</div>",
        unsafe_allow_html=True
    )

    position = cases.index(case)
    result_key = f"verdict_{case['id']}"

    if not state.is_solved(case):
        with st.form(key=f"deduction_form_{case['id']}", border=False):
            answer = st.text_input(
                "Your deduction",
                placeholder="One or two words, e.g. the object, creature or place",
                key=f"answer_{case['id']}"
            )
            submitted = st.form_submit_button("Submit deduction", type="primary")

        if submitted:
            state.count_attempt(case)

            if state.check_answer(case, answer):
                state.solve(case, cases)
                st.session_state[result_key] = "correct"
                st.rerun(scope="fragment")
            else:
                st.session_state[result_key] = "wrong" if answer.strip() else "empty"

    verdict = st.session_state.get(result_key)

    if state.is_solved(case):
        st.markdown(
            f"<div class='verdict ok'><b>Correct, the evidence agrees.</b>"
            f"{esc(case['solution_note'])}</div>",
            unsafe_allow_html=True
        )

        left, right = st.columns(2)

        if position + 1 < len(cases):
            if left.button(f"Open case file {ROMAN[position + 1]}", type="primary",
                           use_container_width=True, key="dialog_next"):
                st.session_state[result_key] = None
                state.open_case(position + 1)
                st.rerun()
        else:
            if left.button("Read the conclusion", type="primary",
                           use_container_width=True, key="dialog_finale"):
                st.session_state[result_key] = None
                st.session_state.view = "finale"
                st.rerun()

        if right.button("Stay in this scene", use_container_width=True, key="dialog_stay"):
            st.session_state[result_key] = None
            st.rerun()

    elif verdict == "wrong":
        attempts = st.session_state.attempts.get(case["id"], 0)
        st.markdown(
            "<div class='verdict bad'><b>That is not what the evidence says.</b>"
            "Nothing is lost: your notebook and your conversation with Watson are "
            "still there. Look again at what you recorded, or ask Watson about it."
            f"<br><span style='color:var(--text-3);font-size:12.5px'>Attempts: {attempts}</span></div>",
            unsafe_allow_html=True
        )

        if st.button("Back to the scene", key="dialog_back"):
            st.session_state[result_key] = None
            st.rerun()

    elif verdict == "empty":
        st.caption("Write your deduction before submitting.")


# -------------------------------------------------------------------------
# Watson
# -------------------------------------------------------------------------

def watson_message(text, meta=None):
    meta_html = f"<span class='meta'>{meta}</span>" if meta else ""

    st.markdown(
        f"<div class='msg'>{watson_avatar()}"
        f"<div class='bubble'><span class='who'>Dr. Watson</span>{esc(text)}{meta_html}</div></div>",
        unsafe_allow_html=True
    )


def player_message(text):
    st.markdown(
        f"<div class='msg you'><div class='bubble'><span class='who'>You</span>{esc(text)}</div></div>",
        unsafe_allow_html=True
    )


def notice(text, error=False):
    st.markdown(
        f"<div class='notice{' error' if error else ''}'>{text}</div>",
        unsafe_allow_html=True
    )


def working(slot, text):
    slot.markdown(
        f"<div class='working' role='status'><span class='dots' aria-hidden='true'>"
        f"<span></span><span></span><span></span></span>{esc(text)}</div>",
        unsafe_allow_html=True
    )


def draw_passages(entry):
    if len(entry["context"]) == 0:
        return

    with st.expander(f"Passages Watson read ({len(entry['context'])})"):
        for item in entry["context"]:
            st.markdown(
                f"<div class='passage'><span class='src'>{esc(item['story'])} · "
                f"{esc(item['chunk_id'])} · score {item['score']:.3f}</span>"
                f"{esc(item['excerpt'])}</div>",
                unsafe_allow_html=True
            )


def corrections_text(entry):
    if not entry.get("corrections"):
        return ""

    pairs = [f"“{esc(typed)}” as “{esc(fixed)}”" for typed, fixed, distance in entry["corrections"]]

    return " · read " + ", ".join(pairs)


def draw_entry(case, index, entry, collection):
    player_message(entry["question"])

    stories = sorted({item["story"] for item in entry["context"]})
    source = f"From {esc(', '.join(stories))}" if stories else ""

    if entry["status"] == "ok":
        watson_message(entry["answer"], source + corrections_text(entry))
        draw_passages(entry)

    elif entry["status"] == "unknown":
        watson_message(entry["answer"], source + corrections_text(entry))
        notice("The passages that were found do not answer this. "
               "Try naming an object, a person or a place from the case.")
        draw_passages(entry)

    elif entry["status"] == "no_context":
        notice("No passage in the case files matched this question"
               f"{corrections_text(entry)}. Try naming an object, a person or a place.")

    else:
        notice(
            "<b>Watson could not answer.</b> "
            + esc(entry.get("error_hint") or "The language model is not available right now.")
            + f"<details><summary>Technical details</summary><code>{esc(entry['error'])}</code></details>",
            error=True
        )
        draw_passages(entry)

        if st.button("Try again", key=f"retry_{case['id']}_{index}"):
            slot = st.empty()
            history = st.session_state.chat_history[case["id"]]
            history[index] = ask_watson(entry["question"], case, collection, slot)
            st.session_state.ask_clear += 1
            st.rerun(scope="fragment")


def ask_watson(question, case, collection, slot):
    """
        Runs the real pipeline: approximate search over the case story, then
        context selection and generation with the Hugging Face model. Times
        are measured separately.
    """
    chunks, vocabulary, document_frequency = collection

    working(slot, "Searching the case files…")

    entry = {
        "question": question,
        "status": "error",
        "answer": None,
        "context": [],
        "corrections": [],
        "retrieval_time_ms": None,
        "generation_time_ms": None,
        "error": None,
        "error_hint": None
    }

    try:
        response = search_approximate(
            question, chunks, vocabulary, document_frequency,
            top_k=5, story=case["story"]
        )
    except Exception as error:
        entry["error"] = f"{type(error).__name__}: {error}"
        entry["error_hint"] = "The search over the documents failed."
        return entry

    entry["retrieval_time_ms"] = response["retrieval_time_ms"]
    entry["corrections"] = response["corrections"]

    if watson.model_is_loaded():
        working(slot, "Watson is reading the passages…")
    else:
        working(slot, "Waking Watson up: loading the language model (only the first time)…")

    reply = watson.answer_question(question, response)

    entry["status"] = reply["status"]
    entry["answer"] = reply["answer"]
    entry["context"] = reply["context"]
    entry["generation_time_ms"] = reply["generation_time_ms"]
    entry["error"] = reply["error"]

    if reply["status"] == "error":
        entry["error_hint"] = (
            f"The language model ({reply['model']}) could not run. Check the internet "
            "connection for the first download and that transformers and torch are "
            "installed, then try again. Your progress is safe."
        )

    return entry


@st.fragment
def watson_panel(case, collection):
    case_id = case["id"]
    ask_key = f"ask_{case_id}"
    history = st.session_state.chat_history.setdefault(case_id, [])

    event = state.take_event(ask_key)
    question = None

    remembered = st.session_state.ask_suggestions.get(case_id, {"prefix": "", "words": []})

    if event is not None:
        if event["type"] == "typing":
            prefix = last_word(event["text"]).lower()
            prefix = "".join(c for c in prefix if c.isalnum())
            remembered = {"prefix": prefix, "words": suggest(prefix, limit=5)}
            st.session_state.ask_suggestions[case_id] = remembered

        elif event["type"] == "submit" and event["text"].strip():
            question = event["text"].strip()[:300]
            remembered = {"prefix": "", "words": []}
            st.session_state.ask_suggestions[case_id] = remembered

    # Short enough that the deduction card below still fits on screen.
    log = st.container(height=260, key=CHAT_LOG_KEY, border=False)
    ask_area = st.container()

    with ask_area:
        starters = case["suggested_questions"][:STARTER_LIMIT] if len(history) < 2 else []

        ask_box(
            key=ask_key,
            prefix=remembered["prefix"],
            suggestions=remembered["words"],
            starters=starters,
            clear_token=st.session_state.ask_clear,
            scroll_token=len(history) * 2 + (1 if question else 0),
            log_key=CHAT_LOG_KEY,
            placeholder="Ask Watson about the case…"
        )

    with log:
        watson_message(case["watson_greeting"])

        for index, entry in enumerate(history):
            draw_entry(case, index, entry, collection)

        if question:
            player_message(question)
            slot = st.empty()
            history.append(ask_watson(question, case, collection, slot))
            st.session_state.ask_clear += 1
            st.rerun(scope="fragment")


# -------------------------------------------------------------------------
# Notebook
# -------------------------------------------------------------------------

def notebook_entry(case, hotspot, recorded):
    quote = ""

    if hotspot["quote"]:
        quote = (f"<blockquote>“{esc(hotspot['quote'])}”<br>"
                 f"<small>— {esc(case['story'])}</small></blockquote>")

    status = ("<span class='tag ok'>Recorded</span>" if recorded
              else "<span class='tag'>Inspected · not recorded</span>")

    return (
        f"<details class='nb-entry{'' if recorded else ' pending'}'>"
        f"<summary><span class='name'>{esc(hotspot['name'])}</span>"
        f"<span class='note'>{esc(hotspot['note'])}</span>"
        f"<span class='tags'><span class='tag'>{esc(case['title'])}</span>{status}</span>"
        f"</summary>"
        f"<div class='more'>{esc(hotspot['observation'])}{quote}</div>"
        f"</details>"
    )


def draw_notebook(case, cases):
    ordered = [case] + [other for other in cases if other["id"] != case["id"]]
    shown_any = False

    for other in ordered:
        position = cases.index(other)

        if not state.is_unlocked(position):
            continue

        inspected = state.inspected_in(other["id"])
        recorded = state.recorded_in(other["id"])
        with_notes = [h for h in other["hotspots"] if h["note"]]

        st.markdown(
            f"<div class='nb-head'><span class='t'>{ROMAN[position]} · {esc(other['title'])}</span>"
            f"<span class='c'>{len(recorded)} recorded · "
            f"{len(inspected)}/{len(other['hotspots'])} inspected</span></div>",
            unsafe_allow_html=True
        )

        entries = []

        for hotspot_id in recorded:
            hotspot = next(h for h in other["hotspots"] if h["id"] == hotspot_id)
            entries.append(notebook_entry(other, hotspot, True))

        for hotspot in with_notes:
            if hotspot["id"] in inspected and hotspot["id"] not in recorded:
                entries.append(notebook_entry(other, hotspot, False))

        if entries:
            shown_any = True
            st.markdown("".join(entries), unsafe_allow_html=True)
        else:
            st.markdown(
                "<div class='nb-empty'>Nothing yet. Click the glowing marks in the scene "
                "and record what matters.</div>",
                unsafe_allow_html=True
            )

    if shown_any:
        st.caption("Open an entry to read the full observation and the line from the story.")


# -------------------------------------------------------------------------
# Screen
# -------------------------------------------------------------------------

def draw_investigation(cases, collection):
    case = cases[st.session_state.current_case]

    draw_case_header(case, cases)

    # Scene on the left; Watson, the notebook and the deduction on the
    # right. On phones the columns stack in that same order.
    scene_column, side_column = st.columns([65, 35], gap="medium")

    with scene_column:
        draw_scene(case, cases)

    with side_column:
        with st.container(key="panel"):
            watson_tab, notebook_tab = st.tabs(["Dr. Watson", "Evidence notebook"])

            with watson_tab:
                watson_panel(case, collection)

            with notebook_tab:
                draw_notebook(case, cases)

        draw_deduction_bar(case, cases)
