from django.urls import path
from . import views

app_name = "tweets"
urlpatterns = [
    path('add_tweet', views.add_tweet, name='add_tweet'),
    path('delete_tweet', views.delete_tweet, name='delete_tweet'),
    path('export_to_csv', views.export_to_csv, name='export_to_csv'),
    path('export_tweets_page', views.export_tweets_page, name='export_tweets_page'),
    path('download_tweets_for_claims', views.download_tweets_for_claims, name='download_tweets_for_claims'),
    path('check_tweets_for_claim_in_twitter', views.check_tweets_for_claim_in_twitter,
         name='check_tweets_for_claim_in_twitter'),
]
