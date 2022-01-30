import numpy as np
import os
import pytest
import pandas as pd

os.environ['DO_TEST'] = "True"
from hp_data.controller import DataController


#def test_get_data_files():
#    """Will test retrieval of data using the controller for various selectors"""
#    date1 = pd.to_datetime('2021/01/01', format='%Y/%m/%d')
#    date2 = pd.to_datetime('2022/01/01', format='%Y/%m/%d')
#    selectors = {'date_from': date1, 'date_to': date2}
#
#    # Just dates
#    cnt = DataController(selectors)
#    data_files = cnt._get_data_files()
#    assert [f'{i.parent.name}/{i.name}' for i in data_files] == ['2021/pp-2021.feather']
#
#    # Add a postcode
#    selectors['postcode'] = 'IG50QG'
#    cnt = DataController(selectors)
#    data_files = cnt._get_data_files()
#    test_files = [f'{i.parent.parent.name}/{i.parent.name}/{i.name}'
#                  for i in data_files]
#    assert test_files == ['2021/postcodes/I.feather']
#
#    selectors['postcode'] = 'TS285EF'
#    cnt = DataController(selectors)
#    data_files = cnt._get_data_files()
#    test_files = [f'{i.parent.parent.name}/{i.parent.name}/{i.name}'
#                  for i in data_files]
#    assert test_files == ['2021/postcodes/T.feather']
#
#    # Now test streets
#    selectors.pop('postcode')
#    selectors['street'] = 'Torquay Road'
#    cnt = DataController(selectors)
#    data_files = cnt._get_data_files()
#    ref_files = {f'2021/postcodes/{i}.feather' for i in ("S", "T", "C")}
#    test_files = {f'{i.parent.parent.name}/{i.parent.name}/{i.name}'
#                  for i in data_files}
#    assert test_files == ref_files
#
#    # Now test a combination of postcode and street
#    selectors['street'] = 'Mattock'
#    selectors['postcode'] = "S1"
#    cnt = DataController(selectors)
#    data_files = cnt._get_data_files()
#    ref_files = ['2021/postcodes/S.feather']
#    test_files = [f'{i.parent.parent.name}/{i.parent.name}/{i.name}'
#                  for i in data_files]
#    assert test_files == ref_files


def test_read_data_files():
    """Will test the read_data_files function works and it returns the correct columns/shape"""
    date1 = pd.to_datetime('2021/01/01', format='%Y/%m/%d')
    date2 = pd.to_datetime('2022/01/01', format='%Y/%m/%d')

    # Just dates
    selectors = {'date_from': date1, 'date_to': date2}
    cnt = DataController(selectors)
    cnt._data_files_to_read = cnt._read_data_files()
    dfs = cnt._read_data_files()
    assert len(list(dfs)) == 420

    # Dates and postcodes
    selectors = {'street': 'bob'}
    cnt = DataController(selectors)
    cnt._data_files_to_read = cnt._read_data_files()
    dfs = cnt._read_data_files()
    assert len(list(dfs)) == 300

    # Dates, postcode, prices,
    selectors = {'date_from': date1, 'date_to': date2, 'street': 'huck',
                 'price_low': 10, 'price_high': 100, 'flobba dobba do': 'daa'}
    cnt = DataController(selectors)
    cnt._data_files_to_read = cnt._read_data_files()
    dfs = cnt._read_data_files()
    assert len(list(dfs)) == 280


def test_select_data():
    """Test the selection of data using the controller"""
    date1 = pd.to_datetime('2021/11/01', format='%Y/%m/%d')
    date2 = pd.to_datetime('2021/11/29', format='%Y/%m/%d')

    # Datetime selection
    selectors = {'date_from': date1, 'date_to': date2}
    cnt = DataController(selectors)
    all_df = cnt._read_data_files()
    df = pd.concat(cnt._select_data(*ret)[0] for ret in all_df)
    assert min(df['date_transfer']) == date1
    assert max(df['date_transfer']) == date2

    # Postcode selection
    selectors['postcode'] = 'M345'
    selectors['date_from'] = pd.to_datetime('2021/02/04', format='%Y/%m/%d')
    cnt = DataController(selectors)
    all_df = cnt._read_data_files()
    df = pd.concat(cnt._select_data(*ret)[0] for ret in all_df)
    assert all(df['postcode'].str.slice(0, 4) == 'M345')
    assert min(df['date_transfer']) == pd.to_datetime('2021/02/04', format='%Y/%m/%d')
    assert max(df['date_transfer']) == pd.to_datetime('2021/11/15', format='%Y/%m/%d')

    # Street and city selection
    selectors.pop('postcode')
    selectors['city'] = 'Liverp'
    selectors['street'] = 'the'
    cnt = DataController(selectors)
    all_df = cnt._read_data_files()
    df = pd.concat(cnt._select_data(*ret)[0] for ret in all_df)
    assert all(df['street'].str.startswith('the'))
    assert all(df['city'].str.startswith('liverpool'))
    assert min(df['date_transfer']) == pd.to_datetime('2021/02/08', format='%Y/%m/%d')
    assert max(df['date_transfer']) == pd.to_datetime('2021/11/03', format='%Y/%m/%d')

    # Price filtering
    selectors['price_high'] = 4e5
    selectors['price_low'] = 3e5
    selectors.pop('city')
    cnt = DataController(selectors)
    all_df = cnt._read_data_files()
    df = pd.concat(cnt._select_data(*ret)[0] for ret in all_df)
    assert all(df['price'] >= 3e5)
    assert all(df['price'] <= 4e5)

