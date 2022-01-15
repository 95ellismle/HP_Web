from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
import pandas as pd

from .forms import FilterForm
from hp_data import controller as cnt
from hp_data import utils as ut
from hp_data.controller import NoDataError

import os
import json
import yaml


def fetch_trie(request):
    """View to fetch the trie requested via AJAX and send it as json"""
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
    """View for the general data screen"""
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

        # Now prep the dates
        min_date = DATA_STATS['min_date']
        max_date = DATA_STATS['max_date']
        if 'date_to' in selectors and selectors['date_to'] >= max_date:
            selectors.pop('date_to')
        if 'date_from' in selectors and selectors['date_from'] <= min_date:
            selectors.pop('date_from')

        return selectors

    def get(self, request):
        """No submissions etc"""
        form = FilterForm(request.POST)
        return render(request, 'ui/summary.html', {'form': form,
                                                   'form_data': {}})

    def post(self, request):
        """After submitting form"""
        form = FilterForm(request.POST)
        form_data = {f: request.POST[f] for f in form.fields}
        ret_obj = {'form': form, 'form_data': form_data}

        print(form.is_valid())
        print(form.errors)
        if form.is_valid():
            selectors = self._create_selectors(request)
            try:
                data = cnt.DataController(selectors)
            except NoDataError:
                ret_obj['err_msg'] = 'No data for current selection, try changing fields in the sidebar'
                return render(request, 'ui/summary.html', ret_obj)
            ret_obj['table'] = data.data.iloc[:10]

        return render(request, 'ui/summary.html', ret_obj)
