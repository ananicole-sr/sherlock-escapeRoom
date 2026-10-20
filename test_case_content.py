import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CASES_FILE = BASE_DIR / "data" / "cases.json"

STORY_FILES = {
    "The Speckled Band": BASE_DIR / "data" / "speckled_band.txt",
    "The Blue Carbuncle": BASE_DIR / "data" / "blue_carbuncle.txt",
    "The Red-Headed League": BASE_DIR / "data" / "red_headed_league.txt"
}


def normalize(text):
    for curly, straight in [("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"')]:
        text = text.replace(curly, straight)

    return " ".join(text.lower().split())


def main():
    with open(CASES_FILE, "r", encoding="utf-8") as file:
        cases = json.load(file)

    problems = []
    checked = 0
    narrative = 0

    for case in cases:
        story_text = normalize(STORY_FILES[case["story"]].read_text(encoding="utf-8"))

        if not (BASE_DIR / case["image"]).exists():
            problems.append(f"{case['id']}: missing image {case['image']}")

        ids = set()

        for hotspot in case["hotspots"]:
            label = f"{case['id']}/{hotspot['id']}"

            if hotspot["id"] in ids:
                problems.append(f"{label}: duplicated id")
            ids.add(hotspot["id"])

            if not (0 <= hotspot["x"] <= 100 and 0 <= hotspot["y"] <= 100):
                problems.append(f"{label}: coordinates outside the image")

            if hotspot["quote"] is None:
                narrative = narrative + 1
                continue

            checked = checked + 1

            if normalize(hotspot["quote"]) not in story_text:
                problems.append(f"{label}: quote not found in {case['story']}")

        if case["answer"] not in case["accepted_answers"]:
            problems.append(f"{case['id']}: answer is not in accepted_answers")

    print(f"Quotes verified against the stories: {checked}")
    print(f"Hotspots marked as game narrative (no quote): {narrative}")

    if problems:
        print("\nPROBLEMS")
        for problem in problems:
            print("  - " + problem)
        raise SystemExit(1)

    print("All case content is consistent with the documents.")


if __name__ == "__main__":
    main()
