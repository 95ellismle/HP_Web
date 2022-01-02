from hp_config import path as conf_path

import yaml

maps_dir = conf_path / 'maps'
with open(maps_dir / 'street_to_pc.yaml', 'r') as f:
    streets_map = yaml.safe_load(f)
with open(maps_dir / 'city_to_pc.yaml', 'r') as f:
    city_map = yaml.safe_load(f)
with open(maps_dir / 'county_to_pc.yaml', 'r') as f:
    county_map = yaml.safe_load(f)


class DataController:
    """The controller that decides what data is passed to the frontend"""
    def __init__(self, selectors):
        print(selectors)
