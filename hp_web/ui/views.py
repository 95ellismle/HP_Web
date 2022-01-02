from datetime import datetime
from django.shortcuts import render
from django.views import View
from .forms import FilterForm

from hp_data import controller as cnt


class DataScreen(View):
    str_keys = {'city', 'street', 'postcode', 'county', }
    def _create_selectors(self, request):
        """Will create the selectors that will be sent to the controller to get back data"""
        selectors = {}
        for key in request.POST:
            if 'date' in key:
                selectors[key] = datetime.strptime(request.POST[key], '%Y-%m-%d')

        print(request.POST)

    def get(self, request):
        """No submissions etc"""
        form = FilterForm(request.POST)
        return render(request, 'ui/summary.html', {'form': form,
                                                   'form_data': {}})

    def post(self, request):
        """After submitting form"""
        form = FilterForm(request.POST)
        form_data = {f: request.POST[f] for f in form.fields}

        if form.is_valid():
            selectors = self._create_selectors(request)
            cnt.DataController(selectors)

        return render(request, 'ui/summary.html', {'form': form,
                                                   'form_data': form_data})
