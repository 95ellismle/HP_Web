# Public libraries
from data import path as data_dir
from pathlib import Path
from pyarrow import feather as ft

import time
import pandas as pd

# Libraries from this project
from data import path
from hp_data.exceptions import NoDataError

import hp_data as hpd
import hp_data.utils as ut


class DataController:
    """The controller that decides what data is passed to the frontend"""
    _loc_fields = {'street', 'postcode', 'city', 'county'}
    _full_data_dir = f'{data_dir}/$<year>'
    _pc_dir = f'{_full_data_dir}/postcodes'

    def __init__(self, selectors):
        self._start_time = time.time()
        self._selectors = selectors

        self._data_files_to_read = self._get_data_files()
        t1 = time.time()

        all_df = self._read_data_files()
        t2 = time.time()

        self.data = pd.concat(self._select_data(df) for df in all_df)
        self._end_time = time.time()

        print(f"Time Taken for file find: {t1 - self._start_time}")
        print(f"Time Taken for file read: {t2 - t1}")
        print(f"Time Taken for data splice: {self._end_time - t2}")

    def _select_data(self, df):
        """Will select the relevant data from the data files."""
        t1 = time.time()
        min_ind, max_ind = self._datetime_selection(df)
        inds = set(range(min_ind, max_ind))
        print(f'DateTime: {time.time() - t1}')

        is_contig = True

        # Handle postcode
        t1 = time.time()
        postcode = self._selectors.get('postcode', '')
        for col in ('street', 'city', 'county', 'postcode'):
            selector_val = self._selectors.get(col, '')
            if len(selector_val) > 1:
                so = df[f'{col}_sort_index'].values
                first_ind, last_ind = ut.find_in_data(df[col].values,
                                                      so,
                                                      selector_val)
                is_contig *= (first_ind != 0) and (last_ind != len(df)-1)
                print(first_ind, last_ind)
                if not is_contig:
                    inds.intersection({so[i] for i in range(first_ind, last_ind+1)})
        print(f"Location: {time.time() - t1}")

        # New build
        t1 = time.time()
        if 'is_new' in self._selectors:
            df = df.dropna(axis=0, subset=['is_new'])
            assert len(self._selectors['is_new']) == 1
            if self._selectors['is_new'][0] == 'is_new':
                df = df[df['is_new']]
            else:
                df = df[~df['is_new']]
        print(f'Is New: {time.time() - t1}')

        # Freehold vs Leasehold
        t1 = time.time()
        if 'tenure' in self._selectors:
            df = df.dropna(axis=0, subset=['tenure'])
            assert len(self._selectors['tenure']) == 1
            df = df[df['tenure'] == self._selectors['tenure'][0]]
        print(f'Tenure: {time.time() - t1}')

        # Price
        t1 = time.time()
        if 'price_high' in self._selectors:
            df = df[df['price'] <= self._selectors['price_high']/1000.]
        if 'price_low' in self._selectors:
            df = df[df['price'] >= self._selectors['price_low']/1000.]
        print(f'Price: {time.time() - t1}')

        t1 = time.time()
        if is_contig:
            df = df.iloc[min_ind: max_ind]
        else:
            df = df.iloc[list(inds)]
        print(f'Splicing: {time.time() - t1}')
        return df

    def _datetime_selection(self, df):
        """Will splice the data by the requested datetime.

        Because the data is sorted by date this uses a binary search.
        """
        # Now mask by date -data is sorted by date
        min_d = self._selectors.get('date_from')
        max_d = self._selectors.get('date_to')

        first_ind = 0
        if 'date_from' in self._selectors:
            first_ind = df['date_transfer'].searchsorted(min_d, side='left')
        last_ind = len(df)
        if 'date_to' in self._selectors:
            last_ind = df['date_transfer'].searchsorted(max_d, side='right')

        return first_ind, last_ind

    def _splice_with_sort_index(self, df, col, min_=None, max_=None):
        """"""


    def _get_data_files(self):
        """Will find which data files to read"""
        min_year = self._selectors.get('date_from',
                                       hpd.DATA_STATS['min_date']).year
        max_year = self._selectors.get('date_to',
                                       hpd.DATA_STATS['max_date']).year
        years_to_read = list(range(min_year, max_year+1))

        # Get data from the postcode files
        if any(i in self._selectors for i in self._loc_fields):
            data_filenames = self._get_loc_files(years_to_read)

        # Read the standard feather files
        else:
            data_filenames = [Path(self._full_data_dir.replace('$<year>', str(y))) / f'pp-{y}.feather'
                              for y in years_to_read]

        return [i for i in data_filenames if i.is_file()]

    def _read_data_files(self):
        """Will read all data files as a dataframe via 'read_dataset' from pyarrow"""
        cols = ['price', 'date_transfer', 'postcode', 'dwelling_type', 'is_new',
                'tenure', 'paon', 'street', 'city', 'county']

        excluders = {'date_from', 'date_to', 'price_high', 'price_low'}
        for sel in self._selectors:
            if sel not in excluders:
                cols += [f'{sel}_sort_index']
        if 'price_low' in self._selectors or 'price_high' in self._selectors:
            cols += ['price_sort_index']

        df = [ft.FeatherDataset([fn]).read_pandas(columns=cols)
              for fn in self._data_files_to_read]

        return df

    def _get_loc_files(self, years_to_read: list):
        """Get the data from the postcode files.

        Args:
            years_to_read: a list of year numbers to read
        """
        years_to_read = list(map(str, years_to_read))

        # Get relevant postcodes
        pcs = set()
        if 'postcode' in self._selectors:
            pcs = {self._selectors['postcode'][0].upper()}

        # Narrow down by street, city and county -if we don't have a postcode
        if not pcs:
            maps = {'city': hpd.city_map, 'street': hpd.streets_map,
                    'county': hpd.county_map}
            for loc in maps:
                if loc in self._selectors:
                    map_ = maps[loc]
                    loc_selector = self._selectors[loc].title()
                    keys = {i for i in map_ if i.startswith(loc_selector)}
                    new_pcs = {j for i in keys for j in map_[i]}
                    if len(pcs) == 0:
                        pcs = new_pcs
                    else:
                        pcs = pcs.intersection(new_pcs)
                        if len(pcs) == 0:
                            raise NoDataError("No data for that selection")

        # Construct the filenames
        fns = []
        for year in years_to_read:
            for pc in pcs:
                dir_name = Path(self._pc_dir.replace('$<year>', year))
                fns.append(dir_name / f'{pc[0].upper()}.feather')

        # Return if they exist
        return [fn for fn in fns if fn.is_file()]

