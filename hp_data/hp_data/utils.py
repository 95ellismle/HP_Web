import numpy as np
import pandas as pd


def create_trie(data):
    """Will create a trie with values that can be autocompleted in a text field.

    The trie will terminate with {0: None}.

    Args:
        data: The data that will be iterated over to create the trie
    """
    root = {}
    for word in data:
        if not word:
            continue
        curr_dict = root
        for letter in word[:-1]:
            low_letter = letter.lower()
            curr_dict = curr_dict.setdefault(low_letter, {})
        letter = word[-1].lower()
        if letter in curr_dict:
            curr_dict[letter][0]  = None
        else:
            curr_dict[letter] = {0: None}

    return root


def binary_search(data, sort_order, search_val):
    """Will perform a binary search to find an element in a sorted data structure.

    Will return the index of the value within the data array.

    Args:
        data: Data container (made primarily for pandas.Series)
        sort_order: The order of the elements
        search_val: The value to search for

    Returns:
        (int, int) the index in the sort array, the index in the data array
    """
    low = 0
    upp = len(data)
    if search_val <= data[sort_order[low]]:
        return low, sort_order[low]
    elif search_val >= data[sort_order[upp-1]]:
        return upp - 1, sort_order[upp - 1]

    # Do binary search
    while True:
        # Only gap of 1
        if upp - low == 1:
            upp_ = sort_order[upp]
            low_ = sort_order[low]
            if isinstance(search_val, str):
                return (upp, upp_)

            h = abs(data[upp_] - search_val)
            l = abs(data[low_] - search_val)
            return (upp, upp_) if h <= l else (low, low_)

        mid_ind = (upp + low) // 2
        mid_val = data[sort_order[mid_ind]]

        if mid_val == search_val:
            return mid_ind, sort_order[mid_ind]

        elif mid_val < search_val:
            low = mid_ind
        else:
            upp = mid_ind


def get_contiguous_sorted_intersection(A, B):
    """Get the intersection of 1 sorted, unique arrays.

    Args:
        A: array 1
        B: array 2

    Returns:
        intersection assuming both arrays are unique and sorted
    """
    if len(A) > len(B):
        return np.searchsorted(A, B)

    return np.searchsorted(B, A)


def _get_in_sorted_df(self, df, col, sort_col, val):
    """Will find a value within a DataFrame via binary search and it's sort_index

    Args:
        df: The dataframe to search in
        col: The column to search for
        sort_col: The sort order
        val: The thing to search for

    Returns:
        An list of indices where the value appears in the dataframe
    """
    data = df[col].values
    sort_order = df[sort_col].values


def find_end(data, sort_order, val, first_or_last='first', init_low=None, init_upp=None):
    """Will find the first occurance of a value within a sorted list

    If the array is an array of strings then the beginnings of the
    strings will be compared.

    Args:
        data: the list
        sort_order: indices giving the order of the list
        val: the values to find
        first_or_last: find the first or last occurance
        init_low: a lower bound on the search
        init_high: an upper bound on the search

    Returns:

    """
    assert first_or_last in {'first', 'last'}, "Please choose 'first' or 'last' as the end"
    assert len(data) == len(sort_order), "Sort order must be the same length as data"
    low = 0 if init_low is None else init_low
    upp = len(data) - 1 if init_upp is None else init_upp

    # Some extra handling for strings
    is_str = isinstance(val, str)
    if is_str:
        len_str = len(val)
        val = val.lower()

    do_first = first_or_last == 'first'
    direction = -1 if do_first else 1

    # Bounds checking
    if do_first:
        new_val = data[sort_order[low]]
        if is_str:
            new_val = new_val[:len_str].lower()
        if new_val == val:
            return low
    else:
        new_val = data[sort_order[upp]]
        if is_str:
            new_val = new_val[:len_str].lower()
        if new_val == val:
            return upp

    prev_mid = None
    #print("\n\n\n")
    #print("upp    low    mid    new_val val")
    #new_val = ''
    #mid = ''
    while True:
        # First get the new value
        #print(''.join([str(i).ljust(7) for i in (upp, low, mid, new_val, val)]))
        mid = (upp + low) // 2
        if mid == prev_mid:
            return mid

        new_val = data[sort_order[mid]]
        #print(''.join([str(i).ljust(7) for i in (upp, low, mid, new_val, val)]))
        new_val_m = data[sort_order[mid + direction]]
        if is_str:
            new_val = new_val[:len_str].lower()
            new_val_m = new_val_m[:len_str].lower()

        # Check if we should keep going
        # Find the first element
        if do_first:
            if mid == 0 or (val > new_val_m and new_val == val) or mid == len(data) -1:
                return mid
            # Decide where to look next time
            elif new_val < val:
                low = mid
            else:
                upp = mid

        # Find the last element
        else:
            if mid == 0 or (val < new_val_m and new_val == val) or mid == len(data) -1:
                return mid
            # Decide where to look next time
            elif new_val <= val:
                low = mid
            else:
                upp = mid

        prev_mid = mid



def find_in_data(data, sort_order, val):
    """Will find the start and end of a set of values within a (sorted) list.

    E.g. if a list looks like: [1, 3, 4, 5, 6, 6, 6, 7, 8]
         and 6 was looked for the return value would be:
           [4, 5, 6]

    Args:
        data: the data to search in
        sort_order: the ordering for the data array
        val: the value to search for

    Returns:
        inds of all occurances of the value
    """
    first_ind = find_end(data, sort_order, val)
    last_ind = find_end(data, sort_order, val, "last",
                        init_low=first_ind)

    return first_ind, last_ind


def huffman(arr):
    """Returns a huffman encoding of the array.

    Args:
        arr: the array that should be huffman encoded
    Returns:
        list(list()) [[val, num_vals], [val1, num_val1], ...]
    """
    if len(arr) == 0:
        return tuple()
    changes = arr[:-1] != arr[1:]
    inds = np.arange(1, len(arr))[changes]
    if len(inds) == 0:
        return ((arr[0], len(arr)),)

    inds = np.insert(inds, 0, 0)
    lens_ = np.insert(np.diff(inds), len(inds)-1, len(arr) - inds[-1])
    return tuple(zip(arr[inds], map(int, lens_)))

