from django.urls import path
from . import views

urlpatterns = [
    path('', views.DataScreen.as_view(), name='summary'),
]
