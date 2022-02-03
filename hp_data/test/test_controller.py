import os
import pytest
import pandas as pd

os.environ['DO_TEST'] = "True"
from hp_data.controller import DataController



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
    assert max(df['date_transfer']) == pd.to_datetime('2021/11/26', format='%Y/%m/%d')

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
    assert max(df['date_transfer']) == pd.to_datetime('2021/11/22', format='%Y/%m/%d')

    # Price filtering
    selectors['price_high'] = 4e5
    selectors['price_low'] = 3e5
    selectors.pop('city')
    cnt = DataController(selectors)
    all_df = cnt._read_data_files()
    df = pd.concat(cnt._select_data(*ret)[0] for ret in all_df)
    assert all(df['price'] >= 3e5)
    assert all(df['price'] <= 4e5)

