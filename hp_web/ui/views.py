from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from .forms import FilterForm

from hp_config import path as conf_path
from hp_data import controller as cnt

import os
import json

if os.environ.get('DO_ONCE') is None:

    # One time setup
    # Open some useful config files
    print('LOADING FILES')
    maps_dir = conf_path / 'maps'
    with open(maps_dir / 'street_to_pc.json', 'r') as f:
        streets_map = json.load(f)
    with open(maps_dir / 'city_to_pc.json', 'r') as f:
        city_map = json.load(f)
    with open(maps_dir / 'county_to_pc.json', 'r') as f:
        county_map = json.load(f)

    # Create the tries for the autocompletes
    def _create_trie(pc_dict):
        """Will create a trie with values that can be autocompleted in a text field"""
        root = {}
        for word in pc_dict:
            curr_dict = root

            for letter in word[:-1]:
                low_letter = letter.lower()
                curr_dict = curr_dict.setdefault(low_letter, {})
            letter = word[-1].lower()
            curr_dict[letter] = {0: None}

        return root

    street_trie = _create_trie(streets_map)
    city_trie = _create_trie(city_map)
    county_trie = _create_trie(county_map)
    os.environ['DO_ONCE'] = 'Done'


def fetch_trie(request):
    data = {}
    if request.method == "POST":
        loc = request.POST.get('_loc', '')
        tries = {'street': street_trie, 'city': city_trie,
                 'county': county_trie, '': {}}
        pre = request.POST.get('_prefix', '')
        if len(pre) > 1:
            data = tries[loc]
            for letter in pre:
                data = data.get(letter.lower(), {})
    return JsonResponse(data)


class DataScreen(View):
    _str_keys = {'city', 'street', 'postcode', 'county', }
    _checks = {'is_new': 2, 'tenure': 2, 'dwelling_type': 5}

    def _create_selectors(self, request):
        """Will create the selectors that will be sent to the controller to get back data"""
        selectors = {}
        for key in request.POST:
            if key.startswith('date_'):
                selectors[key] = datetime.strptime(request.POST[key], '%Y-%m-%d')

            elif key in self._str_keys and request.POST[key]:
                selectors[key] = str(request.POST[key])

            elif key.endswith('_checks'):
                val = request.POST.getlist(key)
                k = key[:-7]
                if len(val) < self._checks[k]:
                    selectors[k] = val

            elif key.startswith('price_'):
                low = int(request.POST['price_low'])
                high = int(request.POST['price_high'])
                if low > 0:
                    selectors['price_low'] = low
                if high < 2.5e6:
                    selectors['price_high'] = high

        return selectors

    def get(self, request):
        """No submissions etc"""
        form = FilterForm(request.POST)
        return render(request, 'ui/summary.html', {'form': form,
                                                   'form_data': {},
                                                   'street_trie': street_trie,
                                                   'city_trie': city_trie,
                                                   'county_trie': county_trie,
                                                   })

    def post(self, request):
        """After submitting form"""
        form = FilterForm(request.POST)
        form_data = {f: request.POST[f] for f in form.fields}

        if form.is_valid():
            selectors = self._create_selectors(request)
            cnt.DataController(selectors)

        return render(request, 'ui/summary.html', {'form': form,
                                                   'form_data': form_data,
                                                   'street_trie': street_trie,
                                                   'city_trie': city_trie,
                                                   'county_trie': county_trie,
                                                   })
