import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_FILE = BASE_DIR / "data" / "processed_chunks.json"
OUTPUT = BASE_DIR / "reports" / "results" / "evaluation_questions.json"

SB = "The Speckled Band"
BC = "The Blue Carbuncle"
RH = "The Red-Headed League"

# Types:
#   direct        the question uses the words of the story or close ones
#   paraphrase    the evidence answers it with different words
#   misspelled    typing errors; original_question is the correct version
#   unanswerable  the collection does not contain the answer
#
# evidence: [chunk_id, exact quote from that chunk's original text].
# answer_keywords: words a correct answer is expected to contain, for an
# automatic first check; answers are still reviewed by hand.
# absent_terms (unanswerable only): words checked to be missing from the
# story, which supports that the answer is not there.

QUESTIONS = [
    # ---------------- The Speckled Band (7) ----------------
    {"id": "SB01", "story": SB, "type": "direct",
     "question": "What were the last words of Helen Stoner's sister?",
     "expected_answer": "\"It was the band! The speckled band!\"",
     "evidence": [["speckled_band_016", "she suddenly shrieked out in a voice which I shall never forget, 'Oh, my God! Helen! It was the band! The speckled band!'"],
                  ["speckled_band_016", "a fresh convulsion seized her and choked her words"]],
     "support_note": "Helen narrates her sister's dying cry; a convulsion then stopped her from saying more.",
     "answer_keywords": ["speckled band"]},
    {"id": "SB02", "story": SB, "type": "direct",
     "question": "Where did the ventilator in Helen Stoner's room lead?",
     "expected_answer": "Into another room (Dr. Roylott's), not to the outside air.",
     "evidence": [["speckled_band_035", "open a ventilator into another room"],
                  ["speckled_band_041", "her sister could smell Dr. Roylott's cigar. Now, of course that suggested at once that there must be a communication between the two rooms"]],
     "support_note": "035: it opens into another room, not outside. 041: that room is Dr. Roylott's.",
     "answer_keywords": ["another room", "roylott", "next room", "adjoining"]},
    {"id": "SB03", "story": SB, "type": "direct",
     "question": "What did Holmes find on top of the iron safe in Dr. Roylott's room?",
     "expected_answer": "A small saucer of milk.",
     "evidence": [["speckled_band_036", "a large iron safe"],
                  ["speckled_band_036", "a small saucer of milk which stood on the top of it"]],
     "support_note": "Same passage: the iron safe in Roylott's room and the saucer of milk on top of it.",
     "answer_keywords": ["saucer", "milk"]},
    {"id": "SB04", "story": SB, "type": "paraphrase",
     "question": "Why could Helen Stoner not move her bed?",
     "expected_answer": "It was clamped to the floor.",
     "evidence": [["speckled_band_042", "It was clamped to the floor"],
                  ["speckled_band_042", "The lady could not move her bed"]],
     "support_note": "Holmes states both the cause and the consequence.",
     "answer_keywords": ["clamped", "fastened"]},
    {"id": "SB05", "story": SB, "type": "misspelled",
     "question": "What animls did Dr. Roylot keep at Stoke Moran?",
     "original_question": "What animals did Dr. Roylott keep at Stoke Moran?",
     "expected_answer": "A cheetah and a baboon (he had a passion for Indian animals).",
     "evidence": [["speckled_band_011", "He has a passion also for Indian animals"],
                  ["speckled_band_011", "he has at this moment a cheetah and a baboon, which wander freely over his grounds"]],
     "support_note": "Helen describes her stepfather's animals on the family estate (Stoke Moran).",
     "answer_keywords": ["cheetah", "baboon"]},
    {"id": "SB06", "story": SB, "type": "misspelled",
     "question": "What was the speckld band realy?",
     "original_question": "What was the speckled band really?",
     "expected_answer": "A swamp adder, the deadliest snake in India.",
     "evidence": [["speckled_band_049", "It is a swamp adder!"],
                  ["speckled_band_049", "the deadliest snake in India"]],
     "support_note": "Holmes identifies the 'speckled band' on Roylott's head.",
     "answer_keywords": ["adder", "snake"]},
    {"id": "SB07", "story": SB, "type": "unanswerable",
     "question": "What colour were the curtains in Helen Stoner's bedroom?",
     "expected_answer": None, "evidence": [],
     "absent_terms": ["curtain"],
     "note": "The story never describes curtains in the bedroom."},

    # ---------------- The Blue Carbuncle (7) ----------------
    {"id": "BC01", "story": BC, "type": "direct",
     "question": "Who picked up the hat and the goose after the fight on Tottenham Court Road?",
     "expected_answer": "Peterson, the commissionaire.",
     "evidence": [["blue_carbuncle_003", "You know Peterson, the commissionaire?"],
                  ["blue_carbuncle_003", "No, no, he found it."],
                  ["blue_carbuncle_004", "he was left in possession of the field of battle, and also of the spoils of victory in the shape of this battered hat and a most unimpeachable Christmas goose"]],
     "support_note": "003 names Peterson the commissionaire and says he found the hat; 004 says the fight left him with the hat and the goose. The previous quotes only said he walked down Tottenham Court Road.",
     "answer_keywords": ["peterson", "commissionaire"]},
    {"id": "BC02", "story": BC, "type": "direct",
     "question": "What initials were written inside the hat?",
     "expected_answer": "H. B. (the card on the goose read 'For Mrs. Henry Baker').",
     "evidence": [["blue_carbuncle_006", "the initials \"H. B.\" were scrawled upon one side"],
                  ["blue_carbuncle_005", "Henry Baker' was printed upon a small card which was tied to the bird's left leg, and it is also true that the initials 'H. B.' are legible upon the lining of this hat"]],
     "support_note": "006 gives the initials; the link to Henry Baker comes from the card quoted in 005, not from the hat itself.",
     "answer_keywords": ["h b", "h.b.", "henry baker"]},
    {"id": "BC03", "story": BC, "type": "direct",
     "question": "Where did Peterson's wife find the blue stone?",
     "expected_answer": "In the crop of the goose.",
     "evidence": [["blue_carbuncle_012", "See what my wife found in its crop!"]],
     "support_note": "Peterson, holding the blue stone, says his wife found it in the goose's crop.",
     "answer_keywords": ["crop", "goose"]},
    {"id": "BC04", "story": BC, "type": "direct",
     "question": "Who was accused of stealing the Countess of Morcar's jewel?",
     "expected_answer": "John Horner, a plumber.",
     "evidence": [["blue_carbuncle_014", "John Horner, 26, plumber, was brought up upon the charge of having upon the 22nd inst., abstracted from the jewel-case of the Countess of Morcar"]],
     "support_note": "The newspaper report states the charge against Horner.",
     "answer_keywords": ["horner"]},
    {"id": "BC05", "story": BC, "type": "misspelled",
     "question": "Wich dealer in Covent Gardn sold the geese to the Alpha Inn?",
     "original_question": "Which dealer in Covent Garden sold the geese to the Alpha Inn?",
     "expected_answer": "Breckinridge.",
     "evidence": [["blue_carbuncle_024", "I got the two dozen from a salesman in Covent Garden"],
                  ["blue_carbuncle_024", "Breckinridge is his name"]],
     "support_note": "The landlord of the Alpha names the Covent Garden salesman.",
     "answer_keywords": ["breckinridge"]},
    {"id": "BC06", "story": BC, "type": "misspelled",
     "question": "What was the real name of the man who called himself John Robinsn?",
     "original_question": "What was the real name of the man who called himself John Robinson?",
     "expected_answer": "James Ryder.",
     "evidence": [["blue_carbuncle_032", "is John Robinson"],
                  ["blue_carbuncle_032", "my real name is James Ryder"]],
     "support_note": "The stranger first gives the alias, then his real name.",
     "answer_keywords": ["ryder"]},
    {"id": "BC07", "story": BC, "type": "unanswerable",
     "question": "What colour was the Countess of Morcar's carriage?",
     "expected_answer": None, "evidence": [],
     "absent_terms": ["carriage"],
     "note": "No carriage is mentioned in the story."},

    # ---------------- The Red-Headed League (6) ----------------
    {"id": "RH01", "story": RH, "type": "direct",
     "question": "How much was Jabez Wilson paid each week by the Red-Headed League?",
     "expected_answer": "Four pounds (£4) a week.",
     "evidence": [["red_headed_league_007", "a salary of £ 4 a week"],
                  ["red_headed_league_018", "Is £ 4 a week"]],
     "support_note": "The advertisement and Duncan Ross both state the pay.",
     "answer_keywords": ["4", "four"]},
    {"id": "RH02", "story": RH, "type": "direct",
     "question": "Who was caught in the bank cellar at the end of the case?",
     "expected_answer": "John Clay.",
     "evidence": [["red_headed_league_044", "It's no use, John Clay"]],
     "support_note": "Said by Holmes to the man coming up through the hole in the bank cellar floor.",
     "answer_keywords": ["clay"]},
    {"id": "RH03", "story": RH, "type": "paraphrase",
     "question": "Why was Jabez Wilson paid to copy the Encyclopaedia?",
     "expected_answer": "To get him out of the way for a number of hours every day.",
     "evidence": [["red_headed_league_046", "to get this not over-bright pawnbroker out of the way for a number of hours every day"]],
     "support_note": "Holmes's explanation: the League and the copying only existed to keep the pawnbroker away.",
     "answer_keywords": ["out of the way", "away from", "absence"],
     "note": "Same question as the Watson diagnostic; the evidence uses different words."},
    {"id": "RH04", "story": RH, "type": "misspelled",
     "question": "Why did Holmes beat the pavment with his stik?",
     "original_question": "Why did Holmes beat the pavement with his stick?",
     "expected_answer": "To find out whether the cellar stretched out in front or behind.",
     "evidence": [["red_headed_league_048", "I surprised you by beating upon the pavement with my stick. I was ascertaining whether the cellar stretched out in front or behind."]],
     "support_note": "Holmes explains it himself; 'the shop' was removed from the expected answer because the quote does not say it.",
     "answer_keywords": ["cellar"]},
    {"id": "RH05", "story": RH, "type": "direct",
     "question": "What was stored in the crates in the bank cellar?",
     "expected_answer": "French gold: napoleons, 2,000 in each crate, packed between layers of lead foil.",
     "evidence": [["red_headed_league_040", "Your French gold?"],
                  ["red_headed_league_040", "borrowed for that purpose 30,000 napoleons from the Bank of France"],
                  ["red_headed_league_040", "The crate upon which I sit contains 2,000 napoleons packed between layers of lead foil"]],
     "support_note": "Merryweather confirms it is the French gold and describes one crate.",
     "answer_keywords": ["napoleon", "gold"]},
    {"id": "RH06", "story": RH, "type": "unanswerable",
     "question": "What was the name of the girl who cooked for Jabez Wilson?",
     "expected_answer": None, "evidence": [],
     "absent_terms": [],
     "note": "The girl is mentioned only as 'a girl of fourteen' (red_headed_league_010); her name is never given."}
]


def normalize(text):
    for curly, straight in [("‘", "'"), ("’", "'"), ("“", '"'), ("”", '"')]:
        text = text.replace(curly, straight)

    return " ".join(text.lower().split())


def main():
    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        chunks = {chunk["id"]: chunk for chunk in json.load(file)}

    problems = []
    ids = set()

    for item in QUESTIONS:
        if item["id"] in ids:
            problems.append(f"{item['id']}: duplicated id")
        ids.add(item["id"])

        if item["type"] == "misspelled" and not item.get("original_question"):
            problems.append(f"{item['id']}: misspelled question without original")

        if item["type"] == "unanswerable":
            if item["evidence"] or item["expected_answer"] is not None:
                problems.append(f"{item['id']}: unanswerable question with evidence or answer")

            story_text = normalize(" ".join(c["original_text"] for c in chunks.values()
                                            if c["story"] == item["story"]))
            for term in item["absent_terms"]:
                if normalize(term) in story_text:
                    problems.append(f"{item['id']}: '{term}' does appear in {item['story']}")
            continue

        if not item["evidence"]:
            problems.append(f"{item['id']}: answerable question without evidence")

        for chunk_id, quote in item["evidence"]:
            chunk = chunks.get(chunk_id)
            if chunk is None:
                problems.append(f"{item['id']}: unknown chunk {chunk_id}")
            elif chunk["story"] != item["story"]:
                problems.append(f"{item['id']}: {chunk_id} belongs to another story")
            elif normalize(quote) not in normalize(chunk["original_text"]):
                problems.append(f"{item['id']}: quote not found in {chunk_id}: {quote!r}")

    counts = {}
    for item in QUESTIONS:
        counts[item["story"]] = counts.get(item["story"], 0) + 1

    if counts != {SB: 7, BC: 7, RH: 6}:
        problems.append(f"wrong distribution: {counts}")

    if problems:
        print("NOT SAVED")
        for problem in problems:
            print("  - " + problem)
        raise SystemExit(1)

    with open(OUTPUT, "w", encoding="utf-8") as file:
        json.dump({
            "description": "Evaluation questions for stage 6. Evidence quotes are verified "
                           "against data/processed_chunks.json by build_evaluation_questions.py.",
            "distribution": counts,
            "questions": QUESTIONS
        }, file, ensure_ascii=False, indent=2)

    print(f"{len(QUESTIONS)} questions verified and saved to {OUTPUT}")


if __name__ == "__main__":
    main()
