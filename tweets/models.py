from django.contrib.auth.models import User
from claims.models import Claim
from django.db import models
from django.utils import timezone


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
    tweet_link = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    author_rank = models.IntegerField()
    label = models.CharField(default='', max_length=10)
    up_votes = models.ManyToManyField(User, related_name='%(class)s_up_votes', blank=True)
    down_votes = models.ManyToManyField(User, related_name='%(class)s_down_votes', blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
