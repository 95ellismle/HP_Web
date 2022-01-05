from data import path as data_dir
from pyarrow import parquet as pq

from hp_data.exceptions import NoDataError
from ui import views

class DataController:
    """The controller that decides what data is passed to the frontend"""
    _loc_fields = {'street', 'postcode', 'city', 'county'}
    _pc_dir = data_dir / 'postcodes'
    _cols = ('price', 'date_transfer', 'postcode', 'type', 'is_new', 'tenure',
       'paon', 'saon', 'street', 'locality', 'city', 'county')

    def __init__(self, selectors):
        self._selectors = selectors

        self._data_files_to_read = self._get_data_files()
        self.data = self._read_data_files()

    def _get_data_files(self):
        """Will find which data files to read"""
        if any(i in self._selectors for i in self._loc_fields):
            data_filenames = self._get_loc_files()
        else:
            print("BOB")

        return data_filenames

    def _read_data_files(self):
        """Will read all data files as a dataframe via 'read_dataset' from pyarrow"""
        df = pq.ParquetDataset(self._data_files_to_read
                ).read_pandas(columns=self._cols).to_pandas()
        return df

    def _get_loc_files(self):
        """Get the data from the postcode files."""
        # Get relevant postcodes
        if 'postcode' in self._selectors:
            pcs = {self._selectors['postcode'][:2]}
        else:
            pcs = set()

        # Narrow down by street, city and county
        maps = {'city': views.city_map, 'street': views.streets_map,
                'county': views.county_map}
        for loc in maps:
            if loc in self._selectors:
                map_ = maps[loc]
                if len(pcs) == 0:
                    pcs = set(map_.get(self._selectors[loc].title(), []))
                else:
                    pcs = pcs.intersection(map_.get(self._selectors[loc].title(), set()))
                    if len(pcs) == 0:
                        raise NoDataError("No data for that selection")

        # Construct the filenames
        fns = []
        for pc in pcs:
            dir_name = self._pc_dir / pc[0].upper()
            fns.append(dir_name / f'{pc[1].upper()}.parq')
            assert (dir_name / f'{pc[1].upper()}.parq').is_file()

        return fns

