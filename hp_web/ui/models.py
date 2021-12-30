from django.db import models
from django.utils import timezone

# Create your models here.
class Post(models.Model):
    postcode = models.CharField(max_length=7)
    street = models.CharField(max_length=70)
    city = models.CharField(max_length=70)
    county = models.CharField(max_length=40)
    is_new = models.BooleanField()
    dwelling_type = models.CharField(max_length=20)
    tenure = models.CharField(max_length=10)

    datetime_from = models.DateTimeField()
    datetime_to = models.DateTimeField()

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title
