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
from hp_data import datacache as dc

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

do_test = os.environ.get('DO_TEST', False)
if do_test == 'True':
    cache_years = [2021]
else:
    cache_years = os.environ.get('CACHE_YEARS', None)

#cache_years = [2021]

cache = dc.DataCache(cache_years)

