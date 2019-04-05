from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path('add_all_scrapers', views.add_all_scrapers, name='add_all_scrapers'),
    path('get_all_scrapers_ids', views.get_all_scrapers_ids, name='get_scrapers'),
    path('get_random_claims_from_scrapers', views.get_random_claims_from_scrapers, name='get_random_claims_from_scrapers'),
    path('add_scraper_guide', views.add_scraper_guide, name='add_scraper_guide'),
    path('add_new_scraper', views.add_new_scraper, name='add_new_scraper'),
    path('add_true_label_to_scraper', views.add_true_label_to_scraper, name='add_true_label_to_scraper'),
    path('delete_true_label_from_scraper', views.delete_true_label_from_scraper, name='delete_true_label_from_scraper'),
    path('add_false_label_to_scraper', views.add_false_label_to_scraper, name='add_false_label_to_scraper'),
    path('delete_false_label_from_scraper', views.delete_false_label_from_scraper, name='delete_false_label_from_scraper'),
    path('<int:user_id>', views.user_page, name='user_page'),
    path('update_user_img', views.update_user_img, name='update_user_img'),
]
