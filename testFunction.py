from collections import defaultdict

def group_anagrams(words):
    """
    Groups a list of words into anagrams.

    Example:
    input: ["eat", "tea", "tan", "ate", "nat", "bat"]
    output: [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
    """

    anagram_map = defaultdict(list)

    for word in words:
        # Use sorted characters as the key
        key = tuple(sorted(word))
        anagram_map[key].append(word)

    return list(anagram_map.values())