from django.shortcuts import render
from django.views import View

from .forms import FilterForm

# Create your views here.
class DataScreen(View):
    def get(self, request):
        """No submissions etc"""
        form = FilterForm(request.POST)
        return render(request, 'ui/summary.html', {'form': form,
                                                   'form_data': {}})

    def post(self, request):
        """After submitting form"""
        form = FilterForm(request.POST)
        form_data = {f: request.POST[f] for f in form.fields}
        return render(request, 'ui/summary.html', {'form': form,
                                                   'form_data': form_data})
