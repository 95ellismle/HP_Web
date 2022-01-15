import pytest
import pandas as pd
import numpy as np

from hp_data import controller


class InertController(controller.DataController):
    """This class is a copy of the DataController, except any __init__ code doesn't run.
    This allow a class to be created and instantiated without reading data etc...
    """
    def __init__(self, selectors):
        self._selectors = selectors


def test_get_data_files():
    """Will test retrieval of data using the controller for various selectors"""
    date1 = pd.to_datetime('2021/01/01', format='%Y/%m/%d')
    date2 = pd.to_datetime('2022/01/01', format='%Y/%m/%d')
    selectors = {'date_from': date1, 'date_to': date2}

    # Just dates
    cnt = InertController(selectors)
    data_files = cnt._get_data_files()
    assert [f'{i.parent.name}/{i.name}' for i in data_files] == ['2021/pp-2021.feather']

    # Add a postcode
    selectors['postcode'] = 'IG50QG'
    cnt = InertController(selectors)
    data_files = cnt._get_data_files()
    test_files = [f'{i.parent.parent.name}/{i.parent.name}/{i.name}'
                  for i in data_files]
    assert test_files == ['2021/postcodes/I.feather']

    selectors['postcode'] = 'TS285EF'
    cnt = InertController(selectors)
    data_files = cnt._get_data_files()
    test_files = [f'{i.parent.parent.name}/{i.parent.name}/{i.name}'
                  for i in data_files]
    assert test_files == ['2021/postcodes/T.feather']

    # Now test streets
    selectors.pop('postcode')
    selectors['street'] = 'Torquay Road'
    cnt = InertController(selectors)
    data_files = cnt._get_data_files()
    ref_files = {f'2021/postcodes/{i}.feather' for i in ("S", "T", "C")}
    test_files = {f'{i.parent.parent.name}/{i.parent.name}/{i.name}'
                  for i in data_files}
    assert test_files == ref_files

    # Now test a combination of postcode and street
    selectors['street'] = 'Mattock'
    selectors['postcode'] = "S1"
    cnt = InertController(selectors)
    data_files = cnt._get_data_files()
    ref_files = ['2021/postcodes/S.feather']
    test_files = [f'{i.parent.parent.name}/{i.parent.name}/{i.name}'
                  for i in data_files]
    assert test_files == ref_files


def test_read_data_files():
    """Will test the read_data_files function works and it returns the correct columns/shape"""
    date1 = pd.to_datetime('2021/01/01', format='%Y/%m/%d')
    date2 = pd.to_datetime('2022/01/01', format='%Y/%m/%d')
    selectors = {'date_from': date1, 'date_to': date2}
    root_cols = {'price', 'date_transfer', 'postcode', 'dwelling_type', 'is_new',
                 'tenure', 'paon', 'street', 'city', 'county'}

    # Just dates
    cnt = InertController(selectors)
    cnt._data_files_to_read = cnt._get_data_files()
    dfs = cnt._read_data_files()
    assert len(dfs) == 1
    assert set(dfs[0].columns) == root_cols

    # Now add a street and reduce the date
    selectors['date_from'] = pd.to_datetime('2019/12/01')
    selectors['postcode'] = 'AL16'
    cnt._data_files_to_read = cnt._get_data_files()
    dfs = cnt._read_data_files()
    assert len(dfs) == 3
    cols = root_cols.copy()
    cols.add('postcode_sort_index')
    assert all(set(i.columns) == cols for i in dfs)

    # Add various other selectors
    selectors['postcode'] = 'HU1'
    selectors['dwelling_type'] = ['Flat/Maisonette', 'Detatched']
    selectors['city'] = ['Hull']
    selectors['price_low'] = 1e5
    selectors['street'] = 'Lacemakers'
    cnt._data_files_to_read = cnt._get_data_files()
    dfs = cnt._read_data_files()
    assert len(dfs) == 3
    cols.add('dwelling_type_sort_index')
    cols.add('price_sort_index')
    cols.add('city_sort_index')
    cols.add('street_sort_index')
    assert all(set(i.columns) == cols for i in dfs)


def test_select_data():
    """Test the selection of data using the controller"""
    date1 = pd.to_datetime('2019/11/01', format='%Y/%m/%d')
    date2 = pd.to_datetime('2019/12/01', format='%Y/%m/%d')
    selectors = {'date_from': date1, 'date_to': date2}

    # Datetime selection
    cnt = InertController(selectors)
    cnt._data_files_to_read = cnt._get_data_files()
    all_df = cnt._read_data_files()
    df = pd.concat(cnt._select_data(df) for df in all_df)
    assert min(df['date_transfer']) == date1
    assert max(df['date_transfer']) == date2

    # Postcode selection
    selectors['postcode'] = 'M345'
    selectors['date_from'] = pd.to_datetime('2019/01/01', format='%Y/%m/%d')
    cnt = InertController(selectors)
    cnt._data_files_to_read = cnt._get_data_files()
    all_df = cnt._read_data_files()
    df = pd.concat(cnt._select_data(df) for df in all_df)
    #print(df)
