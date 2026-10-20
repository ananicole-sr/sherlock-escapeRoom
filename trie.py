# -------------------------------------------------------------------------
# TRIE (prefix tree) for the autocomplete of Watson's question box.
#
# Based on the implementation seen in class (TrieNode + insert, search and
# starts_with). It adds the operation the project needs: given a prefix,
# return the words of the vocabulary that start with it.
#
# Each word also stores a weight (the number of chunks where it appears),
# so the suggestions show the most useful words first.
#
# Complexity (L = length of a word, p = length of the prefix,
#             N = total characters inserted, k = nodes under the prefix):
#   insert(word)          O(L) time
#   search(word)          O(L) time
#   starts_with(prefix)   O(p) time
#   suggest(prefix)       O(p + k + m log m) time, m = words found
#   build from V words    O(N) time
#   storage               O(N) nodes in the worst case (no shared prefixes)
# -------------------------------------------------------------------------


class TrieNode:
    """
        Class that is used to represent a Trie node.
    """

    def __init__(self):
        """
            This constructor initializes a node.
        """
        self._children = {}         # Dictionary of children nodes.
        self._end_of_word = False   # Whether the node is the end of a word.
        self._weight = 0            # Importance of the word ending here.


class Trie:
    """
        Class that is used to represent a Trie.
    """

    def __init__(self):
        """
            This constructor initializes an empty Trie.
        """
        self._root = TrieNode()
        self._size = 0              # Number of different words stored.
        self._nodes = 1             # Number of nodes, counting the root.

    def insert(self, word, weight=1):
        """
            This method inserts a new word in the Trie. If the word already
            exists, its weight is added to the previous one.

            param word: The word to insert into the Trie.
            param weight: The importance of the word for the suggestions.
        """
        current = self._root

        for c in word:
            if c not in current._children:
                current._children[c] = TrieNode()
                self._nodes = self._nodes + 1

            current = current._children[c]

        if not current._end_of_word:
            self._size = self._size + 1

        current._end_of_word = True
        current._weight = current._weight + weight

    def _find_node(self, prefix):
        """
            This method walks the Trie following the prefix and returns the
            node where it ends, or None if the prefix is not in the Trie.
        """
        current = self._root

        for c in prefix:
            if c not in current._children:
                return None

            current = current._children[c]

        return current

    def search(self, word):
        """
            This method searches a complete word in the Trie.

            param word: The word to search in the Trie.
        """
        node = self._find_node(word)

        return node is not None and node._end_of_word

    def starts_with(self, prefix):
        """
            This method checks if any word of the Trie starts with the prefix.

            param prefix: The prefix to search in the Trie.
        """
        return self._find_node(prefix) is not None

    def words_with_prefix(self, prefix):
        """
            This method returns every word that starts with the prefix,
            together with its weight, as a list of (word, weight) tuples.
            The words come out in alphabetical order.

            param prefix: The prefix to search in the Trie.
        """
        node = self._find_node(prefix)

        if node is None:
            return []

        words = []
        self._collect(node, prefix, words)

        return words

    def _collect(self, node, path, words):
        """
            Depth-first traversal that gathers the words under a node.
        """
        if node._end_of_word:
            words.append((path, node._weight))

        for c in sorted(node._children):
            self._collect(node._children[c], path + c, words)

    def suggest(self, prefix, limit=5):
        """
            This method returns up to `limit` words that start with the
            prefix, ordered from the highest weight to the lowest. Words with
            the same weight are ordered alphabetically. The prefix itself is
            not suggested, because the user already wrote it.

            param prefix: The prefix written by the user.
            param limit: Maximum number of suggestions.
        """
        candidates = []

        for word, weight in self.words_with_prefix(prefix):
            if word != prefix:
                candidates.append((word, weight))

        candidates.sort(key=lambda item: (-item[1], item[0]))

        suggestions = []

        for word, weight in candidates[:limit]:
            suggestions.append(word)

        return suggestions

    def __len__(self):
        return self._size

    def node_count(self):
        return self._nodes
