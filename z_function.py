
def compute_z(s):
    n = len(s)
    z = [0] * n

    left = 0
    right = 0

    for i in range(1, n):

        if i <= right:
            z[i] = min(right - i + 1, z[i - left])

        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1

        if i + z[i] - 1 > right:
            left = i
            right = i + z[i] - 1

    return z


def z_search(text, pattern):
    if not pattern:
        return []

    separator = "\0"
    combined = pattern + separator + text

    z = compute_z(combined)

    positions = []
    offset = len(pattern) + 1

    for i in range(offset, len(combined)):
        if z[i] >= len(pattern):
            positions.append(i - offset)

    return positions


if __name__ == "__main__":

    text = "sherlock holmes examined the bell rope carefully"
    pattern = "bell"

    result = z_search(text, pattern)

    print("Z-FUNCTION STRING MATCHING")
    print("=" * 40)
    print(f"Text: {text}")
    print(f"Pattern: {pattern}")
    print(f"Matches found at positions: {result}")
