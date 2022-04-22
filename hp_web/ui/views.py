from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

import json
import numpy as np
import os
import pandas as pd
import requests as rq
import time
import yaml

from .forms import FilterForm
from . import orm

import hp_data as hpd


def fetch_trie(request):
    """View to fetch the trie requested via AJAX and send it as json"""
    data = {}
    if request.method == "POST":
        loc = request.POST.get('_loc', '')
        tries = {'street': hpd.street_trie, 'city': hpd.city_trie,
                 'county': hpd.county_trie, '': {}}
        pre = request.POST.get('_prefix', '')
        if len(pre) > 1:
            data = tries[loc]
            for letter in pre:
                data = data.get(letter.lower(), {})
    return JsonResponse(data)


class BaseSelectorScreen(View):
    """A base screen that handles selectors that other screens can inherit from"""
    _str_keys = {'city', 'street', 'postcode', 'county', 'paon'}
    _checks = {'is_new': 2, 'tenure': 2, 'dwelling_type': 2}

    def _create_selectors(self, request):
        """Will create the selectors that will be sent to the controller to get back data

        The selectors are created from the front-end form.
        """
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

        # Now prep the dates
        min_date = hpd.DATA_STATS['min_date']
        max_date = hpd.DATA_STATS['max_date']
        if 'date_to' in selectors and selectors['date_to'] >= max_date:
            selectors.pop('date_to')
        if 'date_from' in selectors and selectors['date_from'] <= min_date:
            selectors.pop('date_from')
        if 'date_to' in selectors:
            selectors['date_to'] = selectors['date_to'].strftime('%Y-%m-%d')
        if 'date_from' in selectors:
            selectors['date_from'] = selectors['date_from'].strftime('%Y-%m-%d')

        # Prep tenure
        if 'tenure' in selectors:
            # Selecting everything -just don't filter by it
            if len(selectors['tenure']) == 2:
                selectors.pop('tenure')
            else:
                selectors['tenure'] = selectors['tenure'][0]

        return selectors


class DataScreen(BaseSelectorScreen):
    """View for the general data screen"""
    _max_data_len = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._max_data_len = int(1e5)


    def get(self, request):
        """No submissions etc"""
        form = FilterForm(request.POST)
        return render(request, 'ui/summary.html', {'form': form,
                                                   'form_data': {},
                                                   'table': {},
                                                   'err_msg': ''})

    def post(self, request):
        """After submitting form"""
        form = FilterForm(request.POST)
        form_data = {f: request.POST[f] for f in form.fields}
        ret_obj = {'form': form, 'form_data': form_data, 'err_msg': ''}

        if form.is_valid():
            selectors = self._create_selectors(request)
            t1 = time.time()
            ret_data = rq.post('http://0.0.0.0:8008', json={**selectors}).json()
            data_retreival_time = time.time() - t1

            orm.record_usage_stats(selectors, request.POST.get('IP'), data_retreival_time)

        if isinstance(ret_data, int):
            if ret_data == 1:
                ret_obj['err_msg'] = 'No data for current selection, please try a different search'
            else:
                ret_obj['err_msg'] = 'Internal Server Error'
        else:
            ret_obj['data'] = ret_data

        return render(request, 'ui/summary.html', ret_obj)
