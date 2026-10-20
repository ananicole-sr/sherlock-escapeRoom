
# -------------------------------------------------------------------------
# Game state kept in st.session_state, so Streamlit reruns never lose it.
#
#   view            "intro", "case", "finale" or "lab"
#   current_case    index of the open case file
#   unlocked        how many case files can be opened
#   solved          ids of solved cases
#   inspected       case id -> ids of the objects already inspected
#   notebook        recorded observations, in the order they were found
#   chat_history    case id -> conversation with Watson
#   attempts        case id -> number of deductions presented
#   last_event      component key -> timestamp of the last handled event
# -------------------------------------------------------------------------

import streamlit as st

ROMAN = ["I", "II", "III", "IV", "V"]


def init_state():
    defaults = {
        "view": "intro",
        "current_case": 0,
        "unlocked": 1,
        "solved": [],
        "inspected": {},
        "notebook": [],
        "chat_history": {},
        "attempts": {},
        "last_event": {},
        "ask_suggestions": {},
        "ask_clear": 0,
        "lab_response": None,
        "lab_reply": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_progress():
    for key in ["view", "current_case", "unlocked", "solved", "inspected",
                "notebook", "chat_history", "attempts", "last_event",
                "ask_suggestions"]:
        if key in st.session_state:
            del st.session_state[key]

    init_state()


def has_progress():
    if len(st.session_state.solved) > 0 or len(st.session_state.notebook) > 0:
        return True

    for case_id in st.session_state.inspected:
        if len(st.session_state.inspected[case_id]) > 0:
            return True

    for case_id in st.session_state.chat_history:
        if len(st.session_state.chat_history[case_id]) > 0:
            return True

    return False


def take_event(key):
    """
        Returns the last value sent by a custom component only the first
        time it is seen. Component values persist between reruns, so each
        event carries a timestamp that is remembered once handled.
    """
    value = st.session_state.get(key)

    if not isinstance(value, dict) or "ts" not in value:
        return None

    if st.session_state.last_event.get(key) == value["ts"]:
        return None

    st.session_state.last_event[key] = value["ts"]

    return value


# -------------------------------------------------------------------------
# Objects and notebook
# -------------------------------------------------------------------------

def inspected_in(case_id):
    return st.session_state.inspected.setdefault(case_id, [])


def mark_inspected(case_id, hotspot_id):
    inspected = inspected_in(case_id)

    if hotspot_id not in inspected:
        inspected.append(hotspot_id)


def is_recorded(case_id, hotspot_id):
    for entry in st.session_state.notebook:
        if entry["case_id"] == case_id and entry["hotspot_id"] == hotspot_id:
            return True

    return False


def record(case_id, hotspot_id):
    mark_inspected(case_id, hotspot_id)

    if not is_recorded(case_id, hotspot_id):
        st.session_state.notebook.append({"case_id": case_id, "hotspot_id": hotspot_id})


def recorded_in(case_id):
    return [entry["hotspot_id"] for entry in st.session_state.notebook
            if entry["case_id"] == case_id]


# -------------------------------------------------------------------------
# Cases, deductions and unlocking
# -------------------------------------------------------------------------

def is_unlocked(position):
    return position < st.session_state.unlocked


def is_solved(case):
    return case["id"] in st.session_state.solved


def all_solved(cases):
    return all(is_solved(case) for case in cases)


def open_case(position):
    st.session_state.current_case = position
    st.session_state.view = "case"


def normalize_answer(text):
    text = text.lower().strip()

    cleaned = ""

    for character in text:
        if character.isalnum() or character == " ":
            cleaned = cleaned + character

    return " ".join(cleaned.split())


def check_answer(case, typed_answer):
    """
        The answer is checked against the predefined list in cases.json,
        never by the language model.
    """
    typed = normalize_answer(typed_answer)

    if len(typed) == 0:
        return False

    for accepted in case["accepted_answers"]:
        if typed == normalize_answer(accepted):
            return True

    return False


def solve(case, cases):
    if case["id"] not in st.session_state.solved:
        st.session_state.solved.append(case["id"])

    position = cases.index(case)

    st.session_state.unlocked = max(st.session_state.unlocked,
                                    min(position + 2, len(cases)))


def count_attempt(case):
    attempts = st.session_state.attempts
    attempts[case["id"]] = attempts.get(case["id"], 0) + 1
