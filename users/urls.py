from django.urls import path

from . import views

app_name = "users"
urlpatterns = [
    path('get_scrapers', views.get_all_scrapers_ids, name='get_scrapers'),
    path('get_random_claims_from_scrapers', views.get_random_claims_from_scrapers, name='get_random_claims_from_scrapers'),
    path('add_scraper_guide', views.add_scraper_guide, name='add_scraper_guide'),
    path('add_new_scraper', views.add_new_scraper, name='add_new_scraper'),
    path('add_all_scrapers', views.add_all_scrapers, name='add_all_scrapers'),
]
