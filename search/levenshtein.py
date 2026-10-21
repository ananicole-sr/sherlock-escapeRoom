
def levenshtein_distance(word_a, word_b):
    n = len(word_a)
    m = len(word_b)

    table = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        table[i][0] = i

    for j in range(m + 1):
        table[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):

            if word_a[i - 1] == word_b[j - 1]:
                substitution_cost = 0
            else:
                substitution_cost = 1

            deletion = table[i - 1][j] + 1
            insertion = table[i][j - 1] + 1
            substitution = table[i - 1][j - 1] + substitution_cost

            table[i][j] = min(deletion, insertion, substitution)

    return table[n][m]


def levenshtein_distance_limited(word_a, word_b, max_distance):
    if abs(len(word_a) - len(word_b)) > max_distance:
        return max_distance + 1

    n = len(word_a)
    m = len(word_b)

    previous_row = list(range(m + 1))

    for i in range(1, n + 1):

        current_row = [i] + [0] * m
        row_minimum = i

        for j in range(1, m + 1):

            if word_a[i - 1] == word_b[j - 1]:
                substitution_cost = 0
            else:
                substitution_cost = 1

            deletion = previous_row[j] + 1
            insertion = current_row[j - 1] + 1
            substitution = previous_row[j - 1] + substitution_cost

            current_row[j] = min(deletion, insertion, substitution)

            if current_row[j] < row_minimum:
                row_minimum = current_row[j]

        if row_minimum > max_distance:
            return max_distance + 1

        previous_row = current_row

    return previous_row[m]


def common_prefix_length(word_a, word_b):
    length = 0

    while length < len(word_a) and length < len(word_b):
        if word_a[length] != word_b[length]:
            break
        length = length + 1

    return length


def closest_word(word, vocabulary, max_distance=2, document_frequency=None):
    best_word = None
    best_distance = max_distance + 1
    best_prefix = -1
    best_frequency = -1

    for candidate in vocabulary:

        if abs(len(candidate) - len(word)) > max_distance:
            continue

        distance = levenshtein_distance_limited(word, candidate, max_distance)

        if distance > max_distance:
            continue

        prefix = common_prefix_length(word, candidate)

        if document_frequency is None:
            frequency = 0
        else:
            frequency = document_frequency.get(candidate, 0)

        is_better = False

        if distance < best_distance:
            is_better = True
        elif distance == best_distance:
            if prefix > best_prefix:
                is_better = True
            elif prefix == best_prefix and frequency > best_frequency:
                is_better = True

        if is_better:
            best_distance = distance
            best_word = candidate
            best_prefix = prefix
            best_frequency = frequency

    if best_word is None:
        return None, max_distance + 1

    return best_word, best_distance


def main():
    print("\nSHERLOCK HOLMES - LEVENSHTEIN DISTANCE")
    print("=" * 50)

    test_pairs = [
        ("rope", "roap"),
        ("bell", "bel"),
        ("holmes", "holmes"),
        ("speckled", "spekled"),
        ("carbuncle", "carbunkle"),
        ("window", "widow"),
        ("goose", "geese"),
        ("kitten", "sitting")
    ]

    print(f"{'word A':<12} {'word B':<12} {'distance':>9}")
    print("-" * 35)

    for word_a, word_b in test_pairs:
        distance = levenshtein_distance(word_a, word_b)
        print(f"{word_a:<12} {word_b:<12} {distance:>9}")

    print("\nChecking that both versions agree:")

    all_equal = True

    for word_a, word_b in test_pairs:
        full = levenshtein_distance(word_a, word_b)
        limited = levenshtein_distance_limited(word_a, word_b, 10)

        if full != limited:
            all_equal = False
            print(f"  MISMATCH: {word_a} / {word_b}")

    if all_equal:
        print("  Both versions return the same distance.")


if __name__ == "__main__":
    main()
