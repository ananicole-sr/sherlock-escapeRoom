
# -------------------------------------------------------------------------
# QUERY PREPROCESSING shared by the exact (KMP / Z-function) and the
# approximate (Levenshtein + Jaccard) search engines, so both compare the
# same terms. Spelling correction is NOT done here: it belongs only to the
# approximate strategy (approximate_search.correct_query_terms).
#
# Steps:
#   1. Remove the possessive "'s" ("Peterson's" -> "Peterson"). The
#      normalizer turns apostrophes into spaces, so without this step the
#      query would contain the meaningless term "s".
#   2. Normalize with the same function used for the documents (lowercase,
#      accents removed, punctuation removed).
#   3. Tokenize, drop stopwords and one-character tokens, and keep each
#      term once, in the order it appears.
# -------------------------------------------------------------------------

import re

from search.text_cleaner import normalize_text

STOPWORDS = {
    "a", "about", "all", "an", "and", "any", "are", "as", "at", "be", "been",
    "but", "by", "can", "did", "do", "does", "for", "from", "had", "has",
    "have", "he", "her", "him", "his", "how", "i", "if", "in", "into", "is",
    "it", "its", "me", "my", "no", "not", "of", "on", "or", "our", "out",
    "she", "so", "some", "such", "than", "that", "the", "their", "them",
    "then", "there", "these", "they", "this", "to", "too", "up", "was",
    "we", "were", "what", "when", "where", "which", "who", "why", "will",
    "with", "would", "you", "your"
}

# "'s" or "’s" right after a word character and at the end of the word.
POSSESSIVE = re.compile(r"(?<=\w)['’]s\b", re.IGNORECASE)

MIN_TERM_LENGTH = 2


def remove_possessives(text):
    return POSSESSIVE.sub("", text)


def normalize_query(question):
    return normalize_text(remove_possessives(question))


def extract_query_terms(question):
    """
        Returns the important terms of a question, without repetitions and
        in their original order.
    """
    terms = []
    seen = set()

    for token in normalize_query(question).split():
        if token in STOPWORDS or len(token) < MIN_TERM_LENGTH or token in seen:
            continue

        terms.append(token)
        seen.add(token)

    return terms


if __name__ == "__main__":
    for question in ["Where did Peterson's wife find the blue stone?",
                     "What was in Dr. Roylott’s room?",
                     "Why did Holmes' client copy the Encyclopaedia?"]:
        print(f"{question!r} -> {extract_query_terms(question)}")
