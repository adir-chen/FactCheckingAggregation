from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path('get_scrapers', views.get_all_scrapers_ids, name='get_scrapers'),
    path('get_random_claims_from_scrapers', views.get_random_claims_from_scrapers, name='get_random_claims_from_scrapers'),
    path('add_scraper_guide', views.add_scraper_guide, name='add_scraper_guide'),
    path('add_new_scraper', views.add_new_scraper, name='add_new_scraper'),
    path('remove_true_label', views.remove_true_label, name='remove_true_label'),
    path('add_true_label', views.add_true_label, name='add_true_label'),
    path('add_false_label', views.add_false_label, name='add_false_label'),
    path('remove_false_label', views.remove_false_label, name='remove_false_label'),
    path('add_all_scrapers', views.add_all_scrapers, name='add_all_scrapers'),
    path('my_profile', views.my_profile_page, name='my_profile'),
    path('<username>', views.user_page, name='user_page'),
]
