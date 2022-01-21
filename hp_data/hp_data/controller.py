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

    def __init__(self, selectors, cols_to_display=None):
        self._start_time = time.time()
        self._selectors = selectors
        self._set_years_to_get()
        self._cols_to_display = cols_to_display

    def read_data(self):
        """Will read the data"""
        self._data_files_to_read = self._get_data_files()
        t1 = time.time()

        all_df = self._read_data_files()
        t2 = time.time()

        try:
            self.data = pd.concat(self._select_data(df) for df in all_df)
        except ValueError:
            raise NoDataError("No data for that selection")
        if len(self.data) == 0:
            raise NoDataError("No data for that selection")
        self._end_time = time.time()

        print(f"Time Taken for file find: {t1 - self._start_time}")
        print(f"Time Taken for file read: {t2 - t1}")
        print(f"Time Taken for data splice: {self._end_time - t2}")

    def _set_years_to_get(self):
        """Will set which years to read from files and which to get from the cache

        Sets the attributes:
            - self._years_to_get
            - self._years_to_read
            - self._years_from_cache
        """
        min_year = self._selectors.get('date_from',
                                       hpd.DATA_STATS['min_date']).year
        max_year = self._selectors.get('date_to',
                                       hpd.DATA_STATS['max_date']).year

        self._years_to_get = set(range(min_year, max_year+1))
        self._years_to_read = self._years_to_get - set(hpd.CACHE_DATA.keys())
        self._years_to_read = tuple(sorted(self._years_to_read))
        self._years_from_cache = tuple(self._years_to_get.intersection(hpd.CACHE_DATA.keys()))
        self._years_from_cache = tuple(sorted(self._years_from_cache))

    def _select_data(self, df):
        """Will select the relevant data from the data files."""
        t1 = time.time()
        min_ind, max_ind = self._datetime_selection(df)
        inds = set(range(min_ind, max_ind))
        selection_timings = {'datetime': time.time() - t1}

        just_dt = True

        # Handle price
        if 'price_low' in self._selectors or 'price_high' in self._selectors:
            t1 = time.time()
            just_dt = False

            price_low = df.loc[df['price_sort_index'].values[0], 'price']
            price_high = df.loc[df['price_sort_index'].values[-1], 'price']
            if 'price_low' in self._selectors:
                price_low = self._selectors['price_low']
            if 'price_high' in self._selectors:
                price_high = self._selectors['price_high']
            so = df[f'price_sort_index'].values

            first_ind = ut.find_end(df['price'].values, so,
                                    price_low, 'first')
            last_ind = ut.find_end(df['price'].values, so,
                                   price_high, 'last', first_ind)
            inds = inds.intersection(set(so[first_ind:last_ind+1]))
            selection_timings['price'] = time.time() - t1

        # Handle single selections
        for col in ('street', 'city', 'county', 'postcode', 'is_new', 'tenure'):
            t1 = time.time()
            inds, changed = self._select_from_1_col(df, col, inds)
            if changed:
                selection_timings[col] = time.time() - t1
                just_dt = False

        # Handle multiple selections from the same selector
        for col in ('dwelling_type', ):
            t1 = time.time()
            selector_vals = self._selectors.get(col, [])
            if not selector_vals:
                continue

            so = df[f'{col}_sort_index'].values
            new_inds = []
            for val in selector_vals:
                if isinstance(val, str) and len(val) < 2:
                    continue
                just_dt = False
                so = df[f'{col}_sort_index'].values
                first_ind, last_ind = ut.find_in_data(df[col].values, so, val)
                if first_ind != last_ind:
                    new_inds.extend(so[first_ind: last_ind])
            inds = inds.intersection(new_inds)
            selection_timings[col] = time.time() - t1

        # Indexing the data to return
        t1 = time.time()
        if just_dt:
            df = df.iloc[min_ind:max_ind]
        else:
            df = df.iloc[sorted(inds)]
        selection_timings['splicing'] = time.time() - t1

        # Print timings for each selection
        print("Time take to select:")
        for i in selection_timings:
            print(f"    - '{i}': {selection_timings[i]:.3f}")

        if self._cols_to_display:
            return df.loc[:, self._cols_to_display]
        else:
            return df

    def _select_from_1_col(self, df, col, inds):
        """Will select return the start and end indices of search val from the sort index.

        The _selectors attribute will be used to determine what to search for.

        Args:
            df: DataFrame to search in
            col: Name of the col to search in
            inds: Indices to edit to contain all values with the search value

        Returns:
            set<int>: The indices within the dataframe where the value appears
        """
        selector_val = self._selectors.get(col)

        if isinstance(selector_val, str) and len(selector_val) < 2:
            return inds, False
        if selector_val is None:
            return inds, False

        just_dt = False
        so = df[f'{col}_sort_index'].values
        first_ind, last_ind = ut.find_in_data(df[col].values,
                                              so,
                                              selector_val)
        if first_ind == last_ind:
            return set(), True

        return inds.intersection(so[first_ind:last_ind+1]), True

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

    def _get_data_files(self):
        """Will find which data files to read"""

        # Get data from the postcode files
        if any(i in self._selectors for i in self._loc_fields):
            data_filenames = self._get_loc_files()

        # Read the standard feather files
        else:
            data_filenames = [Path(self._full_data_dir.replace('$<year>', str(y))) / f'pp-{y}.feather'
                              for y in self._years_to_read]

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

        all_df = [ft.FeatherDataset([fn]).read_pandas(columns=cols)
              for fn in self._data_files_to_read]
        for yr in self._years_from_cache:
            all_df.append(hpd.CACHE_DATA[yr])

        return all_df

    def _get_loc_files(self):
        """Get the data from the postcode files.

        Args:
            years_to_read: a list of year numbers to read
        """
        years_to_read = list(map(str, self._years_to_read))

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

