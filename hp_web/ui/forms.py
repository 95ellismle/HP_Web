from django import forms

from .models import Filter


def check_pc(postcode):
    """Validator for postcode"""
    if not all((i.isalnum() for i in postcode)):
        bad_char = [i for i in postcode if not i.isalnum()]
        raise forms.ValidationError(f"Postcodes are all alpha-numeric (please remove {''.join(bad_char)})")

    return postcode


def check_street(street):
    """Validator for the street field"""
    valid_char = {'2', 'c', 'x', 'j', '4', '1', '&', 'k', 'n', '5', 'f', ' ', 'b', 'l',
                  "'", 'z', '7', 'u', 'p', '-', 'e', 'h', '9', '3', ',', 'r', 'o', 'd',
                  '(', 's', '8', 'i', 'a', 'm', 'v', '0', '6', 't', 'y', 'w', ')', '.',
                  'q', 'g'}
    if not all(i.lower() in valid_char for i in street):
        raise forms.ValidationError("Unknown characters in the street field")
    return street


def check_city(city):
    """Validator for the city field"""
    valid_char = {'c', '-', 'x', 'e', 'h', 'j', 'k', 'r', 'o', 'd', 's', 'i', 'n', 'f',
                  ' ', 'm', 'a', 'v', 'b', 'l', 't', 'y', 'w', "'", 'z', '.', 'u', 'q',
                  'p', 'g'}
    if not all(i.lower() in valid_char for i in city):
        raise forms.ValidationError("Unknown characters in the city field")
    return city


def check_county(county):
    """Validator for the county field"""
    valid_char = {'c', '-', 'x', 'e', 'h', ',', 'k', 'r', 'o', 'd', 's', 'n', 'i', 'f',
                  ' ', 'm', 'a', 'v', 'b', 'l', 't', 'y', 'w', 'u', 'p', 'g'}
    if not all(i.lower() in valid_char for i in county):
        raise forms.ValidationError("Unknown characters in the county field")
    return county


class FilterForm(forms.ModelForm):

    class Meta:
        model = Filter
        fields = ('postcode', 'street', 'city',
                  'county', 'price_low', 'price_high',
                  'date_from', 'date_to', 'dwelling_type',
                  'is_new', 'tenure', 'paon')

    def __init__(self, *args, **kwargs):
        """Set all fields to not-required"""
        super().__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].required = False

        # Validate the postcode field
        pc_field = self.fields['postcode']
        pc_field.validators.append(check_pc)

        # Validate the street field
        st_field = self.fields['street']
        st_field.validators.append(check_street)

        # Validate the city field
        city_field = self.fields['city']
        city_field.validators.append(check_city)

        # Validate the county field
        county_field = self.fields['county']
        county_field.validators.append(check_county)
