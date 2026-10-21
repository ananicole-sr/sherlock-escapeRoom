
# -------------------------------------------------------------------------
# Visual theme: Victorian investigation.
# Charcoal and night blue backgrounds, dark wood, brass details and aged
# paper surfaces. Serif titles (Cormorant Garamond), legible body (Inter).
#
# Streamlit elements are targeted through their data-testid attributes and
# through the "st-key-<key>" class that Streamlit adds to keyed containers.
# -------------------------------------------------------------------------

import streamlit as st

CSS = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=Inter:wght@400;500;600&display=swap");

:root {
    --night: #0c1017;
    --night-2: #121925;
    --night-3: #1a2331;
    --wood: #2b1f16;
    --wood-2: #3b2a1c;
    --brass: #c8a25a;
    --brass-hi: #e3c47f;
    --brass-lo: #8c6c35;
    --paper: #f1e6cc;
    --paper-2: #e4d5b3;
    --ink: #2a1f15;
    --ink-soft: #5b4733;
    --text: #ede6d8;
    --text-2: #c2b9a7;
    --text-3: #a39a89;
    --ok: #9cc69a;
    --bad: #e8957d;
    --line: rgba(200, 162, 90, 0.24);
    --line-strong: rgba(200, 162, 90, 0.5);
    --serif: "Cormorant Garamond", Georgia, "Times New Roman", serif;
    --sans: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
}

/* ---------- page ---------- */

html, body, .stApp, [class*="css"] {
    font-family: var(--sans);
    -webkit-font-smoothing: antialiased;
}

.stApp {
    color: var(--text);
    background:
        radial-gradient(1200px 600px at 75% -10%, rgba(54, 74, 112, 0.28), transparent 60%),
        radial-gradient(900px 500px at -10% 110%, rgba(59, 42, 28, 0.55), transparent 60%),
        linear-gradient(180deg, #0d121b 0%, var(--night) 55%, #0a0d12 100%);
    background-attachment: fixed;
}

/* The header is invisible but spans the whole width: let clicks reach the
   navigation underneath, except on Streamlit's own menu. */
[data-testid="stHeader"] { background: transparent; height: 0; }
[data-testid="stHeader"], [data-testid="stHeader"] * { pointer-events: none; }
[data-testid="stHeader"] button { pointer-events: auto; }
[data-testid="stToolbar"] { right: 4px; top: 18px; }
/* Our own loading states replace Streamlit's running indicator, which
   would otherwise sit on top of the navigation. */
[data-testid="stStatusWidget"] { visibility: hidden; }
[data-testid="stDecoration"],
[data-testid="stAppDeployButton"],
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"] { display: none !important; }

[data-testid="stMainBlockContainer"], .block-container {
    max-width: 1840px;
    padding: 16px 20px 40px !important;
}

@media (max-width: 640px) {
    [data-testid="stMainBlockContainer"], .block-container { padding: 12px 16px 40px !important; }
}

p, li { color: var(--text); }

h1, h2, h3 {
    font-family: var(--serif) !important;
    color: var(--text) !important;
    letter-spacing: 0.005em;
}

a { color: var(--brass-hi); }

::selection { background: rgba(200, 162, 90, 0.35); }

/* ---------- controls ---------- */

.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    min-height: 44px;
    border-radius: 10px;
    border: 1px solid var(--line-strong);
    background: rgba(18, 25, 37, 0.75);
    color: var(--text);
    font-family: var(--sans);
    font-weight: 500;
    transition: border-color 0.15s ease-out, background 0.15s ease-out, transform 0.1s ease-out;
}

.stButton > button:hover {
    border-color: var(--brass-hi);
    background: rgba(200, 162, 90, 0.1);
    color: var(--text);
}

.stButton > button:active { transform: scale(0.985); }

.stButton > button:focus-visible,
.stFormSubmitButton > button:focus-visible {
    outline: 2px solid var(--brass-hi) !important;
    outline-offset: 2px;
    box-shadow: none !important;
}

.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {
    border: 0;
    background: linear-gradient(180deg, var(--brass-hi), var(--brass));
    color: #1b130a !important;
    font-weight: 600;
    box-shadow: 0 6px 18px rgba(200, 162, 90, 0.22);
}

.stButton > button[kind="primary"] p, [data-testid="stBaseButton-primary"] p,
.stFormSubmitButton > button[kind="primaryFormSubmit"] p { color: #1b130a !important; font-weight: 600; }

.stFormSubmitButton > button[kind="primaryFormSubmit"] {
    border: 0;
    background: linear-gradient(180deg, var(--brass-hi), var(--brass));
    color: #1b130a !important;
}

.stButton > button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(180deg, #ecd092, var(--brass-hi));
    color: #1b130a !important;
}

.stButton > button:disabled {
    opacity: 0.55;
    cursor: not-allowed;
}

.stTextInput input, .stTextArea textarea, [data-baseweb="select"] > div {
    background: var(--night-3) !important;
    color: var(--text) !important;
    border-color: var(--line) !important;
    border-radius: 10px !important;
    font-family: var(--sans);
}

.stTextInput input { min-height: 44px; }

.stTextInput [data-baseweb="input"] {
    border-radius: 10px !important;
    border: 1px solid var(--line) !important;
    background: var(--night-3) !important;
}

.stTextInput [data-baseweb="input"]:focus-within {
    border-color: var(--brass) !important;
    box-shadow: 0 0 0 3px rgba(200, 162, 90, 0.25);
}

label, [data-testid="stWidgetLabel"] p { color: var(--text-2) !important; font-weight: 500; }

[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: var(--text-3) !important; }

/* tabs */
[data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--line) !important; }
[data-baseweb="tab-highlight"] { background: var(--brass-hi) !important; }
[data-baseweb="tab-border"] { display: none; }
button[role="tab"] {
    min-height: 42px;
    padding: 0 14px !important;
    background: transparent !important;
}
button[role="tab"] p { color: var(--text-2) !important; font-weight: 600 !important; font-size: 14.5px !important; }
button[role="tab"][aria-selected="true"] p { color: var(--brass-hi) !important; }
button[role="tab"]:focus-visible { outline: 2px solid var(--brass-hi); outline-offset: -2px; border-radius: 8px; }

/* expanders */
[data-testid="stExpander"] details {
    border: 1px solid var(--line) !important;
    border-radius: 10px !important;
    background: rgba(18, 25, 37, 0.55);
}
[data-testid="stExpander"] summary p { color: var(--text-2) !important; font-size: 13.5px; }
[data-testid="stExpander"] summary:focus-visible { outline: 2px solid var(--brass-hi); border-radius: 10px; }

/* bordered containers */
[data-testid="stVerticalBlockBorderWrapper"] { border-color: var(--line) !important; border-radius: 14px !important; }

/* alerts */
[data-testid="stAlert"] { border-radius: 10px; }

/* metrics */
[data-testid="stMetric"] {
    padding: 14px 16px;
    border-radius: 12px;
    border: 1px solid var(--line);
    background: rgba(18, 25, 37, 0.7);
}
[data-testid="stMetricLabel"] p { color: var(--text-3) !important; font-size: 12.5px !important; text-transform: uppercase; letter-spacing: 0.06em; }
[data-testid="stMetricValue"] { color: var(--text) !important; font-family: var(--serif); font-weight: 600; font-size: 26px !important; overflow-wrap: anywhere; white-space: normal !important; }

/* dialogs */
div[role="dialog"] {
    background:
        linear-gradient(180deg, rgba(26, 35, 49, 0.98), rgba(12, 16, 23, 0.98)) !important;
    border: 1px solid var(--line-strong) !important;
    border-radius: 16px !important;
    color: var(--text);
}
div[role="dialog"] h2 { font-size: 30px !important; }

/* ---------- top bar ---------- */

.st-key-topbar {
    padding-right: 40px;
    padding-bottom: 10px;
    margin-bottom: 6px;
    border-bottom: 1px solid var(--line);
}

.brand { display: flex; align-items: baseline; gap: 12px; min-height: 44px; flex-wrap: wrap; }
.brand .mark {
    font-family: var(--serif);
    font-size: 26px;
    font-weight: 700;
    color: var(--text);
    letter-spacing: 0.01em;
    line-height: 44px;
}
.brand .mark span { color: var(--brass-hi); }
.brand .sub { font-size: 12.5px; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-3); }

.st-key-nav .stButton > button { min-height: 40px; border-radius: 999px; font-size: 14px; }

/* ---------- case header ---------- */

.case-head .kicker {
    font-size: 12px;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--brass-hi);
}
.case-head h1 {
    margin: 2px 0 4px !important;
    padding: 0 !important;
    font-size: clamp(30px, 3.4vw, 44px) !important;
    line-height: 1.05 !important;
    font-weight: 700 !important;
}
.case-head .objective { margin: 0; color: var(--text-2); font-size: 15px; }
.case-head .objective b { color: var(--text); font-weight: 600; }

/* progress between the three case files */
.st-key-tracker [data-testid="stHorizontalBlock"] { gap: 8px; }
.st-key-tracker .stButton > button {
    width: 100%;
    min-height: 48px;
    padding: 6px 12px;
    border-radius: 10px;
    justify-content: flex-start;
    text-align: left;
    font-size: 13.5px;
    line-height: 1.2;
}
.st-key-tracker .stButton > button p { font-size: 13.5px; }

/* ---------- deduction bar ---------- */

.st-key-deduce {
    margin-top: 4px;
    padding: 12px 14px;
    gap: 10px !important;
    border-radius: 12px;
    border: 1px solid var(--line);
    background:
        linear-gradient(90deg, rgba(59, 42, 28, 0.55), rgba(18, 25, 37, 0.6));
}
.deduce-copy .title { font-family: var(--serif); font-size: 21px; font-weight: 700; color: var(--text); line-height: 1.2; }
.deduce-copy { padding-bottom: 10px; }
.deduce-copy .body { margin-top: 2px; font-size: 13.5px; line-height: 1.45; color: var(--text-2); }

/* ---------- scene and side columns ---------- */

/* The scene column is exactly as wide as the scene, which shrinks to fit
   the window height (same formula as fitToWindow in components/scene:
   330 px reserved, image ratio 1672/941, at least 480 px). The space left
   over goes to Watson, so the gap between both columns stays at 28 px. */
@media (min-width: 641px) {
    [data-testid="stHorizontalBlock"]:has(.st-key-panel) {
        gap: 28px !important;
    }
    [data-testid="stHorizontalBlock"]:has(.st-key-panel) > [data-testid="stColumn"]:first-child {
        flex: 0 1 min(calc(65% - 14px), max(480px, calc((100vh - 330px) * 1.7768))) !important;
        width: auto !important;
        min-width: 0 !important;
    }
    [data-testid="stHorizontalBlock"]:has(.st-key-panel) > [data-testid="stColumn"]:last-child {
        flex: 1 1 0 !important;
        width: auto !important;
        min-width: 0 !important;
    }
}

/* ---------- side panel ---------- */

.st-key-panel {
    padding: 4px 14px 12px;
    border-radius: 14px;
    border: 1px solid var(--line);
    background: linear-gradient(180deg, rgba(26, 35, 49, 0.85), rgba(18, 25, 37, 0.85));
}

.st-key-chat_log [data-testid="stVerticalBlockBorderWrapper"],
.st-key-chat_log { border: 0 !important; }

.msg { display: flex; gap: 10px; margin: 0 0 12px; animation: msg-in 0.22s ease-out; }
@keyframes msg-in { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }

.msg .avatar {
    flex: none;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    overflow: hidden;
    background: var(--night-3);
    box-shadow: 0 0 0 1.5px var(--brass), 0 2px 6px rgba(0, 0, 0, 0.5);
}
.msg .avatar img { display: block; width: 100%; height: 100%; object-fit: cover; }
.msg .bubble {
    padding: 10px 14px;
    border-radius: 4px 14px 14px 14px;
    background: rgba(241, 230, 204, 0.06);
    border: 1px solid var(--line);
    font-size: 14.5px;
    line-height: 1.55;
    color: var(--text);
    max-width: 100%;
    overflow-wrap: anywhere;
}
.msg .who { display: block; font-size: 11.5px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--brass-hi); margin-bottom: 2px; }
.msg.you { justify-content: flex-end; }
.msg.you .bubble { border-radius: 14px 4px 14px 14px; background: rgba(200, 162, 90, 0.16); border-color: var(--line-strong); }
.msg.you .who { color: var(--text-2); text-align: right; }
.msg .meta { display: block; margin-top: 6px; font-size: 12px; color: var(--text-3); }

.notice {
    margin: 0 0 12px 46px;
    padding: 8px 12px;
    border-radius: 8px;
    border-left: 3px solid var(--text-3);
    background: rgba(255, 255, 255, 0.03);
    font-size: 13px;
    color: var(--text-2);
}
.notice.error { border-left-color: var(--bad); }
.notice.error b { color: var(--bad); }
.notice code { font-size: 12px; color: var(--text-2); background: transparent; white-space: pre-wrap; }
.notice details { margin-top: 6px; }
.notice summary { cursor: pointer; color: var(--text-3); font-size: 12px; }
.notice summary:focus-visible { outline: 2px solid var(--brass-hi); border-radius: 4px; }

.working { display: flex; align-items: center; gap: 10px; margin: 0 0 12px 46px; font-size: 13.5px; color: var(--text-2); }
.working .dots span {
    display: inline-block; width: 6px; height: 6px; margin-right: 3px; border-radius: 50%;
    background: var(--brass-hi); animation: blink 1.2s infinite ease-in-out;
}
.working .dots span:nth-child(2) { animation-delay: 0.15s; }
.working .dots span:nth-child(3) { animation-delay: 0.3s; }
@keyframes blink { 0%, 80%, 100% { opacity: 0.25; } 40% { opacity: 1; } }

.passage {
    margin: 6px 0 10px;
    padding: 8px 12px;
    border-left: 2px solid var(--brass-lo);
    font-family: var(--serif);
    font-size: 16px;
    line-height: 1.4;
    color: var(--text-2);
}
.passage .src { display: block; font-family: var(--sans); font-size: 11.5px; color: var(--text-3); margin-bottom: 2px; }

/* ---------- notebook ---------- */

.nb-head { display: flex; justify-content: space-between; align-items: baseline; margin: 6px 0 8px; }
.nb-head .t { font-family: var(--serif); font-size: 21px; font-weight: 700; color: var(--text); }
.nb-head .c { font-size: 12.5px; color: var(--text-3); }

.nb-entry {
    margin: 0 0 10px;
    border-radius: 6px;
    background: linear-gradient(180deg, var(--paper), var(--paper-2));
    color: var(--ink);
    box-shadow: 0 0 0 1px rgba(90, 68, 40, 0.45);
}
.nb-entry summary {
    list-style: none;
    cursor: pointer;
    padding: 10px 14px;
    border-radius: 6px;
}
.nb-entry summary::-webkit-details-marker { display: none; }
.nb-entry summary:focus-visible { outline: 2px solid var(--brass-hi); outline-offset: 2px; }
.nb-entry .name { font-family: var(--serif); font-size: 19px; font-weight: 700; color: var(--ink); display: block; line-height: 1.2; }
.nb-entry .note { font-size: 13.5px; color: #33271b; display: block; margin-top: 2px; }
.nb-entry .tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px; }
.nb-entry .tag { font-size: 11px; letter-spacing: 0.04em; padding: 2px 7px; border-radius: 4px; background: rgba(91, 71, 51, 0.12); color: var(--ink-soft); }
.nb-entry .tag.ok { background: rgba(61, 107, 58, 0.14); color: #2f5a2c; }
.nb-entry .more { padding: 0 14px 12px; font-size: 13.5px; color: #33271b; line-height: 1.5; }
.nb-entry .more blockquote { margin: 8px 0 0; padding: 6px 10px; border-left: 3px solid var(--brass-lo); font-family: var(--serif); font-style: italic; font-size: 15px; color: #3b2c1d; }
.nb-entry.pending { background: rgba(241, 230, 204, 0.06); box-shadow: 0 0 0 1px var(--line); }
.nb-entry.pending .name { color: var(--text); }
.nb-entry.pending .note { color: var(--text-2); }
.nb-entry.pending .tag { background: rgba(255, 255, 255, 0.06); color: var(--text-3); }

.nb-empty { padding: 14px; border: 1px dashed var(--line); border-radius: 10px; font-size: 13.5px; color: var(--text-2); }

/* ---------- parchment (riddle) ---------- */

.parchment {
    position: relative;
    padding: 26px 30px;
    border-radius: 6px;
    background:
        radial-gradient(ellipse at 20% 10%, rgba(255, 255, 255, 0.4), transparent 50%),
        linear-gradient(180deg, var(--paper), var(--paper-2));
    color: var(--ink);
    box-shadow: 0 0 0 1px rgba(90, 68, 40, 0.5), 0 18px 40px rgba(0, 0, 0, 0.5);
    font-family: var(--serif);
    font-size: 21px;
    line-height: 1.5;
    white-space: pre-wrap;
    text-align: center;
}
.parchment .kicker { display: block; font-family: var(--sans); font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--ink-soft); margin-bottom: 8px; }

.verdict { margin-top: 14px; padding: 14px 16px; border-radius: 10px; font-size: 14.5px; line-height: 1.55; }
.verdict b { font-family: var(--serif); font-size: 20px; display: block; margin-bottom: 2px; }
.verdict.ok { background: rgba(156, 198, 154, 0.1); border: 1px solid rgba(156, 198, 154, 0.45); }
.verdict.ok b { color: var(--ok); }
.verdict.bad { background: rgba(232, 149, 125, 0.08); border: 1px solid rgba(232, 149, 125, 0.45); }
.verdict.bad b { color: var(--bad); }

/* ---------- intro ---------- */

.st-key-hero {
    position: relative;
    min-height: min(74vh, 680px);
    margin-top: 8px;
    padding: 56px 52px 40px;
    border-radius: 18px;
    border: 1px solid var(--line);
    background-color: var(--night-2);
    background-size: cover;
    background-position: center right;
    justify-content: flex-end;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.45);
    animation: fade-in 0.6s ease-out;
}
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }

.hero-copy { max-width: 600px; }
.hero-copy .kicker { font-size: 12.5px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--brass-hi); }
.hero-copy h1 {
    margin: 10px 0 14px !important;
    padding: 0 !important;
    font-size: clamp(46px, 6vw, 88px) !important;
    line-height: 0.95 !important;
    font-weight: 700 !important;
}
.hero-copy h1 em { font-style: italic; font-weight: 500; color: var(--brass-hi); }
.hero-copy p { font-size: 17px; line-height: 1.6; color: var(--text-2); margin: 0 0 10px; }
.hero-copy p b { color: var(--text); font-weight: 600; font-size: 19px; }

.st-key-hero_actions { max-width: 600px; margin-top: 8px; }
.st-key-hero_actions .stButton > button { min-height: 50px; font-size: 16px; }

@media (max-width: 640px) {
    .st-key-hero { min-height: 72vh; padding: 28px 20px 22px; background-position: 70% center; }
}

.files { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 18px; }
@media (max-width: 760px) { .files { grid-template-columns: 1fr; } }
.file {
    position: relative;
    display: flex;
    gap: 14px;
    align-items: center;
    padding: 10px;
    border-radius: 12px;
    border: 1px solid var(--line);
    background: rgba(18, 25, 37, 0.7);
}
.file .thumb { flex: none; width: 96px; height: 56px; border-radius: 6px; background-size: cover; background-position: center; filter: brightness(1.1); }
.file.locked .thumb { filter: grayscale(0.9) brightness(0.55); }
.file .n { font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--brass-hi); }
.file .t { font-family: var(--serif); font-size: 20px; font-weight: 700; color: var(--text); line-height: 1.1; }
.file .s { font-size: 12.5px; color: var(--text-3); }

/* ---------- finale ---------- */

.st-key-finale_hero {
    margin: 8px 0 18px;
    padding: 64px 24px 28px;
    min-height: min(60vh, 520px);
    justify-content: flex-end;
    border-radius: 18px;
    border: 1px solid var(--line);
    background-color: var(--night-2);
    background-size: cover;
    background-position: center 40%;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.45);
    animation: fade-in 0.6s ease-out;
}
.finale-head { text-align: center; margin: 28px auto 18px; max-width: 760px; }
.finale-head p { text-shadow: 0 1px 8px rgba(0, 0, 0, 0.8); }
.finale-head .kicker { font-size: 12.5px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--brass-hi); }
.finale-head h1 { font-size: clamp(38px, 5vw, 64px) !important; margin: 6px 0 8px !important; }
.finale-head p { color: var(--text-2); font-size: 16.5px; }
.pending-banner {
    max-width: 760px;
    margin: 0 auto 18px;
    padding: 12px 16px;
    border-radius: 10px;
    border: 1px dashed var(--line-strong);
    color: var(--text-2);
    font-size: 14px;
    text-align: center;
}
.solved-card { padding: 16px 18px; border-radius: 12px; border: 1px solid var(--line); background: rgba(18, 25, 37, 0.7); height: 100%; }
.solved-card .n { font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--ok); }
.solved-card .t { font-family: var(--serif); font-size: 24px; font-weight: 700; margin: 2px 0 6px; color: var(--text); }
.solved-card p { font-size: 14px; color: var(--text-2); margin: 0; }

/* ---------- research lab ---------- */

.lab-head h1 { font-size: 40px !important; margin: 6px 0 2px !important; }
.lab-head p { color: var(--text-2); margin: 0 0 6px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 4px 0 10px; }
.chips span { padding: 3px 9px; border-radius: 999px; border: 1px solid var(--line); font-size: 12.5px; color: var(--text-2); }
.chips span.fix { border-color: var(--brass); color: var(--brass-hi); }
.result {
    padding: 12px 14px;
    margin-bottom: 10px;
    border-radius: 10px;
    border: 1px solid var(--line);
    background: rgba(18, 25, 37, 0.7);
}
.result .top { display: flex; justify-content: space-between; gap: 10px; align-items: baseline; flex-wrap: wrap; }
.result .rank { font-family: var(--serif); font-size: 20px; font-weight: 700; color: var(--brass-hi); margin-right: 6px; }
.result .id { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 13px; color: var(--text); }
.result .story { font-size: 12.5px; color: var(--text-3); }
.result .score { font-size: 13px; color: var(--text-2); }
.result .bar { height: 6px; margin: 8px 0; border-radius: 3px; background: rgba(255, 255, 255, 0.06); overflow: hidden; }
.result .bar i { display: block; height: 100%; background: linear-gradient(90deg, var(--brass-lo), var(--brass-hi)); }
.result .excerpt { font-size: 13.5px; color: var(--text-2); line-height: 1.5; }

/* ---------- small screens ---------- */

@media (max-width: 640px) {
    /* keep navigation and case progress on one row instead of stacking */
    .st-key-nav [data-testid="stHorizontalBlock"],
    .st-key-tracker [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 6px !important;
    }
    .st-key-nav [data-testid="stColumn"],
    .st-key-tracker [data-testid="stColumn"] {
        min-width: 0 !important;
        width: auto !important;
        flex: 1 1 0 !important;
    }
    /* four destinations do not fit in one row on a phone: 2 x 2 grid */
    .st-key-nav [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
    .st-key-nav [data-testid="stColumn"] { flex: 1 1 calc(50% - 6px) !important; }
    .st-key-nav .stButton > button { min-height: 40px; padding: 4px 6px; }
    .st-key-nav .stButton > button p { font-size: 13px !important; }
    .st-key-tracker .stButton > button { min-height: 44px; padding: 4px 8px; justify-content: center; text-align: center; }
    .st-key-tracker .stButton > button p { font-size: 12px !important; }
    .st-key-topbar { padding-right: 28px; }
    .brand .mark { font-size: 22px; line-height: 34px; }
    .brand .sub { display: none; }
    .case-head h1 { font-size: 32px !important; }
    .st-key-deduce { padding: 12px; }
    .parchment { padding: 18px 16px; font-size: 18px; }
}

/* ---------- results & analysis ---------- */

.res-lead { color: var(--text-2); font-size: 14.5px; line-height: 1.6; max-width: 980px; }
.res-caption {
    margin: 8px 0 26px;
    padding: 12px 16px;
    border-left: 3px solid var(--brass);
    border-radius: 0 10px 10px 0;
    background: rgba(18, 25, 37, 0.7);
}
.res-caption p { margin: 0 0 6px; font-size: 13.5px; line-height: 1.55; color: var(--text-2); }
.res-caption p:last-child { margin-bottom: 0; }
.res-caption b { color: var(--text); }
.res-missing, .res-preliminary {
    margin: 8px 0 16px;
    padding: 12px 16px;
    border-radius: 10px;
    font-size: 14px;
    color: var(--text);
}
.res-missing { border: 1px solid rgba(232, 149, 125, 0.55); background: rgba(232, 149, 125, 0.08); }
.res-missing b { color: var(--bad); }
.res-missing code, .res-caption code { color: var(--brass-hi); background: transparent; }
.res-preliminary { border: 1px dashed var(--line-strong); background: rgba(200, 162, 90, 0.08); }
.res-preliminary b { color: var(--brass-hi); }
.res-table { overflow-x: auto; margin: 8px 0 6px; }
.res-table table { width: 100%; border-collapse: collapse; font-size: 13.5px; }
.res-table th {
    text-align: left; font-weight: 600; color: var(--text-2);
    padding: 8px 10px; border-bottom: 1px solid var(--line-strong); white-space: nowrap;
}
.res-table td { padding: 7px 10px; border-bottom: 1px solid var(--line); color: var(--text); }
.res-h3 { font-size: 24px !important; margin: 18px 0 8px !important; }
.res-example {
    margin: 0 0 14px; padding: 14px 16px; border-radius: 12px;
    border: 1px solid var(--line); background: rgba(18, 25, 37, 0.7);
}
.res-q { font-size: 15px; color: var(--text); margin-bottom: 10px; }
.res-q span { font-family: var(--serif); font-weight: 700; color: var(--brass-hi); margin-right: 6px; font-size: 18px; }
.res-answers { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
@media (max-width: 760px) { .res-answers { grid-template-columns: 1fr; } }
.res-answer { padding: 10px 12px; border-radius: 8px; background: rgba(241, 230, 204, 0.05); border: 1px solid var(--line); }
.res-engine { font-size: 11.5px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--brass-hi); margin-bottom: 4px; }
.res-text { font-size: 14px; color: var(--text); line-height: 1.5; }
.res-meta { margin-top: 6px; font-size: 12px; color: var(--text-3); }
.res-why { margin: 10px 0 0; font-size: 13.5px; color: var(--text-2); line-height: 1.55; }
[data-testid="stImage"] { max-width: 980px; }
[data-testid="stImage"] img { border-radius: 10px; max-width: 100%; height: auto; }
.res-caption { max-width: 980px; }

@media (prefers-reduced-motion: reduce) {
    .st-key-hero, .msg, .working .dots span { animation: none !important; }
}
</style>
"""


def apply_theme():
    # st.html adds a style-only block without taking space in the layout.
    st.html(CSS)
