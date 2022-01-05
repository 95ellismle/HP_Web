from django.urls import path
from . import views

urlpatterns = [
    path('', views.DataScreen.as_view(), name='summary'),
    path('street_trie/', views.fetch_trie, name="street_trie"),
    path('city_trie/', views.fetch_trie, name="city_trie"),
    path('county_trie/', views.fetch_trie, name="county_trie"),
]
