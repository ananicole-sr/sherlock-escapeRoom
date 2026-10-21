
# -------------------------------------------------------------------------
# Sherlock Holmes - The Final Case
#
#   streamlit run app.py
#
# Screens: title (intro), investigation (case), conclusion (finale) and
# Research Lab (lab). The game state lives in st.session_state (ui/state.py)
# and the heavy resources (collection, language model) are loaded once per
# process, so reruns never repeat them.
# -------------------------------------------------------------------------

import json
import threading
from pathlib import Path

import streamlit as st

import watson
from approximate_search import load_collection
from autocomplete import get_trie
from ui import state
from ui.investigation import draw_investigation
from ui.lab import draw_research_lab
from ui.results import draw_results
from ui.screens import draw_intro, draw_finale
from ui.theme import apply_theme

BASE_DIR = Path(__file__).resolve().parent
CASES_FILE = BASE_DIR / "data" / "cases.json"

st.set_page_config(
    page_title="Sherlock Holmes - The Final Case",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)


@st.cache_resource
def get_collection():
    return load_collection()


@st.cache_resource
def get_cases():
    with open(CASES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def _load_model_quietly():
    try:
        watson.load_model()
    except Exception:
        # The error is reported to the player when Watson is asked.
        pass


@st.cache_resource
def warm_up():
    """
        Builds the Trie and starts loading the language model in the
        background, once per process, so the first question is faster.
    """
    get_trie()

    thread = threading.Thread(target=_load_model_quietly, daemon=True)
    thread.start()

    return thread


def draw_topbar():
    with st.container(key="topbar"):
        brand, nav = st.columns([1.1, 1.5], vertical_alignment="center")

        brand.markdown(
            "<div class='brand'><span class='mark'>The Final <span>Case</span></span>"
            "<span class='sub'>Sherlock Holmes has disappeared</span></div>",
            unsafe_allow_html=True
        )

        with nav:
            with st.container(key="nav"):
                home, game, lab, results = st.columns([0.7, 1.05, 1.05, 1.3])
                view = st.session_state.view

                if home.button("Title", use_container_width=True,
                               type="primary" if view == "intro" else "secondary"):
                    st.session_state.view = "intro"
                    st.rerun()

                if game.button("Investigation", use_container_width=True,
                               type="primary" if view in ("case", "finale") else "secondary"):
                    st.session_state.view = "case"
                    st.rerun()

                if lab.button("Research Lab", use_container_width=True,
                              type="primary" if view == "lab" else "secondary"):
                    st.session_state.view = "lab"
                    st.rerun()

                if results.button("Resultados y análisis", use_container_width=True,
                                  type="primary" if view == "results" else "secondary"):
                    st.session_state.view = "results"
                    st.rerun()


def main():
    apply_theme()
    state.init_state()

    cases = get_cases()
    collection = get_collection()
    warm_up()

    draw_topbar()

    view = st.session_state.view

    if view == "intro":
        draw_intro(cases)
    elif view == "lab":
        draw_research_lab(collection)
    elif view == "results":
        draw_results()
    elif view == "finale" and state.all_solved(cases):
        draw_finale(cases)
    else:
        draw_investigation(cases, collection)


if __name__ == "__main__":
    main()
