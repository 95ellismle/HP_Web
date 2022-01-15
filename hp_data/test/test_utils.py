import numpy as np
import pandas as pd
import time

from hp_data import utils


def test_binary_search():
    """Will test the binary search method"""
    arr = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    sort_order = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    ret = utils.binary_search(arr, sort_order, 5)
    assert ret == (5, 5)

    # Now test with a random array every time
    arr = np.random.random(size=100000)
    sort_order = sorted((val, i) for i, val in enumerate(arr))
    sort_order = [i[1] for i in sort_order]

    ret = utils.binary_search(arr, sort_order, arr[23728])

    for ind in [0, len(arr)-1] + ([np.random.randint(0, len(arr))] * 10):
        ret = utils.binary_search(arr, sort_order, arr[ind])
        assert ret[1] == ind
        assert arr[sort_order[ret[0]]] == arr[ind]


def test_create_trie():
    """Will test the creating a trie"""
    data = ['abba', 'babba', 'cabba', 'cab', 'bob',
            'arse', 'piff',  'tiff',  'bab', 'bairn']
    trie = utils.create_trie(data)
    assert trie == {'a': {'b': {'b': {'a': {0: None}}},
                          'r': {'s': {'e': {0: None}}}},
                    'b': {'a': {'b': {0: None,
                                      'b': {'a': {0: None}}},
                                'i': {'r': {'n': {0: None}}}},
                          'o': {'b': {0: None}}},
                    'c': {'a': {'b': {0: None,
                                      'b': {'a': {0: None}}}}},
                    'p': {'i': {'f': {'f': {0: None}}}},
                    't': {'i': {'f': {'f': {0: None}}}}
                   }

    data = {'stt': 'B!@879', 'sttt': "bOb", 'ttt': "BOT", 'tat': "BOB",
            'tst': "B0B", 'tas': "8O8"}
    trie = utils.create_trie(data)
    assert trie == {'s': {'t': {'t': {0: None,
                                      't': {0: None}}}},
                    't': {'t': {'t': {0: None}},
                          'a': {'t': {0: None},
                                's': {0: None}},
                          's': {'t': {0: None}}}}


def test_find_in_data():
    """Will test the finding of values in a sorted list"""
    # Test int array
    l = list(range(100)) + [100] * 10000 + list(range(100, 200))
    np.random.shuffle(l)
    s = sorted([(v, i) for i, v in enumerate(l)])
    df = pd.DataFrame({'a': l,
                       'sort_index': [i[1] for i in s]})

    ret = utils.find_in_data(df['a'].values,
                             df['sort_index'].values,
                             100)
    assert ret[0] == 100
    assert ret[1] == 10100

    # Test string array
    get_rand_char = lambda : 'abcdefghijklmnopqrstuvwxy'[np.random.randint(0, 25)]
    l = [''.join(get_rand_char() for j in range(7))
         for i in range(10000)]
    l += ['z' + ''.join(get_rand_char() for j in range(6))
          for i in range(10)]
    s = sorted([(v, i) for i, v in enumerate(l)])
    s = [i[1] for i in s]
    ind1, ind2 = utils.find_in_data(l, s, 'z')

    ref = set(l[-10:])
    assert {l[i] for i in s[ind1:ind2+1]} == ref

    # Test shuffled array
    np.random.shuffle(l)
    s = sorted([(v, i) for i, v in enumerate(l)])
    s = [i[1] for i in s]
    ind1, ind2 = utils.find_in_data(l, s, 'z')
    t2 = time.time()
    assert {l[i] for i in s[ind1:ind2+1]} == ref

