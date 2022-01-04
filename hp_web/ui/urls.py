from django.urls import path
from . import views

urlpatterns = [
    path('', views.DataScreen.as_view(), name='summary'),
    path('street_trie/', views.fetch_street_trie, name="street_trie"),
    path('city_trie/', views.fetch_city_trie, name="city_trie"),
    path('county_trie/', views.fetch_county_trie, name="county_trie"),
]
