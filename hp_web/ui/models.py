from django.db import models
from django.utils import timezone


# Create your models here.
class Filter(models.Model):
    postcode = models.CharField(max_length=8)
    street = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    county = models.CharField(max_length=64)
    is_new = models.CharField(max_length=16)
    dwelling_type = models.CharField(max_length=64)
    tenure = models.CharField(max_length=32)
    price_low = models.IntegerField()
    price_high = models.IntegerField()

    date_from = models.DateField()
    date_to = models.DateField()

    def __str__(self):
        return "<Filter: Form>"
