from django.db import models
from django.utils import timezone


class Filter(models.Model):
    postcode = models.CharField(max_length=7)
    paon = models.CharField(max_length=128)
    street = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    county = models.CharField(max_length=64)
    #is_new = models.CharField(max_length=16)
    dwelling_type = models.CharField(max_length=64)
    tenure = models.CharField(max_length=32)
    price_low = models.IntegerField()
    price_high = models.IntegerField()

    date_from = models.DateField()
    date_to = models.DateField()

    def __str__(self):
        return "<Filter: Form>"


class UsageStats(models.Model):
    postcode = models.CharField(max_length=8, null=True)
    paon = models.CharField(max_length=128, null=True)
    street = models.CharField(max_length=128, null=True)
    city = models.CharField(max_length=128, null=True)
    county = models.CharField(max_length=64, null=True)
    #is_new = models.CharField(max_length=16, null=True)
    dwelling_type = models.CharField(max_length=64, null=True)
    tenure = models.CharField(max_length=32, null=True)
    price_low = models.IntegerField(null=True)
    price_high = models.IntegerField(null=True)

    date_from = models.DateField(null=True)
    date_to = models.DateField(null=True)

    response_time = models.FloatField()
    IP_address = models.CharField(max_length=64)
    time_of_submission = models.DateTimeField(null=False, auto_now_add=True)

    def __str__(self):
        s = ''
        for i in ('postcode', 'paon', 'street', 'city', 'county',
                  'dwelling_type', 'tenure', 'price_low', 'price_high',
                  'date_from', 'date_to', 'response_time', 'IP_address'):
            s += f'{i}  {getattr(self, i)}'
        return "<UsageStats: Form>"
