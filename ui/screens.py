
# -------------------------------------------------------------------------
# Title screen and conclusion.
# -------------------------------------------------------------------------

import html

import streamlit as st

from ui import state
from ui.state import ROMAN
from ui.widgets import static_url, TITLE_IMAGE, FINALE_IMAGE


def esc(text):
    return html.escape(str(text))


def draw_intro(cases):
    background = static_url(TITLE_IMAGE)

    st.html(
        f"<style>.st-key-hero {{ background-image: "
        f"linear-gradient(90deg, rgba(8,11,16,.95) 0%, rgba(8,11,16,.8) 40%, rgba(8,11,16,.12) 78%),"
        f"linear-gradient(0deg, rgba(8,11,16,.9), transparent 40%),"
        f"url('{background}'); }}</style>"
    )

    with st.container(key="hero"):
        st.markdown(
            "<div class='hero-copy'>"
            "<div class='kicker'>A Sherlock Holmes investigation</div>"
            "<h1>The Final <em>Case</em></h1>"
            "<p><b>Sherlock Holmes has disappeared.</b></p>"
            "<p>Three of his old case files lie open in Baker Street. Reopen them with "
            "Dr. Watson, examine each scene, and deduce what Holmes knew. "
            "Solve all three to follow his trail.</p>"
            "</div>",
            unsafe_allow_html=True
        )

        with st.container(key="hero_actions"):
            if state.has_progress():
                solved = len(st.session_state.solved)
                first, second, _ = st.columns([1.1, 0.9, 1.4])

                if first.button("Continue investigation", type="primary", use_container_width=True):
                    st.session_state.view = "case"
                    st.rerun()

                if second.button("Start over", use_container_width=True,
                                 help="Erase the notebook, the conversations and the solved cases."):
                    state.reset_progress()
                    st.session_state.view = "case"
                    st.rerun()

                st.caption(f"{solved} of {len(cases)} case files solved in this session.")
            else:
                first, _ = st.columns([1, 2])

                if first.button("Begin investigation", type="primary", use_container_width=True):
                    state.open_case(0)
                    st.rerun()

    files = []

    for position, case in enumerate(cases):
        if state.is_solved(case):
            status, css = "Solved", ""
        elif state.is_unlocked(position):
            status, css = "Open", ""
        else:
            status, css = "Locked", " locked"

        files.append(
            f"<div class='file{css}'>"
            f"<div class='thumb' style=\"background-image:url('{static_url(case['image'])}')\"></div>"
            f"<div><div class='n'>Case file {ROMAN[position]} · {status}</div>"
            f"<div class='t'>{esc(case['title'])}</div>"
            f"<div class='s'>{esc(case['teaser'])}</div></div></div>"
        )

    st.markdown(f"<div class='files'>{''.join(files)}</div>", unsafe_allow_html=True)


def draw_finale(cases):
    st.html(
        f"<style>.st-key-finale_hero {{ background-image: "
        f"linear-gradient(0deg, rgba(8,11,16,.95) 0%, rgba(8,11,16,.6) 55%, rgba(8,11,16,.45) 100%),"
        f"radial-gradient(ellipse at center, rgba(8,11,16,.55), transparent 70%),"
        f"url('{static_url(FINALE_IMAGE)}'); }}</style>"
    )

    with st.container(key="finale_hero"):
        draw_finale_head()

    draw_finale_cases(cases)


def draw_finale_head():
    st.markdown(
        "<div class='finale-head'><div class='kicker'>All three case files are closed</div>"
        "<h1>The trail is complete</h1>"
        "<p>A snake on a bell-rope, a gem in a goose, a tunnel under a bank. "
        "Every deduction Holmes once made, you have made again. "
        "All three cases are solved. Holmes can be found.</p></div>"
        "<div class='pending-banner'><b>Final chapter pending.</b> The ending of the "
        "story (where Holmes is and why he left) has not been written by the team yet. "
        "This screen is a placeholder, not the definitive conclusion.</div>",
        unsafe_allow_html=True
    )


def draw_finale_cases(cases):
    columns = st.columns(len(cases))

    for position, case in enumerate(cases):
        columns[position].markdown(
            f"<div class='solved-card'><div class='n'>✓ Case file {ROMAN[position]}</div>"
            f"<div class='t'>{esc(case['title'])}</div><p>{esc(case['solution_note'])}</p></div>",
            unsafe_allow_html=True
        )

    st.write("")
    _, left, right, _ = st.columns([1, 1, 1, 1])

    if left.button("Review the case files", use_container_width=True):
        state.open_case(len(cases) - 1)
        st.rerun()

    if right.button("Open the Research Lab", use_container_width=True):
        st.session_state.view = "lab"
        st.rerun()
