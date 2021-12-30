from django import forms

from .models import Filter


class FilterForm(forms.ModelForm):

    class Meta:
        model = Filter
        fields = ('postcode', 'street', 'city',
                  'county', 'price_low', 'price_high',
                  'date_from', 'date_to', 'dwelling_type',
                  'is_new', 'tenure',)

    def __init__(self, *args, **kwargs):
        """Set all fields to not-required"""
        super().__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].required = False
