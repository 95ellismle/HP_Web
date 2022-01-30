import os
os.environ['DO_TEST'] = 'True'

import hp_data as hpd


def test_create_cache():
    """Will test the create cache function"""
    assert list(hpd.cache.keys()) == [2021]
    assert list(hpd.cache[2021].keys()) == ['A', 'B', 'C', 'D', 'E',
                                            'F', 'G', 'H', 'I', 'K',
                                            'L', 'M', 'N', 'O', 'P',
                                            'R', 'S', 'T', 'U', 'W',
                                            'Y']
    assert sorted(hpd.cache[2021]['A'].keys()) == [False, True]
    assert sorted(hpd.cache[2021]['C'][True].keys()) == ['Detached', 'Flat/Maisonette',
                                                         'Other', 'Semi-Detached',
                                                         'Terraced',]
    assert sorted(hpd.cache[2021]['O'][False]['Terraced']) == ['Freehold', 'Leasehold']


def test_yield_items():
    """Will test the yielding of items with an index from the cache"""
    # Single selections with a None
    ret = hpd.cache.yield_items([2021, 'F', False, 'Flat/Maisonette', None])
    ret = list(ret)
    assert len(ret) == 2
    assert ret[0][1] == [('is_new', False), ('dwelling_type', 'Flat/Maisonette'), ('tenure', 'Freehold')]
    assert ret[1][1] == [('is_new', False), ('dwelling_type', 'Flat/Maisonette'), ('tenure', 'Leasehold')]

    # 2 Nones
    ret = hpd.cache.yield_items([2021, 'F', False])
    ret = list(ret)
    assert len(ret) == 10

    # List selection
    ret = hpd.cache.yield_items([2021, 'F', [False, True]])
    ret = list(ret)
    assert len(ret) == 20
    ret = hpd.cache.yield_items([2021, 'F', [False], ['Terraced', 'Semi-Detached', 'Flat/Maisonette'], None])
    ret = list(ret)
    assert len(ret) == 6
    assert ret[0][1] == [('is_new', False), ('dwelling_type', 'Terraced'), ('tenure', 'Freehold')]
    assert ret[1][1] == [('is_new', False), ('dwelling_type', 'Terraced'), ('tenure', 'Leasehold')]
    assert ret[2][1] == [('is_new', False), ('dwelling_type', 'Semi-Detached'), ('tenure', 'Freehold')]
    assert ret[3][1] == [('is_new', False), ('dwelling_type', 'Semi-Detached'), ('tenure', 'Leasehold')]
    assert ret[4][1] == [('is_new', False), ('dwelling_type', 'Flat/Maisonette'), ('tenure', 'Freehold')]
    assert ret[5][1] == [('is_new', False), ('dwelling_type', 'Flat/Maisonette'), ('tenure', 'Leasehold')]

    # Real test
    ret = hpd.cache.yield_items([[2019, 2020, 2021], ('N',), None,
                                 ['Detached', 'Semi-Detached', 'Flat/Maisonette', 'Terraced'], 'freehold'])
    print(list(ret))


