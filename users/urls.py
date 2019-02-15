from django.urls import path

from . import views

app_name = "users"
urlpatterns =[
    path('get_scrapers', views.get_all_scrapers_ids, name='get_scrapers'),
    path('get_random_claims_from_scrapers', views.get_random_claims_from_scrapers, name='get_random_claims_from_scrapers'),
]
