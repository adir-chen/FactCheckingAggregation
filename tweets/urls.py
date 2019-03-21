from django.urls import path
from . import views

app_name = "tweets"
urlpatterns = [
    path('post_tweets_page', views.post_tweets_page, name='post_tweets_page'),
    path('download_tweets_for_claims', views.download_tweets_for_claims, name='download_tweets_for_claims'),
    path('up_vote', views.up_vote, name='up_vote'),
    path('down_vote', views.down_vote, name='down_vote'),
    path('add_tweet', views.add_tweet, name='add_tweet'),
    path('edit_tweet', views.edit_tweet, name='edit_tweet'),
    path('delete_tweet', views.delete_tweet, name='delete_tweet'),
]
