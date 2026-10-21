
# -------------------------------------------------------------------------
# Builds reports/review/evaluation_review.json: the preliminary AI review of the
# 60 evaluation runs in a structured form (version 2).
#
#   version 1  reports/review/evaluation_review.md (kept unchanged)
#   version 2  version 1 + the corrections listed in CORRECTIONS below,
#              documented in reports/review/evaluation_review_corrections.md
#
# The answers and contexts come from reports/results/evaluation_results.json and are
# never modified. All assessments are preliminary, made by an AI, and
# pending human review.
# -------------------------------------------------------------------------

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REVIEW_V1 = BASE_DIR / "reports" / "review" / "evaluation_review.md"
RESULTS_FILE = BASE_DIR / "reports" / "results" / "evaluation_results.json"
OUTPUT = BASE_DIR / "reports" / "review" / "evaluation_review.json"

SECTIONS = {
    "KMP": "kmp",
    "Z-function": "z",
    "Búsqueda aproximada (Levenshtein + Jaccard)": "approximate"
}

CORRECTED_REFERENCES = {
    "RH05": {
        "v1_expected_answer": "French gold: napoleons, 2,000 in each crate, packed between layers of lead foil.",
        "v2_expected_answer": "French gold: napoleons packed between layers of lead foil. The crate "
                              "Merryweather sits on contains 2,000 napoleons; 30,000 were borrowed in total.",
        "reason": "The story gives the quantity for one crate only (\"The crate upon which I sit contains "
                  "2,000 napoleons\") and the total borrowed (\"30,000 napoleons from the Bank of France\"); "
                  "it never says \"each crate\". reports/results/evaluation_questions.json is left unchanged; this is "
                  "the corrected reference used in version 2."
    }
}

# (question id, engines) -> new values and reason
CORRECTIONS = [
    {
        "id": "SB02", "engines": ["kmp", "z"],
        "set": {"support": "completo"},
        "justification": "speckled_band_035 says the ventilator opens \"into another room\" instead of "
                         "\"the outside air\", which supports, by inference, that it leads inside the "
                         "house. The answer is incomplete (it does not say another room, nor Roylott's) "
                         "but makes no unsupported claim: correctness stays partial, support becomes complete.",
        "reason": "v1 mixed incompleteness with lack of support."
    },
    {
        "id": "RH05", "engines": ["kmp", "z", "approximate"],
        "set": {"correctness": "parcial", "support": "parcial"},
        "justification": "red_headed_league_040 supports napoleons packed between layers of lead foil and "
                         "\"Your French gold?\". \"The crates contained 2,000 napoleons\" generalizes the "
                         "quantity of one crate to the crates (the text gives 2,000 for one crate and "
                         "30,000 in total), and the answer omits that it is French gold.",
        "reason": "v1 accepted the quantity against a reference (\"2,000 in each crate\") that the story "
                  "does not support."
    },
    {
        "id": "RH06", "engines": ["approximate"],
        "set": {"correctness": "abstención (no válida)"},
        "justification": "\"The passage does not mention a girl named Cook\" is true for the context (no "
                         "girl appears in it) and invents nothing, but it reads \"cooked\" as the name "
                         "\"Cook\" and denies something the question did not ask. It does not say that "
                         "the girl's name is unknown, so it is not a valid abstention on the question "
                         "asked, although abstaining would have been appropriate.",
        "reason": "v1 counted a misread question as an appropriate abstention."
    }
]


def parse_v1():
    text = REVIEW_V1.read_text(encoding="utf-8")
    entries = {}
    engine = None
    current = None

    for line in text.splitlines():
        if line.startswith("## "):
            engine = SECTIONS.get(line[3:].strip())
            continue

        heading = re.match(r"### (\w+) · (\w+)", line)
        if heading and engine:
            current = {"id": heading.group(1), "type": heading.group(2), "engine": engine}
            entries[(current["id"], engine)] = current
            continue

        if current is None:
            continue

        for label, key in [("Utilidad del contexto", "context_usefulness"), ("Corrección", "correctness"),
                           ("Respaldo en el contexto", "support")]:
            match = re.match(rf"- {label}: \*\*(.+)\*\*$", line)
            if match:
                current[key] = match.group(1)

        if line.startswith("- Justificación: "):
            current["justification"] = line[len("- Justificación: "):]

    return entries


def main():
    entries = parse_v1()
    results = {(r["id"], r["algorithm"]): r for r in json.load(open(RESULTS_FILE, encoding="utf-8"))["results"]}

    assert len(entries) == 60, len(entries)

    for (qid, engine), entry in entries.items():
        run = results[(qid, engine)]
        entry["question"] = run["question"]
        entry["answer"] = run["answer"]
        entry["context_chunk_ids"] = [c["chunk_id"] for c in run["context"]]
        entry["expected_answer"] = (CORRECTED_REFERENCES.get(qid, {}).get("v2_expected_answer")
                                    or run["expected_answer"])
        entry["changed_in_v2"] = False

    for correction in CORRECTIONS:
        for engine in correction["engines"]:
            entry = entries[(correction["id"], engine)]
            entry["v1"] = {key: entry[key] for key in ["context_usefulness", "correctness", "support",
                                                       "justification"]}
            entry.update(correction["set"])
            entry["justification"] = correction["justification"]
            entry["correction_reason"] = correction["reason"]
            entry["changed_in_v2"] = True

    ordered = sorted(entries.values(), key=lambda e: (["kmp", "z", "approximate"].index(e["engine"]),
                                                      list(results).index((e["id"], e["engine"]))))

    with open(OUTPUT, "w", encoding="utf-8") as file:
        json.dump({
            "status": "Preliminary AI assessment, pending human review. Not a human evaluation.",
            "version": 2,
            "sources": {
                "version_1": "reports/review/evaluation_review.md",
                "corrections": "reports/review/evaluation_review_corrections.md",
                "answers_and_contexts": "reports/results/evaluation_results.json (unchanged)"
            },
            "corrected_references": CORRECTED_REFERENCES,
            "corrections": CORRECTIONS,
            "entries": ordered
        }, file, ensure_ascii=False, indent=2)

    changed = [(e["id"], e["engine"]) for e in ordered if e["changed_in_v2"]]
    print(f"{len(ordered)} entries written to {OUTPUT}; changed in v2: {changed}")


if __name__ == "__main__":
    main()
