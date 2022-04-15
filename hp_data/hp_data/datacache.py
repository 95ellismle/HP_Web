"""Will store the datacache object. This stores the data in a very searchable way -hopefully speeding up the app"""
from concurrent.futures import ThreadPoolExecutor
import logging
import sys
from pathlib import Path
from pyarrow import feather as ft

from data import path as dt_path
import hp_config as hpc


class DataCache(dict):
    """Stores all the data in a nested dict to make data easily searchable.

    self = {year1:
                 {postcode1:
                          {is_new:
                                 {
                                  dwelling_type1:  {
                                                    freehold: DataFrame,
                                                    leasehold: DataFrame
                                                    }
                                  dwelling_type2: ...
                                 },
                          not_new: ...
                          },
                postcode2: ...
                },
            year2: ...
           }

    """
    _cols_to_read = ['price', 'date_transfer', 'postcode', 'dwelling_type', 'is_new',
                    'tenure', 'paon', 'street', 'city', 'county', 'postcode_sort_index',
                    'price_sort_index', 'street_sort_index',
                    'city_sort_index', 'county_sort_index']
    _column_names = {2: 'is_new', 3: 'dwelling_type', 4: 'tenure'}
    _mem_usage = 0

    def __init__(self, cache_years=None, *args, **kwargs):
        self._cache_years = cache_years
        self._create_cache()
        super().__init__(*args, **kwargs)

    def _add_cache_year(self, year):
        """Will add a single year to the cache"""
        data = self.setdefault(int(year.stem), {})

        for fp in sorted(year.glob('postcodes/*.feather')):
            splitter = fp.stem.split('_')
            pc = splitter[0]
            for i in splitter[1:]:
                v = i.upper()
                if v.startswith('IN'):
                    is_new = bool(int(i[-1]))
                elif v.startswith('DT'):
                    dwelling_type = self.rev_dt[int(i[2:])]
                elif v.startswith('TN'):
                    tenure = self.rev_tn[int(i[2:])]
            try:
                d = data.setdefault(pc, {}).setdefault(is_new, {}).setdefault(dwelling_type, {})
                d[tenure] = ft.FeatherDataset([fp]).read_pandas()
                self._mem_usage += d[tenure].memory_usage().sum() / 1048576
            except NameError:
                raise SystemExit(f"Filename corrupt: {i}")

        print(self)
        print(f'Read cache year: {year}')

    def _create_cache(self):
        """Will iterate over all files in the data directory and load them into the cache.
        This will create the data structure as seen in the docstr.
        """
        cache_years = sorted(dt_path.glob('????'))
        if self._cache_years is not None:
            self._cache_years = set(self._cache_years)
            cache_years = (i for i in cache_years if int(i.stem) in self._cache_years)

        self.rev_dt = {v: k for k, v in hpc.dwelling_type.items()}
        self.rev_tn = {v: k for k, v in hpc.tenure.items()}

        # Read the cache files
        with ThreadPoolExecutor(4) as executor:
            executor.map(self._add_cache_year, cache_years)

        print(f"Finished reading cache, memory used: {self._mem_usage}Mb")

    def yield_items(self,
                    selectors: list,
                    data=None,
                    selector_ind=0,
                    all_selectors=[]
                    ):
        """Will yield the dataframes based on the selections,
        leaving any selection empty will yield all.

        Args:
            selectors: a list/tuple of things to select from the data.
                       E.g: [2021, None, ['Detached', 'Semi-detached']]
                       Order is:
                        [years, postcode, is_new, dwelling_type, tenure]
        """
        # Finally yield the data and the column values/names
        if selector_ind >= len(selectors):
            yield (data, all_selectors)
            return

        # Initialisation
        if data is None:
            data = self
            if len(selectors) < 5:
                if isinstance(selectors, tuple):
                    selectors = list(selectors)
                elif not isinstance(selectors, list):
                    selectors = [selectors]
                selectors += [None] * (5 - len(selectors))
            selectors = selectors[:5]

        # Indivual selector init
        curr_sels = selectors[selector_ind]
        if curr_sels is None:
            curr_sels = data.keys()
        elif not isinstance(curr_sels, (list, tuple)):
            curr_sels = [curr_sels]
        else:
            curr_sels = [sel for sel in curr_sels if sel in data]

        # Selection of data
        for sel in curr_sels:
            if sel not in data:
                continue

            # Add the column names and vals we are iterating over
            new_sels = all_selectors
            if selector_ind in self._column_names:
                new_sels = all_selectors.copy()
                new_sels.append((self._column_names[selector_ind], sel))

            yield from self.yield_items(selectors, data[sel], selector_ind+1, new_sels)

