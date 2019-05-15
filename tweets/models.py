import json
import tweepy
from django.contrib.auth.models import User
from django.utils import timezone
from tweepy import OAuthHandler
from FactCheckingAggregation import settings
from claims.models import Claim
from django.db import models


class Tweet(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
    tweet_link = models.CharField(max_length=200)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.claim.id) + ' - ' + self.tweet_link

    def get_tweet_data(self):
        auth = OAuthHandler(settings.twitter_consumer_key, settings.twitter_consumer_secret)
        auth.set_access_token(settings.twitter_access_token, settings.twitter_access_secret)
        api = tweepy.API(auth)
        tweet_data = {'tweet_title': '',
                      'tweet_text': '',
                      'tweet_date': ''}
        try:
            tweet = api.get_status(self.tweet_link.split('status/')[1])
            if tweet:
                tweet_data['tweet_title'] = tweet.user.name + "'s" + ' tweet'
                tweet_data['tweet_text'] = tweet.text.split('https')[0]
                tweet_data['tweet_date'] = str(tweet.created_at.date())
        except:
            pass
        return json.dumps(tweet_data)
