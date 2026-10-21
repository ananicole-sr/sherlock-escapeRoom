
import re
import unicodedata

# Ligatures that NFKD does not decompose; without this, "Encyclopædia"
# became "encyclop dia" and never matched "encyclopaedia".
LIGATURES = {
    "æ": "ae",
    "œ": "oe",
    "ß": "ss"
}


def normalize_text(text):
    text = text.lower()

    for ligature, letters in LIGATURES.items():
        text = text.replace(ligature, letters)

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def tokenize(text):
    return normalize_text(text).split()
