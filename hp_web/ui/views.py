from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

import json
import os
import pandas as pd
import yaml

import hp_data as hpd

from .forms import FilterForm
from hp_data import controller as cnt
from hp_data import utils as ut
from hp_data.controller import NoDataError


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
        min_date = hpd.DATA_STATS['min_date']
        max_date = hpd.DATA_STATS['max_date']
        if 'date_to' in selectors and selectors['date_to'] >= max_date:
            selectors.pop('date_to')
        if 'date_from' in selectors and selectors['date_from'] <= min_date:
            selectors.pop('date_from')

        # Prep tenure
        if 'tenure' in selectors:
            # Selecting everything -just don't filter by it
            if len(selectors['tenure']) == 2:
                selectors.pop('tenure')
            else:
                selectors['tenure'] = selectors['tenure'][0]

        # Prep new build
        if 'is_new' in selectors:
            if len(selectors['is_new']) == 2:
                selectors.pop('is_new')
            else:
                selectors['is_new'] = selectors['is_new'][0] == 'is_new'

        return selectors

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
        ret_obj = {'form': form, 'form_data': form_data, 'table': {}, 'err_msg': ''}

        if form.is_valid():
            selectors = self._create_selectors(request)
            try:
                data = cnt.DataController(selectors, ['date_transfer', 'price', 'paon', 'street', 'city', 'county',
                                                      'postcode', 'dwelling_type', 'is_new', 'tenure'])
                data.read_data()
            except NoDataError:
                ret_obj['err_msg'] = 'No data for current selection, try changing fields in the sidebar'
                return render(request, 'ui/summary.html', ret_obj)
            if len(data.data) > 10000:
                ret_obj['err_msg'] = 'Only the first 10,000 results are being passed back from the server. Please narrow your search for accurate sorting'
                print(len(data.data))
            ret_obj['table'] = data.data.iloc[:10000].to_json(orient='split')

        return render(request, 'ui/summary.html', ret_obj)

