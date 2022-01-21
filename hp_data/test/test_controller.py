import numpy as np
import os
import pytest
import pandas as pd

os.environ['DO_TEST'] = "True"
from hp_data.controller import DataController


def test_get_data_files():
    """Will test retrieval of data using the controller for various selectors"""
    date1 = pd.to_datetime('2021/01/01', format='%Y/%m/%d')
    date2 = pd.to_datetime('2022/01/01', format='%Y/%m/%d')
    selectors = {'date_from': date1, 'date_to': date2}

    # Just dates
    cnt = DataController(selectors)
    data_files = cnt._get_data_files()
    assert [f'{i.parent.name}/{i.name}' for i in data_files] == ['2021/pp-2021.feather']

    # Add a postcode
    selectors['postcode'] = 'IG50QG'
    cnt = DataController(selectors)
    data_files = cnt._get_data_files()
    test_files = [f'{i.parent.parent.name}/{i.parent.name}/{i.name}'
                  for i in data_files]
    assert test_files == ['2021/postcodes/I.feather']

    selectors['postcode'] = 'TS285EF'
    cnt = DataController(selectors)
    data_files = cnt._get_data_files()
    test_files = [f'{i.parent.parent.name}/{i.parent.name}/{i.name}'
                  for i in data_files]
    assert test_files == ['2021/postcodes/T.feather']

    # Now test streets
    selectors.pop('postcode')
    selectors['street'] = 'Torquay Road'
    cnt = DataController(selectors)
    data_files = cnt._get_data_files()
    ref_files = {f'2021/postcodes/{i}.feather' for i in ("S", "T", "C")}
    test_files = {f'{i.parent.parent.name}/{i.parent.name}/{i.name}'
                  for i in data_files}
    assert test_files == ref_files

    # Now test a combination of postcode and street
    selectors['street'] = 'Mattock'
    selectors['postcode'] = "S1"
    cnt = DataController(selectors)
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
    cnt = DataController(selectors)
    cnt._data_files_to_read = cnt._get_data_files()
    dfs = cnt._read_data_files()
    assert len(dfs) == 1
    assert set(dfs[0].columns) == root_cols

    # Now add a street and reduce the date
    selectors['date_from'] = pd.to_datetime('2019/12/01')
    selectors['postcode'] = 'AL16'
    cnt._set_years_to_get()  # Reset the years to get based on the selectors
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
    cnt = DataController(selectors)
    cnt._data_files_to_read = cnt._get_data_files()
    all_df = cnt._read_data_files()
    df = pd.concat(cnt._select_data(df) for df in all_df)
    assert min(df['date_transfer']) == date1
    assert max(df['date_transfer']) == date2
    print()

    # Postcode selection
    selectors['postcode'] = 'M345'
    selectors['date_from'] = pd.to_datetime('2019/02/01', format='%Y/%m/%d')
    cnt = DataController(selectors)
    cnt._data_files_to_read = cnt._get_data_files()
    all_df = cnt._read_data_files()
    df = pd.concat(cnt._select_data(df) for df in all_df)
    assert all(df['postcode'].str.slice(0, 4) == 'M345')
    assert min(df['date_transfer']) == pd.to_datetime('2019/02/01', format='%Y/%m/%d')
    assert max(df['date_transfer']) == pd.to_datetime('2019/11/29', format='%Y/%m/%d')
    print()

    # Street and city selection
    selectors.pop('postcode')
    selectors['city'] = 'Liverp'
    selectors['street'] = 'the'
    cnt = DataController(selectors)
    cnt._data_files_to_read = cnt._get_data_files()
    all_df = cnt._read_data_files()
    df = pd.concat(cnt._select_data(df) for df in all_df)
    assert all(df['street'].str.startswith('The'))
    assert all(df['city'].str.startswith('Liverpool'))
    assert min(df['date_transfer']) == pd.to_datetime('2019/02/01', format='%Y/%m/%d')
    assert max(df['date_transfer']) == pd.to_datetime('2019/11/29', format='%Y/%m/%d')

    # New build
    print()
    selectors.pop('city')
    selectors.pop('street')
    selectors['is_new'] = True
    selectors['date_from'] = pd.to_datetime('2019/01/01', format='%Y/%m/%d')
    selectors['date_to'] = pd.to_datetime('2019/12/31', format='%Y/%m/%d')
    cnt = DataController(selectors)
    cnt._data_files_to_read = cnt._get_data_files()
    all_df = cnt._read_data_files()
    ref_df = all_df[0].loc[all_df[0]['is_new'], 'is_new']
    df = pd.concat(cnt._select_data(df) for df in all_df)
    assert all(df['is_new'])
    assert len(df) == len(ref_df)

    # Tenure
    print()
    selectors.pop('is_new')
    selectors['tenure'] = 'freehold'
    selectors['city'] = 'derby'
    cnt = DataController(selectors)
    cnt._data_files_to_read = cnt._get_data_files()
    all_df = cnt._read_data_files()
    df = pd.concat(cnt._select_data(df) for df in all_df)
    ref_df = all_df[1] if all_df[1].loc[0, 'postcode'].startswith('D') else all_df[0]
    ref_df = ref_df.loc[(ref_df['tenure'] == 'Freehold')
                        & (ref_df['city'] == 'Derby'), 'tenure']
    assert all(df['tenure'] == 'Freehold')
    assert len(ref_df) == len(df)

    # Dwelling type
    print()
    selectors['dwelling_type'] = ['Detached', 'seMi-deta', 'flat/maisonette']
    selectors['city'] = 'derby'
    cnt = DataController(selectors)
    cnt._data_files_to_read = cnt._get_data_files()
    all_df = cnt._read_data_files()
    df = pd.concat(cnt._select_data(df) for df in all_df)
    assert all(df['city'].unique() == 'Derby')
    assert set(df['dwelling_type'].unique()) == {'Detached', 'Semi-Detached', 'Flat/Maisonette'}

    # Price filtering
    print()
    selectors['price_high'] = 4e5
    selectors['price_low'] = 3e5
    selectors.pop('dwelling_type')
    selectors.pop('city')
    cnt = DataController(selectors)
    cnt._data_files_to_read = cnt._get_data_files()
    all_df = cnt._read_data_files()
    df = pd.concat(cnt._select_data(df) for df in all_df)
    assert all(df['price'] >= 3e5)
    assert all(df['price'] <= 4e5)

