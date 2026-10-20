
# -------------------------------------------------------------------------
# Custom components (plain HTML + JavaScript, no build step).
#
#   scene_view   the case image with clickable objects
#   ask_box      Watson's question box with Trie autocomplete
#
# Both return the last event as a dict {"type", ..., "ts"}; use
# state.take_event(key) to handle each event only once.
# -------------------------------------------------------------------------

from pathlib import Path

import streamlit.components.v1 as components

COMPONENTS_DIR = Path(__file__).resolve().parent.parent / "components"

_scene = components.declare_component("scene", path=str(COMPONENTS_DIR / "scene"))
_ask = components.declare_component("ask", path=str(COMPONENTS_DIR / "ask"))


TITLE_IMAGE = "static/scenes/title_baker_street.jpg"
FINALE_IMAGE = "static/scenes/finale_dawn.jpg"
WATSON_PORTRAIT = "static/ui/watson_portrait.jpg"


def static_url(path):
    """
        Files in the "static" folder are served by Streamlit at app/static/.
    """
    return "app/" + path


def watson_avatar():
    # Decorative: the bubble already names Dr. Watson.
    return (f"<div class='avatar' aria-hidden='true'>"
            f"<img src='{static_url(WATSON_PORTRAIT)}' alt=''></div>")


def scene_view(case, label, inspected, recorded, key):
    hotspots = []

    for hotspot in case["hotspots"]:
        hotspots.append({
            "id": hotspot["id"],
            "name": hotspot["name"],
            "x": hotspot["x"],
            "y": hotspot["y"],
            "observation": hotspot["observation"],
            "note": hotspot["note"],
            "quote": hotspot["quote"],
            "inspected": hotspot["id"] in inspected,
            "recorded": hotspot["id"] in recorded
        })

    return _scene(
        case_id=case["id"],
        image=static_url(case["image"]),
        alt=case["image_alt"],
        label=label,
        story=case["story"],
        hotspots=hotspots,
        key=key,
        default=None
    )


def ask_box(key, prefix, suggestions, starters, clear_token, scroll_token, log_key,
            placeholder):
    return _ask(
        prefix=prefix,
        suggestions=suggestions,
        starters=starters,
        clear_token=clear_token,
        scroll_token=scroll_token,
        log_key=log_key,
        placeholder=placeholder,
        key=key,
        default=None
    )
