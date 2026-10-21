
def compute_lps(pattern):
    lps = [0] * len(pattern)

    length = 0
    i = 1

    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1

    return lps


def kmp_search(text, pattern):
    if not pattern:
        return []

    lps = compute_lps(pattern)

    positions = []
    i = 0 
    j = 0  

    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1

        if j == len(pattern):
            positions.append(i - j)
            j = lps[j - 1]

        elif i < len(text) and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    return positions


if __name__ == "__main__":
    text = "sherlock holmes examined the bell rope carefully"

    pattern = "bell"

    result = kmp_search(text, pattern)

    print("KMP STRING MATCHING")
    print("=" * 40)
    print(f"Text: {text}")
    print(f"Pattern: {pattern}")
    print(f"LPS array: {compute_lps(pattern)}")
    print(f"Matches found at positions: {result}")
