"""One time setup code called when hp_data (or it's sub mods) is imported"""
import json
import logging
import os
import pandas as pd
import sys
import yaml

from data import path as dt_path
from hp_config import path as conf_path
from hp_data import utils as ut

log = logging.getLogger(__name__)


# Open some useful config files
log.debug('Loading Map Files')
maps_dir = conf_path / 'maps'
with open(maps_dir / 'street_to_pc.json', 'r') as f:
    streets_map = json.load(f)
with open(maps_dir / 'city_to_pc.json', 'r') as f:
    city_map = json.load(f)
with open(maps_dir / 'county_to_pc.json', 'r') as f:
    county_map = json.load(f)

street_trie = ut.create_trie(streets_map)
city_trie = ut.create_trie(city_map)
county_trie = ut.create_trie(county_map)

# Read the data stats
with open(conf_path / 'data_stats.yaml', 'r') as f:
    DATA_STATS = yaml.safe_load(f)
    for key in DATA_STATS:
        if key.endswith('_date'):
            DATA_STATS[key] = pd.to_datetime(DATA_STATS[key], format='%Y/%m/%d')
DATA_STATS['poss_postcodes_trie'] = ut.create_trie(DATA_STATS['poss_postcodes'])

# Load the cache

curr_year = pd.Timestamp.now() - pd.to_timedelta(15, 'w')
curr_year = curr_year.year + 1
num_prev_years = 10
skip_cache = bool(os.environ.get('DO_TEST', False))
skip_cache = True
CACHE_DATA = {}


"""
The cache needs thinking about.
It should be in its own module and initialised here.

Firstly, because it is a more flexible data structure than a column based table,
the cache can store data separately. E.g:
    new_build_data = {year1:
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

Then the sort_indices for: is_new and dwelling_type can be dropped. So too can the data columns.

This should reduce memory footprint by ~25% and increase data selection speed.
"""

print(f"Do Cache: {not skip_cache}")
if not skip_cache:
    for year in range(curr_year - num_prev_years, curr_year):
        pc_dir = dt_path / f"{year}/postcodes"
        CACHE_DATA[year] = {}
        for pc in pc_dir.glob('*.feather'):
            CACHE_DATA[year][pc.stem] = pd.read_feather(pc)

