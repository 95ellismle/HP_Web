def _create_trie(pc_dict):
    """Will create a trie with values that can be autocompleted in a text field"""
    root = {}
    for word in pc_dict:
        curr_dict = root

        for letter in word[:-1]:
            low_letter = letter.lower()
            curr_dict = curr_dict.setdefault(low_letter, {})
        letter = word[-1].lower()
        curr_dict[letter] = {0: None}

    return root

