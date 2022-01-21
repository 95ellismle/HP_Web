"""Will store the datacache object. This stores the data in a very searchable way -hopefully speeding up the app"""
import sys
from pathlib import Path
from pyarrow import feather as ft

from data import path as dt_path


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

    _dwelling_types = ['Detached', 'Semi-Detached', 'Terraced', 'Flat/Maisonette', 'Other']
    _tenures = ['Freehold', 'Leasehold']
    _mem_usage = 0

    def __init__(self, *args, **kwargs):
        self._create_cache()
        super().__init__(*args, **kwargs)

    def _create_cache(self):
        """Will iterate over all files in the data directory and load them into the cache.
        This will create the data structure as seen in the docstr.
        """
        for year in sorted(dt_path.glob('????')):
            data = self.setdefault(int(year.stem), {})
            print(year)

            for pc in sorted(year.glob('postcodes/*.feather')):
                data = data.setdefault(pc.stem, {})
                Odf = ft.FeatherDataset([pc]).read_pandas(columns=self._cols_to_read)

                for is_new in (True, False):
                    data = data.setdefault(is_new, {})
                    df1 = Odf[Odf['is_new'] == is_new]

                    for dwelling_type in self._dwelling_types:
                       data = data.setdefault(dwelling_type, {})
                       df2 = df1[df1['dwelling_type'] == dwelling_type].drop('is_new', axis=1)

                       for tenure in self._tenures:
                           new_df = df2[df2['tenure'] == tenure].drop(['tenure', 'dwelling_type'],
                                                                      axis=1)
                           self._mem_usage += sys.getsizeof(new_df)
                           data[tenure] = new_df

