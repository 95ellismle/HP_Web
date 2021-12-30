from django.db import models
from django.utils import timezone


# Create your models here.
class Filter(models.Model):
    postcode = models.CharField(max_length=7)
    street = models.CharField(max_length=70)
    city = models.CharField(max_length=70)
    county = models.CharField(max_length=40)
    is_new = models.CharField(max_length=10)
    dwelling_type = models.CharField(max_length=50)
    tenure = models.CharField(max_length=20)
    price_low = models.IntegerField()
    price_high = models.IntegerField()

    date_from = models.DateField()
    date_to = models.DateField()

    def __str__(self):
        return "<Filter: Form>"
